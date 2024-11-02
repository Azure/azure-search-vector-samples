---
page_type: sample
languages:
  - csharp
name: Vector storage and retrieval in C#
description: |
  Using Azure.Search.Documents, index and query vectors in a RAG pattern or a traditional search solution.
products:
  - azure
  - azure-cognitive-search
urlFragment: csharp-vector-search
---

# Vector search in C# (Azure AI Search)  

In this .NET console application for Azure AI Search, **DotNetVectorDemo** provides raw data for which embeddings are generated externally and then pushed into a search index for queries. First, it calls Azure OpenAI resource and a deployment of the text-embedding-3-small model to create embeddings for text in a local `text-sample.json` file. Next, it pushes the embeddings and other textual content to a search index. The searchable output is a combination of human-readable text and embeddings that can be queried from your code. Note that a pre-populated set of these embeddings is already provided in `vector-sample.json`.

## Prerequisites  

+ An Azure subscription, with [access to Azure OpenAI service](https://aka.ms/oai/access). You must have the Azure OpenAI service endpoint and an API key if you are not using RBAC authentication.

+ A deployment of the **text-embedding-3-small** embedding model. For the deployment name, the deployment name is the same as the model, "text-embedding-3-small".  

+ Model capacity should be sufficient to handle the load. We successfully tested these samples on a deployment model having a 33K tokens per minute rate limit.  

+ An Azure AI Search service with room for a new index. You must have full endpoint and an admin API key if you are not using RBAC authentication.  

+ Azure SDK for .NET 5.0 or later. The project specifies 11.7.0-beta.1 to use preview features

You can use [Visual Studio](https://visualstudio.microsoft.com/) or [Visual Studio Code with the C# extension](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp) for these demos.  

## Setup  

1. Clone this repository.  

2. Create a `local.settings.json` file in the same directory as the code for each project and include the following variables:  
  
   ```json  
    {
      "AZURE_SEARCH_SERVICE_ENDPOINT": "YOUR-SEARCH-SERVICE-ENDPOINT",
      "AZURE_SEARCH_INDEX_NAME": "YOUR-SEARCH-INDEX",
      "AZURE_OPENAI_ENDPOINT": "YOUR-AZURE-OPENAI-ENDPOINT"
    }
   ```  
  
   Here's an example with fictitious values:  
  
   ```json  
   {  
    "AZURE_SEARCH_SERVICE_ENDPOINT": "https://demo-srch-eastus.search.windows.net",  
    "AZURE_SEARCH_INDEX_NAME": "demo-vector-index",  
    "AZURE_OPENAI_ENDPOINT": "https://demo-openai-southcentralus.openai.azure.com/",  
   ```

You can find more values to set by checking `Configuration.cs`

## Run the code  

Before running the code, ensure you have the .NET SDK installed on your machine.  

1. If you're using Visual Studio Code, select **Terminal** and **New Terminal** to get a command line prompt.   
  
1. For each project, navigate to the project folder (e.g., `demo-dotnet/DotNetVectorDemo` or `demo-dotnet/DotNetIntegratedVectorizationDemo`) in your terminal and execute the following command to verify .Net 5.0 or later is installed:  
  
    ```bash  
    dotnet run -- -h
    ```

    ```
    dotnet run -- -h
    Description:
      .NET Vector demo

    Usage:
      DotNetVector [options]

    Options:
      --setup-index      Indexes sample documents. text-embedding-3-small embeddings with a dimension of 1024 are used
      --query <query>    Optional text of the search query. By default no query is run. Unless --textOnly is specified, this query is automatically vectorized. []
      --filter <filter>  Optional filter of the search query. By default no filter is applied []
      -k <k>             How many nearest neighbors to use for vector search. Defaults to 50 [default: 50]
      --top <top>        How nany results to return. Defaults to 3 [default: 3]
      --exhaustive       Optional, specifies if the query skips using the index and computes the true nearest neighbors. Can only be used with vector or hybrid queries. [default:
                         False]
      --text-only        Optional, specifies if the query is vectorized before searching. If true, only the text indexed is used for search. [default: False]
      --hybrid           Optional, specifies if the query combines text and vector results. [default: False]
      --semantic         Optional, specifies if the semantic reranker is used to rerank results from the query. [default: False]
      --debug <debug>    Optional, specifies if debug output is included from the query. Only valid values are disabled (default), semantic, or vector [default: disabled]
      --version          Show version information
      -?, -h, --help     Show help and usage information
    ```

1. Setup a sample index using the following command. It will use a file of pre-populated embeddings created by `text-embedding-3-small` with a dimension of 1024
  
   ```bash  
   dotnet run -- --setup-index
   ```  

1. Run a test query using the following examples:

```bash
dotnet run -- --query "What is Azure Search" --hybrid --semantic
```

The output will be the chunks matched by the query and their relevance score. If [semantic](https://learn.microsoft.com/azure/search/semantic-search-overview) is specified, [captions and answers](https://learn.microsoft.com/azure/search/semantic-answers) will be included in the output if they are available.

## Output  

Output is a search index. You can use the Azure portal to explore the index definition or delete the index if you no longer need it.  

## Troubleshoot errors  

If you get error 429 from Azure OpenAI service, it means the resource is over capacity:  

+ Check the Activity Log of the Azure OpenAI service to see what else might be running.  

+ Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.  

+ Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).