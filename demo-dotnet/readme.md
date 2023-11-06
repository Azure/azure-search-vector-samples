# Readme: Azure Cognitive Search - Vector search using Azure OpenAI service with .NET  
   
This repository contains two .NET console applications that demonstrate how to generate text embeddings using Azure OpenAI service, insert those embeddings into vector fields in Azure Cognitive Search, and issue vector queries. Queries include vector searches with metadata filtering and hybrid (text + vectors) search. The code uses Azure OpenAI service to generate embeddings for titleVector and contentVector fields. You'll need access to Azure OpenAI service to run these demos.  
   
The first project, **DotNetVectorDemo**, reads the `text-sample.json` file, which contains the raw data for which embeddings are generated. It uses the Push API to index documents from a local JSON file.  
   
The second project, **DotNetIntegratedVectorizationDemo**, uses the Indexer in Azure Search to index PDF documents from blob storage and chunk/split and generate embeddings via built-in skills.  
   
The output is a combination of human-readable text and embeddings that can be pushed into a search index.  
   
## Prerequisites  
   
To run these demos, you'll need the following:  
   
+ An Azure subscription, with [access to Azure OpenAI service](https://aka.ms/oai/access). You must have the Azure OpenAI service endpoint and an API key.  
   
+ A deployment of the **text-embedding-ada-002** embedding model. We use API version 2023-05-15 in these demos. For the deployment name, the deployment name is the same as the model, "text-embedding-ada-002".  
   
+ Model capacity should be sufficient to handle the load. We successfully tested these samples on a deployment model having a 33K tokens per minute rate limit.  
   
+ Azure SDK for .NET 5.0 or later.  
   
+ An Azure Cognitive Search service with room for a new index. You must have full endpoint and an admin API key.  
   
You can use [Visual Studio](https://visualstudio.microsoft.com/) or [Visual Studio Code with the C# extension](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp) for these demos.  
   
## Setup  
   
1. Clone this repository.  
   
2. Create a `local.settings.json` file in the same directory as the code for each project and include the following variables:  
  
   ```json  
   {  
    "AZURE_SEARCH_SERVICE_ENDPOINT": "YOUR-SEARCH-SERVICE-ENDPOINT",  
    "AZURE_SEARCH_INDEX_NAME": "YOUR-SEARCH-SERVICE-INDEX-NAME",  
    "AZURE_SEARCH_ADMIN_KEY": "YOUR-SEARCH-SERVICE-ADMIN-KEY",  
    "AZURE_OPENAI_ENDPOINT": "YOUR-OPENAI-ENDPOINT",  
    "AZURE_OPENAI_API_KEY": "YOUR-OPENAI-API-KEY",  
    "AZURE_OPENAI_API_VERSION": "YOUR-OPENAI-API-VERSION",  
    "AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL": "YOUR-OPENAI-MODEL-DEPLOYMENT-NAME"  
   }  
   ```  
  
   Here's an example with fictitious values:  
  
   ```json  
   {  
    "AZURE_SEARCH_SERVICE_ENDPOINT": "https://demo-srch-eastus.search.windows.net",  
    "AZURE_SEARCH_INDEX_NAME": "demo-vector-index",  
    "AZURE_SEARCH_ADMIN_KEY": "000000000000000000000000000000000",  
    "AZURE_OPENAI_ENDPOINT": "https://demo-openai-southcentralus.openai.azure.com/",  
    "AZURE_OPENAI_API_KEY": "0000000000000000000000000000000000",  
    "AZURE_OPENAI_API_VERSION": "2023-05-15",  
    "AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL": "text-embedding-ada-002"  
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
   dotnet run  
   ```  
   
1. When prompted, select "Y" to create and load the index. Wait for the query prompt.  
   
1. Choose a query type, such as single vector query or a hybrid query. The program calls Azure OpenAI service to convert your query string into a vector.  
  
   Sample data is 108 descriptions of Azure services, so your query should be about Azure. For example, for a vector query, type in "what Azure services support full text search" or "what product has OCR".  
   
## Output  
   
Output is a search index. You can use the Azure portal to explore the index definition or delete the index if you no longer need it.  
   
## Troubleshoot errors  
   
If you get error 429 from Azure OpenAI service, it means the resource is over capacity:  
   
+ Check the Activity Log of the Azure OpenAI service to see what else might be running.  
   
+ Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.  
   
+ Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).