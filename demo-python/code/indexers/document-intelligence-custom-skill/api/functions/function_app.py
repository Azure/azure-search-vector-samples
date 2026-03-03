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
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

app = func.FunctionApp()

@app.function_name(name="markdownsplit")
@app.route(route="markdownsplit")
async def SplitMarkdownDocument(req: func.HttpRequest) -> func.HttpResponse:
    input = {}
    result_content = []
    try:
        req_body = req.get_json()
        # Read input values
        # Either file_data or metadata_storage_path and metadata_storage_sas_token
        if "values" in req_body:
            for value in req_body["values"]:
                record_id = value["recordId"]
                chunk_size = 512
                if "chunkSize" in value["data"]:
                    try:
                        chunk_size = int(value["data"]["chunkSize"])
                    except Exception as e:
                        result_content.append(
                            {
                                "recordId": record_id,
                                "data": {},
                                "errors": [
                                    {
                                        "message": "'chunkSize' must be an int"
                                    } 
                                ]
                            }
                        )
                        continue
                chunk_overlap = 128
                if "chunkOverlap" in value["data"]:
                    try:
                        chunk_overlap = int(value["data"]["chunkOverlap"])
                    except Exception as e:
                        result_content.append(
                            {
                                "recordId": record_id,
                                "data": {},
                                "errors": [
                                    {
                                        "message": "'chunkOverlap' must be an int"
                                    } 
                                ]
                            }
                        )
                        continue
                encoder_model_name = "text-embedding-3-large"
                if "encoderModelName" in value["data"]:
                    encoder_model_name = value["data"]["encoderModelName"]
                    if encoder_model_name not in ["text-embedding-ada-002", "text-embedding-3-large", "text-embedding-3-small"]:
                        result_content.append(
                            {
                                "recordId": record_id,
                                "data": {},
                                "errors": [
                                    {
                                        "message": f"Unknown encoder model {encoder_model_name}"
                                    } 
                                ]
                            }
                        )
                        continue
                if "content" in value["data"]:
                    input[record_id] = { "content": value["data"]["content"], "chunkSize": chunk_size, "chunkOverlap": chunk_overlap, "encoderModelName": encoder_model_name }
                else:
                    result_content.append(
                        {
                            "recordId": record_id,
                            "data": {},
                            "errors": [
                               {
                                   "message": "Expected 'content'"
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

    # Split the document into chunks based on markdown headers.
    # Max chunking goes 8 headers deep.
    headers_to_split_on = [
        ("#", "1"),
        ("##", "2"),
        ("###", "3"),
        ("####", "4"),
        ("#####", "5"),
        ("######", "6"),  
        ("#######", "7"), 
        ("########", "8")
    ]
    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, return_each_line=False, strip_headers=False)
    for record_id, data in input.items():
        encoder_model_name = data["encoderModelName"]
        character_splitter: RecursiveCharacterTextSplitter
        try:
            if encoder_model_name:
                character_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(model_name=encoder_model_name, chunk_size = data["chunkSize"], chunk_overlap = data["chunkOverlap"])
            else:
                character_splitter = RecursiveCharacterTextSplitter(chunk_size = data["chunkSize"], chunk_overlap = data["chunkOverlap"])
        except Exception as e:
            logging.exception("Failed to load text splitter")
            result_content.append({
                "recordId": record_id,
                "data": {},
                "errors": [
                    {
                        "message": f"Failed to split text: {e}"
                    }
                ]
            })
            continue
        # Split markdown content into chunks based on headers
        md_chunks = text_splitter.split_text(data["content"])
        # Further split the markdown chunks into the desired
        char_chunks = character_splitter.split_documents(md_chunks)
        # Return chunk content and headers
        chunks = [{ "content": document.page_content, "headers": [document.metadata[header] for header in sorted(document.metadata.keys())] } for document in char_chunks]
        result_content.append({ "recordId": record_id, "data": { "chunks": chunks } })

    response = { "values": result_content }
    return func.HttpResponse(body=json.dumps(response), mimetype="application/json", status_code=200)

@app.function_name(name="read")
@app.route(route="read")
async def ReadDocument(req: func.HttpRequest) -> func.HttpResponse:
    input = {}
    result_content = []
    try:
        req_body = req.get_json()
        # Read input values
        # Either file_data or metadata_storage_path and metadata_storage_sas_token
        if "values" in req_body:
            for value in req_body["values"]:
                record_id = value["recordId"]

                # Check if using markdown or text mode
                if "mode" in value["data"]:
                    mode = value["data"]["mode"]
                    if mode not in ["markdown", "text"]:
                        result_content.append(
                            {
                                "recordId": record_id,
                                "data": {},
                                "errors": [
                                    {
                                        "message": "'mode' must be either 'text' or 'markdown'"
                                    }
                                ]
                            }
                        )
                        continue
                else:
                    mode = "text"

                if "file_data" in value["data"]:
                    input[record_id] = { "type": "file", "file_data": value["data"]["file_data"], "mode": mode }
                elif "metadata_storage_path" in value["data"] and "metadata_storage_sas_token" in value["data"]:
                    input[record_id] = { "type": "sas", "sas_uri": f"{value['data']['metadata_storage_path']}{value['data']['metadata_storage_sas_token']}", "mode": mode }
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
        for record_id, data in input.items():
            if "file_data" in data:
                result_content.append(await process_file(client, record_id, data["file_data"], data["mode"])) # type: ignore
            else:
                result_content.append(await process_sas_uri(client, record_id, data["sas_uri"], data["mode"])) # type: ignore

    response = { "values": result_content }
    return func.HttpResponse(body=json.dumps(response), mimetype="application/json", status_code=200)

async def process_file(client: DocumentIntelligenceClient, record_id: str, file: Any, mode: str):
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
            "prebuilt-layout", body=file_data, content_type="application/octet-stream", output_content_format=mode, features=["ocrHighResolution"]
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

async def process_sas_uri(client: DocumentIntelligenceClient, record_id: str, sas_uri: str, mode: str):
    try:
        poller = await client.begin_analyze_document(
            "prebuilt-layout", body=AnalyzeDocumentRequest(url_source=sas_uri), output_content_format=mode, features=["ocrHighResolution"]
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
