# Readme: Azure Cognitive Search - Vector search using OpenAI with .NET

This repository contains a .NET console application that demonstrates how to generate text embeddings using Azure OpenAI, insert those embeddings into a vector store in Azure Cognitive Search, and perform a wide variety of vector search queries such as vector searches with metadata filtering and hybrid (text + vectors) search. The code uses Azure OpenAI to generate embeddings for title and content fields. You'll need access to Azure OpenAI to run this demo.

The code reads the `text-sample.json` file, which contains the input data for which embeddings need to be generated.

The output is a combination of human-readable text and embeddings that can be pushed into a search index.

![Dotnet Vector Video](https://github.com/Azure/cognitive-search-vector-pr/blob/main/demo-dotnet/data/images/dotnet-vector-video.gif?raw=true)

## Prerequisites

To run this code, you will need the following:

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access)
- A deployment of the `text-embedding-ada-002` embedding model in your Azure OpenAI service. This demo uses API version `2023-05-15`. We used the same name as the model for the deployment name, "text-embedding-ada-002".
- Azure OpenAI connection and model information:
  - Azure OpenAI API key
  - Azure OpenAI embedding model deployment name
  - Azure OpenAI API version
- .NET 5.0 SDK or later
- Azure Cognitive Search Service
You can use [Visual Studio](https://visualstudio.microsoft.com/) or [Visual Studio Code with the C# extension](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp) for this demo.

## Setup

1. Clone this repository.

2. Create a `local.settings.json` file in the same directory as the code and include the following variables:

   ```plaintext
   {
    "AZURE_SEARCH_SERVICE_ENDPOINT": "YOUR-SEARCH-SERVICE-ENDPOINT",
    "AZURE_SEARCH_INDEX_NAME": "YOUR-SEARCH-SERVICE-INDEX-NAME",
    "AZURE_SEARCH_ADMIN_KEY": "YOUR-SEARCH-SERVICE-ADMIN-KEY",
    "OPENAI_ENDPOINT": "YOUR-OPENAI-ENDPOINT",
    "OPENAI_API_KEY": "YOUR-OPENAI-API-KEY",
    "OPENAI_API_VERSION": "YOUR-OPENAI-API-VERSION",
    "OPENAI_EMBEDDING_DEPLOYED_MODEL": "YOUR-OPENAI-MODEL-DEPLOYMENT-NAME"
   }

   ```

## Run the Code

Before running the code, ensure you have the .NET SDK installed on your machine.

To run the code, navigate to the `demo-dotnet/code` folder in your terminal and execute the following commands:

```
dotnet build
dotnet run
```

## Output

The code writes the input_data with the added embeddings to the Azure Cognitive Search index. The embeddings can be uploaded to an Azure Cognitive Search index using the 2023-07-01-preview API version. Next, you can perform multiple query experiences such as pure vector search, vector search with metadata filtering, hybrid search, and hybrid search with Semantic Reranking, Answers, Captions, and Highlights powered by Microsoft Bing.
