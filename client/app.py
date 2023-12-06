import logging
import os
from flask import Flask, render_template, request
from azure.storage.blob import BlobServiceClient
from flask_paginate import Pagination
import requests
from datetime import datetime

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

# Azure Function URL
azure_function_url = os.getenv("AZURE_FUNCTION_URL", "")



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


# @app.route('/search', methods=['GET', 'POST'])
# def product_search():
#     if request.method == 'POST':
#         search_query = request.form.get('search_query')
#         filters = request.form.getlist('filters')
#         sort_option = request.form.get('sort_option')

#         # Construct a payload to send to Azure Function
#         payload = {
#             'search_query': search_query,
#             'filters': filters,
#             'sort_option': sort_option
#         }

#         # Send request to Azure Function
#         response = requests.post(azure_function_url, json=payload)

#         # Parse the response
#         search_results = response.json()

#         return render_template('search.html', search_results=search_results)

#     return render_template('search.html')
def convert_to_iso(date):
    if date:
        return f"{date}T00:00:00Z"  # Assuming start of the day
    return None

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get form inputs
        search_query = request.form.get('search_query')
        start_date = convert_to_iso(request.form.get('start_date'))
        end_date = convert_to_iso(request.form.get('end_date'))
        order_by = request.form.get('order_by')
        page = int(request.args.get('page', 1))  # Get the requested page from the query parameters

        # Call the Azure Search API with pagination parameters
        search_results = search_images(search_query, start_date, end_date, order_by, page)

        # Convert SearchItemPaged to a list for easy handling in the template
        search_results_list = list(search_results)
        logging.error(f"list len is: {len(search_results_list)} page is: {page}")

        return render_template('search.html', search_results=search_results_list, page=page,
                               search_query=search_query, start_date=start_date,
                               end_date=end_date, order_by=order_by)

    elif request.method == 'GET':
        # Get pagination parameters from the URL
        page = int(request.args.get('page', 1))
        search_query = request.args.get('search_query')
        filter = request.args.get('filter')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        order_by = request.args.get('order_by')

        # Call the Azure Search API with pagination parameters
        search_results = search_images(search_query, start_date, end_date, order_by, page)

        # Convert SearchItemPaged to a list for easy handling in the template
        search_results_list = list(search_results)

        return render_template('search.html', search_results=search_results_list, page=page,
                               search_query=search_query, start_date=start_date,
                               end_date=end_date, order_by=order_by)

    return render_template('search.html')

def search_images(search_query, start_date, end_date, order_by, page):

    # Construct your search query based on the parameters
    filter = f"metadata_storage_last_modified ge {start_date} and metadata_storage_last_modified le {end_date}"
    order_by = f"metadata_storage_last_modified {order_by}"

    # Calculate skip value based on the page number and results per page
    

    res = requests.post(
        url=azure_function_url,
        json=dict(search_query=search_query, filter=filter, order_by=order_by, page=page)
    )

    if res.ok:
        data = res.json()
        return data
    
    return []

if __name__ == '__main__':
    app.run(debug=True)
