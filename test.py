import requests
import base64
import time

url = "http://localhost:7071/api/hello"

while True:
    time.sleep(1)
    res = requests.get("https://picsum.photos/200")
    b64_string = base64.b64encode(res.content).decode('utf-8')
    requests.post(
        url, 
        json=dict(base64Image=b64_string))