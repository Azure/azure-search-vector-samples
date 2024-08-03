import azure.functions as func
import json
import logging
import os
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.identity.aio import DefaultAzureCredential
import base64
import io
from azure.core.exceptions import HttpResponseError
from typing import Any

app = func.FunctionApp()

@app.function_name(name="read")
@app.route(route="read")
async def ReadDocument(req: func.HttpRequest) -> func.HttpResponse:
    input_files = {}
    input_sas = {}
    result_content = []
    try:
        req_body = req.get_json()
        # Read input values
        # Either file_data or metadata_storage_path and metadata_storage_sas_token
        if "values" in req_body:
            for value in req_body["values"]:
                record_id = value["recordId"]
                if "file_data" in value["data"]:
                    input_files[record_id] = value["data"]["file_data"]
                elif "metadata_storage_path" in value["data"] and "metadata_storage_sas_token" in value["data"]:
                    input_sas[record_id] = f"{value['data']['metadata_storage_path']}{value['data']['metadata_storage_sas_token']}"
                else:
                    result_content.append(
                        {
                            "recordId": record_id,
                            "data": {},
                            "errors": [
                               {
                                   "message": "Expected either 'file_data' or 'metadata_storage_path' and 'metadata_storage_sas_token'"
                               } 
                            ]
                        }
                    )
    except Exception as e:
        logging.exception("Could not get input data request body")
        return func.HttpResponse(
            "Invalid input",
            status_code=400
        )

    async with DocumentIntelligenceClient(endpoint=os.environ["AZURE_DOCUMENTINTELLIGENCE_ENDPOINT"], credential=DefaultAzureCredential()) as client:
        for record_id, file in input_files.items():
            result_content.append(await process_file(client, record_id, file)) # type: ignore
        for record_id, sas_uri in input_sas.items():
            result_content.append(await process_sas_uri(client, record_id, sas_uri)) # type: ignore

    response = { "values": result_content }
    return func.HttpResponse(body=json.dumps(response), mimetype="application/json", status_code=200)

async def process_file(client: DocumentIntelligenceClient, record_id: str, file: Any):
    if not isinstance(file, dict) or \
        file["$type"] != "file" or \
        "data" not in file:
        return {
            "recordId": record_id,
            "data": {},
            "errors": [
                {
                    "message": "file_data is not in correct format"
                }
            ]
        }

    try:
        file_bytes = base64.b64decode(file["data"])
        file_data = io.BytesIO(file_bytes)
    except:
        return {
            "recordId": record_id,
            "data": {},
            "errors": [
                {
                    "message": "Failed to decode file content"
                }
            ]
        }

    try:
        poller = await client.begin_analyze_document(
            "prebuilt-layout", analyze_request=file_data, content_type="application/octet-stream"
        )
        result = await poller.result()
        return {
            "recordId": record_id, "data": { "content": result.content }
        }
    except HttpResponseError as e:
        logging.exception("Failed to read document")
        return {
            "recordId": record_id,
            "data": {},
            "errors": [
                {
                    "message": f"Failed to process file content: {e.message}"
                }
            ]
        }

async def process_sas_uri(client: DocumentIntelligenceClient, record_id: str, sas_uri: str):
    try:
        poller = await client.begin_analyze_document(
            "prebuilt-layout", analyze_request=AnalyzeDocumentRequest(url_source=sas_uri)
        )
        result = await poller.result()
        return {
            "recordId": record_id, "data": { "content": result.content }
        }
    except HttpResponseError as e:
        logging.exception("Failed to read document")
        return {
            "recordId": record_id,
            "data": {},
            "errors": [
                {
                    "message": f"Failed to process file content: {e.message}"
                }
            ]
        }
