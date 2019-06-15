import os, argparse, json, glob
import flask, json
from flask import request, jsonify
from datetime import datetime, tzinfo, timezone, date, timedelta
from dateutil import parser
import math
from math import sin, cos, sqrt, atan2, radians

json_file = "./data/big_dump/"

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def getAllIdsInRadius (lat, lon, search_radius):
    # first find nearest weather city from weather_data
    min_dist = search_radius/1000 # convert m to km
    lat1a = float(lat)
    lon1a = float(lon)
    lat1 = radians(lat1a)
    lon1 = radians(lon1a)
    location_ids = []
    with open(json_file + "info.json", "r") as f:
        d = json.load(f)
        for location_id_temp in d:  
            lat2 = float(d[location_id_temp]['info']['latitude'])
            lon2 = float(d[location_id_temp]['info']['longitude'])
            # see https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude/43211266#43211266 for details

            R = 6373.0 #radius of earth in km
            lat2 = radians(lat2)
            lon2 = radians(lon2)
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            dist = R * c

            if (dist < min_dist):
                location_ids.append(location_id_temp)
    
    return (location_ids)

def getIdFormLocation (lat, lon):
    # first find nearest weather city from weather_data
    min_dist = 1000000
    lat1a = float(lat)
    lon1a = float(lon)
    lat1 = radians(lat1a)
    lon1 = radians(lon1a)
    location_id = []
    with open(json_file + "info.json", "r") as f:
        d = json.load(f)
        for location_id_temp in d:  
            lat2 = float(d[location_id_temp]['info']['latitude'])
            lon2 = float(d[location_id_temp]['info']['longitude'])
            # see https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude/43211266#43211266 for details

            R = 6373.0 #radius of earth in km
            lat2 = radians(lat2)
            lon2 = radians(lon2)
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            dist = R * c

            if (dist < min_dist):
                min_dist = dist
                location_id = location_id_temp
    
    return (location_id)

@app.route("/api/v1/help")
def hello():
        return "Help! I need somebody to Help!"

@app.route('/api/v1/data', methods=['GET'])
def api_filter():
    query_parameters = request.args

    location_id = query_parameters.get('id')
    if not (location_id):
        lat = query_parameters.get('lat')
        lon = query_parameters.get('lon')
        location_id = getIdFormLocation (lat, lon)

    start_date = query_parameters.get('start_date')
    start_date = parser.parse(start_date)
    start_date = int((start_date - datetime(1970, 1, 1)).total_seconds())
    end_date = query_parameters.get('end_date')
    end_date = parser.parse(end_date)
    end_date = int((end_date - datetime(1970, 1, 1)).total_seconds())
    
    results = {location_id:{'info':{}, 'readings':{}, 'error':{}}}
    #check if sensor data exists on server
    if (os.path.isfile(json_file + location_id + '.json')):
        #open json file
        with open(json_file + location_id + '.json', "r") as f:
            d = json.load(f)
            #get info
            results[location_id]['info'].update(
				d[location_id]['info']
				)

            #get all timestamps
            all_time = []
            for t in d[location_id]["readings"]:
                all_time.append(int(t))
            #order timestamps
            all_time.sort()
            for t in all_time:
                if (t > start_date) and (t < end_date):
                    results[location_id]['readings'][str(t)] = d[location_id]['readings'][str(t)]
    else:
        results[location_id]['error'] = {'human':"We don't have a sensor by that name round here"}
    #results = "blah"

    return jsonify(results)

@app.route('/api/v2/data', methods=['GET'])
def api_filter2():
    query_parameters = request.args

    #empty results
    results = {'query':{},'errors':[],'info':[], 'data':{'headers':[],'results':[]}}
    results['query'] = {
        'location_id':query_parameters.get('location_id'),
        'lat':query_parameters.get('lat'),
        'lon':query_parameters.get('lon'),
        'radius':query_parameters.get('radius'),
        'start_time':query_parameters.get('start_time'),
        'end_time':query_parameters.get('end_time'),
        'period':query_parameters.get('period'),
        'smoothing':query_parameters.get('smoothing'),
        }

    location_id = [query_parameters.get('location_id')]
    radius = query_parameters.get('radius')
    if (radius):
        radius = int(radius)
    
    if not (location_id[0]):
        if not (radius):
            lat = query_parameters.get('lat')
            lon = query_parameters.get('lon')
            location_id = [getIdFormLocation (lat, lon)]
        else:
            #get all sensors in radius
            lat = query_parameters.get('lat')
            lon = query_parameters.get('lon')
            location_id = getAllIdsInRadius (lat, lon, radius)
    if not (location_id[0]):
        results['errors'].append({'300':"can't resolve location id"})

    start_time = query_parameters.get('start_time')
    if (start_time):
        start_time = parser.parse(start_time)
        start_time = int((start_time - datetime(1970, 1, 1)).total_seconds())
    end_time = query_parameters.get('end_time')
    if (end_time):
        end_time = parser.parse(end_time)
        end_time = int((end_time - datetime(1970, 1, 1)).total_seconds())
    period = query_parameters.get('period')
    if (period):
        if (start_time and not(end_time)):
            end_time = start_time + int(period)
        elif not(start_time) and end_time:
            start_time = end_time - int(period)
        else:
            end_time = datetime.utcnow()
            end_time = int((end_time - datetime(1970, 1, 1)).total_seconds())
            start_time = end_time - int(period)
    if not (start_time):
        results['errors'].append({'200':"time period not understood"})

    smoothing = query_parameters.get('smoothing')
    if (smoothing):
        smoothing *= 60 #convert to seconds

    #get response
    #reference headers
    refh = [
            "timestamp",
            "P1",
            "P2",
            "humidity",
            "pressure",
            "temperature"
        ]
    results['data']["headers"] = refh
    print (refh)
    for temp_id in location_id:
        refh = [
            "timestamp",
            "P1",
            "P2",
            "humidity",
            "pressure",
            "temperature"
        ]
        if (os.path.isfile(json_file + 'v2/' + temp_id + '.json')):
            #open json file
            with open(json_file + 'v2/' + temp_id + '.json', "r") as f:
                posh = refh #used for repositioining headers
                d = json.load(f)
                #get info
                results['info'].append(d['info'])
                #get headers
                tempheaders = d["data"]["headers"]
                #get headers in correct order
                for h in refh:
                    if h in tempheaders:
                        posh[refh.index(h)] = tempheaders.index(h)
                    else:
                        posh[refh.index(h)] = "blank"
                #get data                
                for r in d["data"]["results"]:
                    t = r[0]
                    r2 = []
                    if (t > start_time) and (t < end_time):
                        for p in posh:
                            if not (p == "blank"):
                                r2.append(r[p]) 
                            else:
                                r2.append(None)
                        results['data']["results"].append(r2)
                
        else:
            results['errors'].append({'100':"We don't have a sensor by that name round here"})

    return jsonify(results)
    #check if sensor data exists on server
    #querystr = "http://192.168.43.154:8086/query?"


if __name__ == '__main__':
    app.run('0.0.0.0',80)