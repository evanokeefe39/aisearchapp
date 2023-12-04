import azure.functions as func
from azure.storage.blob import BlobServiceClient
import base64
import uuid

app = func.FunctionApp()

@app.function_name(name="HttpExample")
@app.route(route="hello")
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        base64_image = req_body.get('base64Image')

        if base64_image:
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(base64_image)

            # Generate a unique filename
            filename = str(uuid.uuid4()) + '.png'

            # Connect to Azure Blob Storage
            connection_string = 'BlobEndpoint=https://aisearchtestsac.blob.core.windows.net/;QueueEndpoint=https://aisearchtestsac.queue.core.windows.net/;FileEndpoint=https://aisearchtestsac.file.core.windows.net/;TableEndpoint=https://aisearchtestsac.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=bfqt&srt=co&sp=rwdlacupiytfx&se=2024-12-04T11:16:44Z&st=2023-12-04T03:16:44Z&spr=https&sig=KzX3JN9LDYHGY%2B%2BeDFkWS0PrdVy06dbGOFZq9NbyzSA%3D'
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_name = 'images'
            container_client = blob_service_client.get_container_client(container_name)

            # Upload image to Blob Storage
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(image_bytes)

            return func.HttpResponse(f"Image '{filename}' uploaded successfully.", status_code=200)
        else:
            return func.HttpResponse("Invalid request. 'base64Image' is required in the request body.", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)