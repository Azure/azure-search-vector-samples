---
page_type: sample
languages:
  - python
name: Vector quantization and storage options in C#
products:
  - azure
  - azure-ai-search
description: |
  Using Azure.Search.Documents and the Azure SDK for C#, save on storage when using vector quantization
urlFragment: quantization-storage-c#
---

# Vector quantization and storage options using C# (Azure AI Search)  

The C# program creates vectorized data on Azure AI Search and demonstrates how to save on storage using the following features

- Quantization
- Disabling storage of vectors returned in query responses. These vectors are stored separately from vectors used for the queries themselves.
- Smaller data types than `Edm.Single`.

The sample data is a JSON file containing a pre-chunked version of the sample documents. They have been embedded using text-embedding-3-large with 3072 dimensions.

## Prerequisites

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access).

- Azure AI Search, any version, but make sure search service capacity is sufficient for the workload. We recommend Basic or higher for this demo.

+ Azure SDK for .NET 5.0 or later. 

You can use [Visual Studio](https://visualstudio.microsoft.com/) or [Visual Studio Code with the C# extension](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csharp) for these demos.  

## Run the code

Before running the code, ensure you have the .NET SDK installed on your machine.

1. Clone this repository.  

1. Create a `local.settings.json` file in the same directory as the code that follows the same pattern as `local.settings-sample.json`

1. If you're using Visual Studio Code, select **Terminal** and **New Terminal** to get a command line prompt.   
  
1. For each project, navigate to the project folder (e.g., `demo-dotnet/QuantizationAndStorageOptions`) in your terminal and execute the following command to verify .Net 5.0 or later is installed:  
  
   ```bash  
   dotnet build  
   ```  

1. Run the program:  
  
   ```bash  
   dotnet run  
   ```  
