# CTC16-Data-Gathering

# API

## Request format
(server address) /api/v1/data?
* lat
* lon
* 

Example: 

http://127.0.0.1:5000/api/v1/data?lat=56.964&lon=-2.212&start_date=2019-05-05T10:00:00&end_date=2019-05-25T11:00:00

## Run the API locally
The API is currently a python server. You need to run this locally

* Install Python v3
* pip install the following:
    * flask
    * python-dateutil
* run server via commandline "python ./AbdnServer.py"

This will run the server locally (127.0.0.1) on port 5000.

To access the API open a web browser and naviagte to:

http://127.0.0.1:5000/api/v1/data?lat=56.964&lon=-2.212&start_date=2019-05-05T10:00:00&end_date=2019-05-25T11:00:00
