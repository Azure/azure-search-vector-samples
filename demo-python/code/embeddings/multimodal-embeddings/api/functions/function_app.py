import azure.functions as func
import json
import logging
import os
from openai import AsyncAzureOpenAI
from azure.identity.aio import DefaultAzureCredential, get_bearer_token_provider
from azure.core.exceptions import HttpResponseError
from typing import Any
import base64
import io
from mimetypes import guess_type

app = func.FunctionApp()

@app.function_name(name="caption")
@app.route(route="caption")
async def CaptionImage(req: func.HttpRequest) -> func.HttpResponse:
    input = {}
    result_content = []
    try:
        req_body = req.get_json()
        # Read input values
        # Either file_data or metadata_storage_path and metadata_storage_sas_token
        if "values" in req_body:
            for value in req_body["values"]:
                record_id = value["recordId"]

                if "metadata_storage_path" in value["data"] and "file_data" in value["data"]:
                    input[record_id] = { "type": "file", "file_data": value["data"]["file_data"], "metadata_storage_path": value["data"]["metadata_storage_path"] }
                elif "metadata_storage_path" in value["data"] and "metadata_storage_sas_token" in value["data"]:
                    input[record_id] = { "type": "sas", "sas_uri": f"{value['data']['metadata_storage_path']}{value['data']['metadata_storage_sas_token']}" }
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

    async with DefaultAzureCredential() as credential:
        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
        async with AsyncAzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"], api_version=os.environ["AZURE_OPENAI_API_VERSION"], azure_ad_token_provider=token_provider) as client:
            for record_id, data in input.items():
                if "file_data" in data:
                    result_content.append(await caption_file(client, record_id, data["file_data"], data["metadata_storage_path"]))
                else:
                    result_content.append(await caption_uri(client, record_id, data["sas_uri"]))

    response = { "values": result_content }
    return func.HttpResponse(body=json.dumps(response), mimetype="application/json", status_code=200)

SYSTEM_PROMPT="""You are a helpful assistant who captions image files descriptively. Use 2-3 sentences to write your caption"""

async def caption_file(client: AsyncAzureOpenAI, record_id: str, file: Any, path: str):
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

    return await caption_uri(client, record_id, uri=f"data:{guess_type(path)[0]};base64,{file['data']}")

async def caption_uri(client: AsyncAzureOpenAI, record_id: str, uri: str):
    try:
        response = await client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_CHATGPT_DEPLOYMENT"],
            messages = [
                { "role": "system", "content": SYSTEM_PROMPT },
                { "role": "user", "content": [ { "type": "text", "text": "Caption this picture:" }, { "type": "image_url", "image_url": { "url": uri } } ]}
            ]
        )
        return {
            "recordId": record_id,
            "data": {
                "caption": response.choices[0].message.content
            }
        }
    except Exception as e:
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
