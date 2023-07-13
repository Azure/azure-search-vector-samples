# Readme: Generate embeddings using OpenAI with Node.js

The JavaScript demo in this repository is used to create vectorized data that can be indexed in a search index. There are no calls to Cognitive Search, but it does call Azure OpenAI. You'll need access to Azure OpenAI in your Azure subscription to run this demo.

## Prerequisites

To run this code, you will need the following:

+ An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access)

+ A deployment of the text-embedding-ada-002 embedding model in your Azure OpenAI service. We use API version 2022-12-01 in this demo. For the deployment name, we used the same name as the model, "text-embedding-ada-002".

+ Azure OpenAI connection and model information:

  + OpenAI API key
  + OpenAI embedding model deployment name
  + OpenAI API version

+ Node.js (these instructions were tested with version Node.js version 16.0)

You can use [Visual Studio Code with the JavaScript extension](https://code.visualstudio.com/docs/nodejs/extensions) for this demo. For help setting up the environment, see this [JavaScript quickstart](https://learn.microsoft.com/azure/search/search-get-started-javascript).

You don't need Azure Cognitive Search for this step.

## Setup

1. Clone this repository.

1. Create a .env file in the *demo-javascript* directory and include the following variables:

   ```
   AZURE_OPENAI_SERVICE_NAME=YOUR-AZURE-OPENAI-SERVICE-NAME
   AZURE_OPENAI_DEPLOYMENT_NAME=YOUR-AZURE-OPENAI-DEPLOYMENT-NAME
   AZURE_OPENAI_API_VERSION=YOUR-AZURE-OPENAI-API-VERSION
   AZURE_OPENAI_API_KEY=YOUR-AZURE-OPENAI-API-KEY
   ```

1. Install npm dependencies:
   ```
   cd demo-javascript/code
   npm install
   ```

## Run the code

### Document vectorization
```node docs-text-openai-embeddings.js```

This will generate embeddings for the title and content fields of the input data (*data/text-sample.json*), and add the embeddings and "@search.action" field to *output/docVectors.json*. The embeddings can be uploaded to an Azure Cognitive Search index using the 2023-07-01-preview API version of the [Add, Update, or Delete Documents REST API](https://learn.microsoft.com/rest/api/searchservice/preview-api/add-update-delete-documents)

### Query vectorization
```node query-text-openai-embedding.js```

This will generate a query embedding, to perform vector searches. 

Modify the *userQuery* variable in query-text-openai-embedding.js to customize the query.
