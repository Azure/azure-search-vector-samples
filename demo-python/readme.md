# Readme: Generate embeddings using OpenAI with Python

The notebooks in this repository contain Python code used to create vectorized data that can be indexed in a search index. There are two notebooks:

+ **text-openai-embedding.ipynb** generates embeddings using the text-embedding-ada-002 model on Azure OpenAI
+ **demo-python\code\text-semantic-kernel-embedding.ipynb** generates embeddings *and* creates and loads an index on Azure Cognitive Search

## Prerequisites

To run this code, you will need the following:

+ An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access)

+ A deployment of the text-embedding-ada-002 embedding model in your Azure OpenAI service. We use API version 2022-12-01 in this demo. For the deployment name, we used the same name as the model, "text-embedding-ada-002".

+ Azure OpenAI connection and model information

  + OpenAI API key
  + OpenAI embedding model deployment name
  + OpenAI API version

+ Python (these instructions were tested with version 3.9.x)

You can use [Visual Studio Code with the Python extension](https://code.visualstudio.com/docs/python/python-tutorial) for this demo. 

You don't need Azure Cognitive Search for the first notebook, but for the end-to-end sample, provide the endpoint to your search service (any billable tier) and an API key.

## Set up

1. Clone this repository.

2. Create a .env file in the same directory as the code and include the following variables:

   ```
   OPENAI_SERVICE_NAME=YOUR-OPENAI-SERVICE-NAME
   DEPLOYMENT_NAME=YOUR-MODEL-DEPLOYMENT-NAME
   OPENAI_API_VERSION=YOUR-OPENAI-API-VERSION
   ```

## Run the Code

1. Use Visual Studio Code or another Python IDE to open a notebook in the code folder. 

1. Execute the code in each cell. If you're using the end-to-end sample, provide the search URL and API key as variables inside the notebook.

## Check output

The code writes the input_data with the added embeddings and "@search.action" field to the *docVectors.json* file in the output directory. The embeddings can be uploaded to an Azure Cognitive Search index using the 2023-07-01-preview API version of the [Add, Update, or Delete Documents REST API](../docs/rest-api-reference/upload-documents.md). 

+ text-openai-embedding.ipynb outputs "docVectors.json" and "queryVector.json". If you're using the Postman collection quickstart, you can paste the JSON into the body of the Upload documents request and also into the query requests.

+ text-semantic-kernel-embedding.ipynb will create and load a search index containing vector fields on your Azure Cognitive Search service. Search Explorer isn't helpful for vector queries, but if your goal is a published search index, then this notebook can help. Other output includes "sk_docVectors.json" and "sk_queryVector.json" files.

