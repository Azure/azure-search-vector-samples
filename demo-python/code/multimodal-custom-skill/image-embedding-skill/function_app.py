# Source code for the function app. This function runs a custom vectorizer for text-to-image queries. 
# It's also a custom skill that vectorizes images from a blob indexer.
import azure.functions as func
import json
import logging
import os
import requests
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)
app = func.FunctionApp()

# Doubles as a custom skill and a custom vectorizer
@app.function_name(name="GetImageEmbedding")
@app.route(route="GetImageEmbedding")
def GetImageEmbedding(req: func.HttpRequest) -> func.HttpResponse:
    # Read input image urls
    input_image_urls = []
    input_text = []
    if req.method == "GET":
        if "text" in req.params:
            input_text.append((0, req.params["text"]))
    elif req.method == "POST":
        try:
            req_body = req.get_json()
            if "text" in req_body:
                input_text.append((0, req_body["texts"]))
            elif "values" in req_body:
                for value in req_body["values"]:
                    if "imageUrl" in value["data"]:
                        # append sas token to url
                        image_url = f'{value["data"]["imageUrl"]}{value["data"]["sasToken"]}'
                        input_image_urls.append((value["recordId"], image_url))
                    elif "text" in value["data"]:
                        input_text.append((value["recordId"], value["data"]["text"]))
        except Exception as e:
            logging.exception(e, "Could not get data from request body")

    if len(input_image_urls) == 0 and len(input_text) == 0:
        logging.info("no input found")
        return func.HttpResponse(
            "No input found",
            status_code=400
        )

    response = None
    endpoint = os.environ["COGNITIVE_SERVICES_ENDPOINT"]  
    api_key = os.environ["COGNITIVE_SERVICES_API_KEY"]  
    params = {  
        "api-version": "2023-02-01-preview",
        "modelVersion": "latest"
    }
    headers = {  
        "Content-Type": "application/json",  
        "Ocp-Apim-Subscription-Key": api_key  
    }
    output_values = []
    if len(input_image_urls) > 0:
        # Embed image urls
        url = f"{endpoint}/computervision/retrieval:vectorizeImage"  
        for record_id, image_url in input_image_urls:
            json_data = {  
                "url": image_url  
            }
            for attempt in Retrying(
                retry=retry_if_exception_type(requests.HTTPError),
                wait=wait_random_exponential(min=15, max=60),
                stop=stop_after_attempt(15),
                before_sleep=before_retry_sleep,
            ):
                with attempt:
                    response = requests.post(url, params=params, headers=headers, json=json_data)  
                    if response.status_code != 200:  
                        logging.error(f"Error: {response.status_code}, {response.text}")  
                        response.raise_for_status()
            vector = response.json()["vector"]
            output_values.append({
                "recordId": record_id,
                "data": {
                    "vector": vector
                }
            })
    else:
        # Embed text
        url = f"{endpoint}/computervision/retrieval:vectorizeText"  
        for record_id, text in input_text:
            json_data = {
                "text": text  
            }
            for attempt in Retrying(
                retry=retry_if_exception_type(requests.HTTPError),
                wait=wait_random_exponential(min=15, max=60),
                stop=stop_after_attempt(15),
                before_sleep=before_retry_sleep,
            ):
                with attempt:
                    response = requests.post(url, params=params, headers=headers, json=json_data)  
                    if response.status_code != 200:  
                        logging.error(f"Error: {response.status_code}, {response.text}")  
                        response.raise_for_status()
            vector = response.json()["vector"]
            output_values.append({
                "recordId": record_id,
                "data": {
                    "vector": vector
                }
            })

    response = { "values": output_values }
    return func.HttpResponse(body=json.dumps(response), mimetype="application/json", status_code=200)

def before_retry_sleep(retry_state):
    logging.info("Rate limited on the Vision embeddings API, sleeping before retrying...")