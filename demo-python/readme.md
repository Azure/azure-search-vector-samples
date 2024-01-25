---
page_type: sample
languages:
  - python
name: Vector search in Python
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using azure-search-documents and the Azure SDK for Python, index and query vectors in a RAG pattern or a traditional search solution.
urlFragment: vector-search-python
---

# Vector search in Python (Azure AI Search)

This repository contains multiple notebooks that demonstrate how to use Azure AI Search for vector and non-vector content in RAG patterns and in traditional search solutions.

Start with **azure-search-vector-python-sample.ipynb** for the basic steps. The code reads the `text-sample.json` file, which contains the input data for which embeddings need to be generated. Output is a combination of human-readable text and embeddings that's pushed into a search index.

![Python Vector Video](https://github.com/Azure/cognitive-search-vector-pr/blob/main/demo-python/data/images/python-vector-video.gif?raw=true)

Once you understand the basics, continue with the following notebooks for more exploration:

| Sample | Description |
|--------|-------------|
| [azure-search-backup-and-restore.ipynb](./code/azure-search-backup-and-restore.ipynb) | Backup retrievable index fields and restore it on a different search service. |
| [azure-search-custom-vectorization-sample.ipynb](./code/custom-embeddings/azure-search-custom-vectorization-sample.ipynb) | Integrated data chunking and vectorization using custom skills and open source models. |
| [azure-search-integrated-vectorization-sample.ipynb](./code/azure-search-integrated-vectorization-sample.ipynb) | Integrated data chunking and vectorization (preview) using Azure OpenAI. |
| [azure-search-vector-image-index-creation-python-sample.ipynb](./code/azure-search-vector-image-index-creation-python-sample.ipynb) | Vectorization using Azure AI Vision image embedding. |
| [azure-search-vector-image-python-sample.ipynb](./code/azure-search-vector-image-python-sample.ipynb)  | Vectorize images using Azure AI Vision image retrieval. |
| [azure-search-vector-python-huggingface-model-sample.ipynb](./code/azure-search-vector-python-huggingface-model-sample.ipynb)  | Vectorize using Hugging Face E5-small-V2 embedding model. |
| [azure-search-vector-python-langchain-sample.ipynb](./code/azure-search-vector-python-langchain-sample.ipynb) | LangChain integration. |
| [azure-search-vector-python-llamaindex-sample.ipynb](./code/azure-search-vector-python-llamaindex-sample.ipynb) | LlamaIndex integration. |
| [azure-search-vector-python-sample.ipynb](./code/azure-search-vector-python-sample.ipynb) | Basic vector indexing and queries. **Start here**. |

## Prerequisites

To run the Python samples in this folder, you will need the following:

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access)
- A deployment of the `text-embedding-ada-002` embedding model in your Azure OpenAI service. This demo uses API version `2023-10-01-preview`. We used the same name as the model for the deployment name, "text-embedding-ada-002".
- Azure OpenAI connection and model information:
  - OpenAI API key
  - OpenAI embedding model deployment name
  - OpenAI API version
- Python (these instructions were tested with version 3.11.x)

You can use [Visual Studio Code with the Python extension](https://code.visualstudio.com/docs/python/python-tutorial) for these demos.

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

## Run the code

Before running the code, ensure you have the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) installed in Visual Studio Code.

To run the code, navigate to the `code` folder and open the `ipynb` file in Visual Studio Code and execute the cells by clicking the **Run** button or pressing Shift+Enter.

## Troubleshoot errors

If you get error 429 from Azure OpenAI, it means the resource is over capacity:

- Check the Activity Log of the Azure OpenAI service to see what else might be running.

- Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.

- Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).
