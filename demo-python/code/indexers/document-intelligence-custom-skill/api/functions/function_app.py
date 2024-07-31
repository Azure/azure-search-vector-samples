import azure.functions as func
import json
import logging
import os
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
import base64
import io
from azure.core.exceptions import HttpResponseError

app = func.FunctionApp()

@app.function_name(name="read")
@app.route(route="read")
async def ReadDocument(req: func.HttpRequest) -> func.HttpResponse:
    # Read input file
    input_files = {}
    try:
        req_body = req.get_json()
        if "values" in req_body:
            for value in req_body["values"]:
                input_files[value["recordId"]] = value["data"]["file_data"]
    except Exception as e:
        logging.exception("Could not get input data request body")
        return func.HttpResponse(
            "Invalid input",
            status_code=400
        )

    async with DocumentIntelligenceClient(endpoint=os.environ["AZURE_DOCUMENTINTELLIGENCE_ENDPOINT"], credential=DefaultAzureCredential()) as client:
        result_content = []
        for record_id, file in input_files.items():
            result_content.append(await process_file(client, record_id, file))

    response = { "values": result_content }
    return func.HttpResponse(body=json.dumps(response), mimetype="application/json", status_code=200)

async def process_file(client: DocumentIntelligenceClient, record_id: any, file: any):
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
        return {
            "recordId": record_id,
            "data": {},
            "errors": [
                {
                    "message": f"Failed to process file content: {e.message}"
                }
            ]
        }
