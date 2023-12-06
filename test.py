import requests
import base64
import time

url = "http://localhost:7071/api/hello"
url = "http://localhost:7071/api/search"

# while True:
#     time.sleep(1)
#     res = requests.get("https://picsum.photos/200")
#     b64_string = base64.b64encode(res.content).decode('utf-8')
#     requests.post(
#         url, 
#         json=dict(base64Image=b64_string))

start_date = "2023-01-01T00:00:00Z"
end_date = "2023-12-31T23:59:59Z"
filter = f"metadata_storage_last_modified ge {start_date} and metadata_storage_last_modified le {end_date}"
order_by = "metadata_storage_last_modified desc"
res = requests.post(
        url, 
        json=dict(
            search="*", 
            filter=filter, 
            order_by=order_by #desc/asc
            ))

print(res)

#               {
#     "search": "",
#     "filter": "metadata_storage_last_modified ge 2023-01-01T00:00:00Z and metadata_storage_last_modified le 2023-12-31T23:59:59Z",
#     "orderby": "metadata_storage_last_modified desc",
#     "count": true
#   }