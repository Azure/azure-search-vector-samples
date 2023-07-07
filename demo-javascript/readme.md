# Readme: Generate embeddings using OpenAI with node.js

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

2. Create a .env file in the same directory as the code and include the following variables:

   ```
   OPENAI_SERVICE_NAME=YOUR-OPENAI-SERVICE-NAME
   DEPLOYMENT_NAME=YOUR-MODEL-DEPLOYMENT-NAME
   OPENAI_API_VERSION=YOUR-OPENAI-API-VERSION
   ```

## Run the Code

To run the code, execute the following command from a command line:

For document vectorization, run the following command:
```node docs-text-openai-embeddings.js```

This will generate embeddings for the title and content fields of the input data and write the embeddings to the *docVectors.json* file in the output directory.

For query vectorization, run the following command:
```node query-text-openai-embedding.js```

## Output

The code writes the input_data with the added embeddings and "@search.action" field to the *docVectors.json* file in the output directory. The embeddings can be uploaded to an Azure Cognitive Search index using the 2023-07-01-preview API version of the [Add, Update, or Delete Documents REST API](https://learn.microsoft.com/rest/api/searchservice/preview-api/add-update-delete-documents).

You can also generate a query embedding to perform vector searches.
