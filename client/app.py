import os
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient
from flask_paginate import Pagination

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Use environment variables or set defaults
connection_string = os.getenv('BLOB_STORAGE_CONNECTION_STRING', 'YOUR_DEFAULT_CONNECTION_STRING')
container_name = os.getenv('BLOB_CONTAINER_NAME', 'YOUR_DEFAULT_CONTAINER_NAME')

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def list_blobs():
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    return [blob.name for blob in blob_list]

@app.route('/')
def index():
    blobs = list_blobs()

    # Get the page number from the query string or default to 1
    page = int(request.args.get('page', 1))
    per_page = 10  # Number of blobs per page

    offset = (page - 1) * per_page
    paginated_blobs = blobs[offset : offset + per_page]

    pagination = Pagination(page=page, total=len(blobs), per_page=per_page, record_name='blobs')

    return render_template('index.html', blobs=paginated_blobs, pagination=pagination)

if __name__ == '__main__':
    app.run(debug=True)
