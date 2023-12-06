import os
import json
import azure.functions as func
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

import logging

load_dotenv()


# Instantiate a client
class CreateClient(object):
    def __init__(self):

        # Azure Cognitive Search Configuration
        search_service_endpoint = os.getenv("SEARCH_SERVICE_ENDPOINT", "")
        index_name = os.getenv("SEARCH_INDEX_NAME", "")
        api_key = os.getenv("SEARCH_API_KEY", "")
        
        self.endpoint = search_service_endpoint
        self.index_name = index_name
        self.key = api_key
        self.credentials = AzureKeyCredential(api_key)

    # Create a SearchClient
    # Use this to upload docs to the Index
    def create_search_client(self):
        return SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credentials,
        )

    # Create a SearchIndexClient
    # This is used to create, manage, and delete an index
    def create_admin_client(self):
        return SearchIndexClient(endpoint=self.endpoint, credential=self.credentials)


app = func.FunctionApp()

start_client = CreateClient()
admin_client = start_client.create_admin_client()
search_client = start_client.create_search_client()


@app.function_name(name="HttpExample2")
@app.route(route="search")
def main(req: func.HttpRequest) -> func.HttpResponse:

    RESULTS_PER_PAGE = 10

    # try:

    req_body = req.get_json()

    search_query = req_body.get('search', '')
    filter = req_body.get('filter', '')
    order_by = req_body.get('order_by', '')
    page = req_body.get('page', 1)
    
    skip = (page - 1) * RESULTS_PER_PAGE
   
    # Execute the search
    results = search_client.search(
        search_text=search_query
        , filter=filter
        , order_by=order_by
        , top=RESULTS_PER_PAGE
        , skip=skip
    )

    _ = list(results)

    logging.info(f"search res count: {_}")
    # Extract relevant information from the results
    #search_results = [{"name": hit["document"]["name"], "description": hit["document"]["description"]} for hit in results]
    
    return func.HttpResponse(
        json.dumps(_),
        mimetype="application/json",
        status_code=200
    )

    # except Exception as e:
    #     # handle e
    #     return func.HttpResponse(
    #         json.dumps("error"),
    #         mimetype="application/json",
    #         status_code=500
    #     )

