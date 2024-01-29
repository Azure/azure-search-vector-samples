---
page_type: sample
languages:
  - csharp
name: Embed data chunking and vectorization in C#
description: |
  Using Azure.Search.Documents, add data chunking and vectorization to indexing and query workloads.
products:
  - azure
  - azure-cognitive-search
urlFragment: csharp-integrated-vectorization
---

# Embed data chunking and vectorization in C# (Azure AI Search)

In this .NET console application for Azure AI Search, **DotNetIntegratedVectorizationDemo** uses an indexer, skillset, and a data source connection to Azure Storage to chunk, vectorize, and index content in a blob container. This project uses [integrated vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization), currently in public preview. You still provide the Azure OpenAI endpoint and deployed model, but chunking and vectorization is integrated into the indexing pipeline, and text queries can be vectorized at query time.

## Prerequisites  

+ An Azure subscription, with [access to Azure OpenAI service](https://aka.ms/oai/access). You must have the Azure OpenAI service endpoint and an API key.

+ A deployment of the **text-embedding-ada-002** embedding model hosted on your Azure OpenAI resource. We use API version 2023-05-15 in these demos. You can change the deployment name, bu tthe default is **text-embedding-ada-002**

+ Model capacity should be sufficient to handle the load. We successfully tested these samples on a deployment model having a 33K tokens per minute rate limit. 

+ An Azure AI Search service with room for a new index, and room for an indexer, data source, and skillset. You must have full endpoint and an admin API key.  

+ An Azure Storage account, with a blob container containing sample data, such as the [health plan PDFs](https://github.com/Azure-Samples/azure-search-sample-data/tree/main/health-plan).

+ Azure SDK for .NET 5.0 or later. This project specifies 11.6.0-beta.1 for preview features.

You can use [Visual Studio](https://visualstudio.microsoft.com/) or [Visual Studio Code with the C# extension](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp) for these demos.  

## Setup  

1. Clone this repository.  

2. Create a `local.settings.json` file in the same directory by copying the `local.settings-sample.json` file and changing the following variables appropriately
  
```json  
{
    "AZURE_SEARCH_SERVICE_ENDPOINT": "",
    "AZURE_SEARCH_INDEX_NAME": "demovectorizer",
    "AZURE_SEARCH_ADMIN_KEY": "",
    "AZURE_OPENAI_ENDPOINT": "",
    "AZURE_OPENAI_API_KEY": "",
    "AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL": "text-embedding-ada-002",
    "AZURE_BLOB_CONNECTION_STRING": "",
    "AZURE_BLOB_CONTAINER_NAME": ""
}
```  
  
Here's an example with fictitious values:  
  
```json  
{  
   "AZURE_SEARCH_SERVICE_ENDPOINT": "https://demo-srch-eastus.search.windows.net",  
   "AZURE_SEARCH_INDEX_NAME": "demo-vector-index",  
   "AZURE_SEARCH_ADMIN_KEY": "000000000000000000000000000000000", // May be omitted if using RBAC auth  
   "AZURE_OPENAI_ENDPOINT": "https://demo-openai-southcentralus.openai.azure.com/",  
   "AZURE_OPENAI_API_KEY": "0000000000000000000000000000000000",  // May be omitted if using RBAC auth
   "AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL": "text-embedding-ada-002",
   "AZURE_BLOB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=000000000000000000000000==;EndpointSuffix=core.windows.net", // May be in the ResourceId= format if using RBAC auth / managed identity
   "AZURE_BLOB_CONTAINER_NAME": "health-plan-pdfs"
}  
```  

## Run the code  

Before running the code, ensure you have the .NET SDK installed on your machine.  

1. If you're using Visual Studio Code, select **Terminal** and **New Terminal** to get a command line prompt.   
  
1. For each project, navigate to the project folder (e.g., `demo-dotnet/DotNetVectorDemo` or `demo-dotnet/DotNetIntegratedVectorizationDemo`) in your terminal and execute the following command to verify .Net 5.0 or later is installed:  
  
   ```bash  
   dotnet build  
   ```  

1. Run the program:  
  
```bash  
dotnet run -- -h
```

```
Description:
  .NET Integrated Vectorization Demo

Usage:
  DotNetIntegratedVectorizationDemo [options]

Options:
  --setup-and-run-indexer  Sets up integrated vectorization indexer with a skillset.
  --query <query>          Optional text of the search query. By default no query is run. Unless --textOnly is
                           specified, this query is automatically vectorized. []
  --filter <filter>        Optional filter of the search query. By default no filter is applied []
  -k <k>                   How many results to return if running a query. [default: 3]
  --exhaustive             Optional, specifies if the query skips using the index and computes the true nearest
                           neighbors. Can only be used with vector or hybrid queries. [default: False]
  --text-only              Optional, specifies if the query is vectorized before searching. If true, only the text
                           indexed is used for search. [default: False]
  --hybrid                 Optional, specifies if the query combines text and vector results. [default: False]
  --semantic               Optional, specifies if the semantic reranker is used to rerank results from the query.
                           [default: False]
  --version                Show version information
  -?, -h, --help           Show help and usage information
```

1. Setup and run the indexer using the following command

```bash
dotnet run -- -setup-and-run-indexer
```
For **DotNetIntegratedVectorizationDemo**, sample data should be PDFS or documents large enough for chunking into segments. If you're using the sample health plan PDFs, some vector queries might be "what health plan is the most comprehensive" or "is there coverage for alternative medicine".  

1. Run a test query using the following examples:

```bash
dotnet run -- -query "is there coverage for alternative medicine" -hybrid -semantic
```

The output will be the chunks matched by the query and their relevance score. If [semantic](https://learn.microsoft.com/azure/search/semantic-search-overview) is specified, [captions and answers](https://learn.microsoft.com/azure/search/semantic-answers) will be included in the output if they are available.

## Output  

Output is a search index. You can use the Azure portal to explore the index definition or delete the index if you no longer need it.  

## Troubleshoot errors  

If you get error 429 from Azure OpenAI service, it means the resource is over capacity:  

+ Check the Activity Log of the Azure OpenAI service to see what else might be running.  

+ Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.  

+ Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).