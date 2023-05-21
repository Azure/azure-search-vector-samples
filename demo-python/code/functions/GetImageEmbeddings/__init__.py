import os  
import json  
import logging  
import requests  
  
import azure.functions as func  
  
def main(req: func.HttpRequest) -> func.HttpResponse:  
    logging.info('Python HTTP trigger function processed a request.')  
  
    # Extract values from request payload  
    req_body = req.get_body().decode('utf-8')  
    logging.info(f"Request body: {req_body}")  
    request = json.loads(req_body)  
    values = request['values']  
  
    # Process values and generate the response payload  
    response_values = []  
    for value in values:  
        imageUrl = value['data']['imageUrl']  
        recordId = value['recordId']  
        logging.info(f"Input imageUrl: {imageUrl}")  
        logging.info(f"Input recordId: {recordId}")  
  
        # Get image embeddings  
        vector = get_image_embeddings(imageUrl)  
  
        # Add the processed value to the response payload  
        response_values.append({  
            "recordId": recordId,  
            "data": {  
                "vector": vector  
            },  
            "errors": None,  
            "warnings": None  
        })  
  
    # Create the response object  
    response_body = {  
        "values": response_values  
    }  
    logging.info(f"Response body: {response_body}")  
  
    # Return the response  
    return func.HttpResponse(json.dumps(response_body), mimetype="application/json")  


  
def get_image_embeddings(imageUrl):  
    cogSvcsEndpoint = os.environ["COGNITIVE_SERVICES_ENDPOINT"]  
    cogSvcsApiKey = os.environ["COGNITIVE_SERVICES_API_KEY"]  
  
    url = f"{cogSvcsEndpoint}/computervision/retrieval:vectorizeImage"  
  
    params = {  
        "api-version": "2023-02-01-preview"  
    }  
  
    headers = {  
        "Content-Type": "application/json",  
        "Ocp-Apim-Subscription-Key": cogSvcsApiKey  
    }  
  
    data = {  
        "url": imageUrl  
    }  
  
    response = requests.post(url, params=params, headers=headers, json=data)  
  
    if response.status_code != 200:  
        logging.error(f"Error: {response.status_code}, {response.text}")  
        response.raise_for_status()  
  
    embeddings = response.json()["vector"]  
    return embeddings  
