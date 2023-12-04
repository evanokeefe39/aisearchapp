import os
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient
from flask_paginate import Pagination
import requests

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Use environment variables or set defaults
connection_string = os.getenv('BLOB_STORAGE_CONNECTION_STRING', 'YOUR_DEFAULT_CONNECTION_STRING')
container_name = os.getenv('BLOB_CONTAINER_NAME', 'YOUR_DEFAULT_CONTAINER_NAME')
sas_token = os.getenv('BLOB_SAS_TOKEN', '')

search_service_endpoint = os.getenv('SEARCH_SERVICE_ENDPOINT', 'YOUR_SEARCH_SERVICE_ENDPOINT')
search_api_key = os.getenv('SEARCH_API_KEY', 'YOUR_SEARCH_API_KEY')
index_name = os.getenv('SEARCH_INDEX_NAME', 'YOUR_SEARCH_INDEX_NAME')


blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def list_blobs():
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    return [blob.name for blob in blob_list]

def add_sas_token(blob_name):
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    return blob_url + '?'+ sas_token

def search_index(query):
    search_url = f"{search_service_endpoint}/indexes/{index_name}/docs/search"
    headers = {
        'Content-Type': 'application/json',
        'api-key': search_api_key,
    }
    payload = {
        'search': query,
        'count': 10,  # Adjust as needed
    }
    response = requests.post(search_url, json=payload, headers=headers)
    return response.json()

@app.route('/')
def index():
    blobs = list_blobs()

    # Get the page number from the query string or default to 1
    page = int(request.args.get('page', 1))
    per_page = 10  # Number of blobs per page

    offset = (page - 1) * per_page
    paginated_blobs = blobs[offset : offset + per_page]

    paginated_blob_page = Pagination(page=page, total=len(blobs), per_page=per_page, record_name='blobs')

    # Add SAS token to each image URL
    paginated_blobs_with_sas = [dict(uri=add_sas_token(blob), blob=blob) for blob in paginated_blobs]

    return render_template('index.html', blobs=paginated_blobs_with_sas, pagination=paginated_blob_page)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = search_index(query)

    # Your logic to process and display search results
    # For example, assuming your results contain a 'name' field:
    search_results = [result['name'] for result in results.get('value', [])]

    return render_template('search.html', query=query, results=search_results)


if __name__ == '__main__':
    app.run(debug=True)
