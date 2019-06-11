import time
import requests
url = "http://35.232.37.2/api/v1/help?"
while True:
    time.sleep(600)
    myResponse = requests.get(url)
    print(time.asctime( time.localtime(time.time()) ), myResponse.content)
