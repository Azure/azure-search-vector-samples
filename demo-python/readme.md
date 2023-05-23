# Readme: Generate embeddings using OpenAI with Python

This repository contains a Python notebook that demonstrates how to generate text embeddings using Azure OpenAI, insert those embeddings into a vector store in Azure Cognitive Search, and perform a wide variety of vector search queries such as vector searches with metadata filtering and hybrid (text + vectors)search. The code uses Azure OpenAI to generate embeddings for title and content fields. You'll need access to Azure OpenAI to run this demo.

This repository also contains a Python notebook that demonstrates how to use the indexer and custom skills to generate embeddings for Azure Cognitive Services Florence Vision API for Image embeddings and perform vector searches form text to image as well as image to image. You'll need access to Azure Cognitive Services to run this demo.

The code reads the `text-sample.json` file, which contains the input data for which embeddings need to be generated.

The output is a combination of human-readable text and embeddings that can be pushed into a search index.

![Python Vector Video](https://github.com/Azure/cognitive-search-vector-pr/blob/main/demo-python/data/images/python-vector-video.gif?raw=true)

## Prerequisites

To run this code, you will need the following:

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access)
- A deployment of the `text-embedding-ada-002` embedding model in your Azure OpenAI service. This demo uses API version `2022-12-01`. We used the same name as the model for the deployment name, "text-embedding-ada-002".
- Azure OpenAI connection and model information:
  - OpenAI API key
  - OpenAI embedding model deployment name
  - OpenAI API version
- Python (these instructions were tested with version 3.9.x)
- Connect to [Azure SDK Python Dev Feed](https://dev.azure.com/azure-sdk/public/_artifacts/feed/azure-sdk-for-python/connect/pip) to use the alpha version of the azure-search-documents pip package.
  - [Download Python](https://www.python.org/downloads/)
  - Update Pip: `python -m pip install --upgrade pip`
  - Install the keyring `pip install keyring artifacts-keyring`
  - If you're using Linux, ensure you've installed the [prerequisites](https://pypi.org/project/artifacts-keyring/), which are required for artifacts-keyring.
  - Add a `pip.ini` (Windows) or `pip.conf` (Mac/Linux) file to your virtualenv or where Python is located on your machine:
  ```plaintext
  [global]
  index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/
  ```
  - For example, on my machine, I placed mine in the following directory: `C:\Users\fsunavala\AppData\Local\Programs\Python\Python39\pip.ini`
  - **Note**: Be sure you don't save it as a `.txt` file
- Installation steps if using Poetry:
  - Install Poetry by following the instructions at https://python-poetry.org/docs/.
    Navigate to your project folder containing the `pyproject.toml` file.
  - Run the following command to configure Poetry to use the Azure SDK Python dev feed:
  ```
  poetry config repositories.azure-sdk-for-python https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/
  ```
  - To install the azure-search-documents package from the dev feed, run the following command:
  ```
  poetry add azure-search-documents==11.5.0-alpha.20230522.2
  ```

You can use [Visual Studio Code with the Python extension](https://code.visualstudio.com/docs/python/python-tutorial) for this demo.

## Setup

1. Clone this repository.

2. Create a `.env` file in the same directory as the code and include the following variables:

   ```plaintext
   AZURE_SEARCH_SERVICE_ENDPOINT=YOUR-SEARCH-SERVICE-ENDPOINT
   AZURE_SEARCH_INDEX_NAME=YOUR-SEARCH-SERVICE-INDEX-NAME
   AZURE_SEARCH_API_KEY=YOUR-SEARCH-SERVICE-ADMIN-KEY
   OPENAI_ENDPOINT=YOUR-OPENAI-ENDPOINT
   OPENAI_API_KEY=YOUR-OPENAI-API-KEY
   OPENAI_API_VERSION=YOUR-OPENAI-API-VERSION
   ```

## Run the Code

Before running the code, ensure you have the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) installed in Visual Studio Code.

To run the code, navigate to the `code` folder and open the `azure-search-vector-python-sample.ipynb` file in Visual Studio Code and execute the cells by clicking the "Run" button or pressing Shift+Enter.

## Output

The code writes the `input_data` with the added embeddings and `"@search.action"` field to the _docVectors.json_ file in the `output` directory. The embeddings can be uploaded to an Azure Cognitive Search index using the 2023-07-01-preview API version of the [Add, Update, or Delete Documents REST API](../docs/rest-api-reference/upload-documents.md). Next, you can perform multiple query experiences such as pure vector search, vector search with metadata filtering, hybrid search, and Hybrid Search with Semantic Reranking, Answers, Captions, and Highlights powered by Microsoft Bing.
