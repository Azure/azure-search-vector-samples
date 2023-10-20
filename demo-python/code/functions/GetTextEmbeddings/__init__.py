import logging
from sentence_transformers import SentenceTransformer
import azure.functions as func
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Read input text
    input_text = []
    if req.method == "GET":
        if "text" in req.params:
            input_text.append(req.params["text"])
    else:
        try:
            req_body = req.get_json()
            if "text" in req_body:
                input_text.append(req_body["text"])
            elif "values" in req_body:
                for value in req_body["values"]:
                    input_text.append(value["data"]["text"])
        except Exception as e:
            logging.exception(e, "Could not get text from request body")

    if len(input_text) == 0:
        return func.HttpResponse(
            "No input text found",
            status_code=400
        )
    
    # Embed text
    # https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    model = SentenceTransformer(os.path.join(os.getcwd(), 'all-MiniLM-L6-v2'))
    embeddings = model.encode(input_text)
    response = { "values": [ { "recordId": i, "data": { "vector": embedding.tolist() } } for i, embedding in enumerate(embeddings)]}

    return func.HttpResponse(body=json.dumps(response), mimetype="application/json", status_code=200)
