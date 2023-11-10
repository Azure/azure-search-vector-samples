# Readme: Generate embeddings using OpenAI with Python

This repository contains a Python notebook that demonstrates how to generate text embeddings using Azure OpenAI, insert those embeddings into a vector store in Azure Cognitive Search, and perform a wide variety of vector search queries, such as vector searches with metadata filtering and hybrid (text + vectors) search. The code uses Azure OpenAI to generate embeddings for title and content fields. You'll need access to Azure OpenAI to run this demo.

This repository also contains a Python notebook that demonstrates how to use the indexer and custom skills to generate embeddings for Azure Cognitive Services Florence Vision API for Image embeddings and perform vector searches form text to image as well as image to image. You'll need access to Azure Cognitive Services to run this demo.

The code reads the `text-sample.json` file, which contains the input data for which embeddings need to be generated.

The output is a combination of human-readable text and embeddings that can be pushed into a search index.

![Python Vector Video](https://github.com/Azure/cognitive-search-vector-pr/blob/main/demo-python/data/images/python-vector-video.gif?raw=true)

## Prerequisites

To run this code, you will need the following:

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access)
- A deployment of the `text-embedding-ada-002` embedding model in your Azure OpenAI service. This demo uses API version `2023-10-01-preview`. We used the same name as the model for the deployment name, "text-embedding-ada-002".
- Azure OpenAI connection and model information:
  - OpenAI API key
  - OpenAI embedding model deployment name
  - OpenAI API version
- Python (these instructions were tested with version 3.11.x)

You can use [Visual Studio Code with the Python extension](https://code.visualstudio.com/docs/python/python-tutorial) for this demo.

## Setup

1. Clone this repository.

1. Create a `.env` file in the same directory as the code and include the following variables:

   ```plaintext
   AZURE_SEARCH_SERVICE_ENDPOINT=YOUR-SEARCH-SERVICE-ENDPOINT
   AZURE_SEARCH_INDEX_NAME=YOUR-SEARCH-SERVICE-INDEX-NAME
   AZURE_SEARCH_ADMIN_KEY=YOUR-SEARCH-SERVICE-ADMIN-KEY
   AZURE_OPENAI_ENDPOINT=YOUR-OPENAI-ENDPOINT
   AZURE_OPENAI_API_KEY=YOUR-OPENAI-API-KEY
   AZURE_OPENAI_API_VERSION=YOUR-OPENAI-API-VERSION
   AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL=YOUR-OPENAI-EMBEDDING-DEPLOYED-MODEL
   AZURE_AI_VISION_API_KEY=YOUR-AZURE_AI_SERVICES-API-KEY
   AZURE_AI_VISION_ENDPOINT=YOUR-COGNITIVE-SERVICES-ENDPOINT
   AZURE_AI_VISION_MODEL_VERSION=YOUR-AZURE_AI_SERVICES-MODEL-VERSION
   AZURE_AI_VISION_REGION=YOUR-AZURE_AI_SERVICES-REGION
   BLOB_CONNECTION_STRING=YOUR-BLOB-CONNECTION-STRING
   BLOB_CONTAINER_NAME=YOUR-BLOB-CONTAINER-NAME
   ```

## Run the Code

Before running the code, ensure you have the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) installed in Visual Studio Code.

To run the code, navigate to the `code` folder and open the `azure-search-vector-python-sample.ipynb` file in Visual Studio Code and execute the cells by clicking the "Run" button or pressing Shift+Enter.

## Output

The code writes the `input_data` with the added embeddings to the _docVectors.json_ file in the `output` directory. The embeddings can be uploaded to an Azure Cognitive Search index using the 2023-10-01-preview API version of the [Add, Update, or Delete Documents REST API](https://learn.microsoft.com/rest/api/searchservice/preview-api/add-update-delete-documents). Next, you can perform multiple query experiences such as pure vector search, vector search with metadata filtering, hybrid search, and Hybrid Search with Semantic Reranking, Answers, Captions, and Highlights powered by Microsoft Bing.

## Troubleshoot errors

If you get error 429 from Azure OpenAI, it means the resource is over capacity:

- Check the Activity Log of the Azure OpenAI service to see what else might be running.

- Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.

- Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).
