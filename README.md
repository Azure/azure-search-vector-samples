# Vector samples - Azure AI Search

This repository provides Python, C#, REST, and JavaScript code samples for [vector support](https://learn.microsoft.com/azure/search/vector-search-overview) in Azure AI Search.

There are breaking changes from REST API version 2023-07-01-Preview to newer API versions. These breaking changes also apply to the Azure SDK beta packages targeting that REST API version. See [Upgrade REST APIs](https://learn.microsoft.com/azure/search/search-api-migration) for migration guidance.

## Feature status

Vector support consists of generally available features and preview features.

| Feature | Status |
|---------|--------|
| [vector indexing](https://learn.microsoft.com/azure/search/vector-search-how-to-create-index) | generally available (2023-11-01 and stable SDK packages) |
| [vector queries](https://learn.microsoft.com/azure/search/vector-search-how-to-query) | generally available (2023-11-01 and stable SDK packages)|
| [integrated data chunking](https://learn.microsoft.com/azure/search/cognitive-search-skill-textsplit) | public preview (2023-10-01-preview and later, plus beta SDK packages) |
| [integrated embedding](https://learn.microsoft.com/azure/search/cognitive-search-skill-azure-openai-embedding) | public preview (2023-10-01-preview and later, plus beta SDK packages) |
| [index projections](https://learn.microsoft.com/azure/search/index-projections-concept-intro) | public preview (2023-10-01-preview and later, plus beta SDK packages) |
| [vectorizers](https://learn.microsoft.com/azure/search/vector-search-how-to-configure-vectorizer) | public preview (2023-10-01-preview and later, plus beta SDK packages) |
| [scalar quantization](https://learn.microsoft.com/azure/search/vector-search-how-to-configure-compression-storage) | public preview (2024-03-01-preview and later, plus beta SDK packages) |

Preview features are available under [Supplemental Terms of Use](https://azure.microsoft.com/support/legal/preview-supplemental-terms/). 

## demo-dotnet samples

| Sample | Description | Status |
| ------ | ------------|--------|
| [DotNetVectorDemo](demo-dotnet/DotNetVectorDemo/readme.md) | A .NET console app that calls Azure OpenAI to vectorize data. It then calls Azure AI Search to create, load, and query vector data.| Generally available (GA) |
| [DotNetIntegratedVectorizationDemo](demo-dotnet/DotNetIntegratedVectorizationDemo/readme.md) | A .NET console app that calls Azure AI Search to create an index, indexer, data source, and skillset. An Azure Storage account provides the data. Azure OpenAI is called by the skillset during indexing, and again during query execution to vectorize text queries. | Public preview |
| [QuantizationAndStorageOptions](demo-dotnet/demo-dotnet/QuantizationAndStorageOptions/readme.md) | A .NET console app that demonstrates [narrow data types](https://learn.microsoft.com/rest/api/searchservice/supported-data-types#edm-data-types-for-vector-fields) and built-in scalar quantization, reducing vector index size in memory and on disk. It also disables storage of vectors returned in query response, which you don't need if you're not returning vectors in a query.  | Public preview |

## demo-python samples

| Sample | Description | Status |
| ------ | ------------|--------|
| [demo-python readme](demo-python/readme.md) |  A growing collection of notebooks that demonstrate aspects of vector search support, including data chunking and embedding of both text and image content and queries, using a variety of frameworks and techniques.| GA and preview | 

## demo-java samples

| Sample | Description | Status |
| ------ | ------------|--------|
| [demo-vectors](demo-java/demo-vectors/readme.md) | A Java console app that calls Azure OpenAI to vectorize data. It then calls Azure AI Search to create, load, and query vector data.| GA | 
| [demo-integrated-vectorization](demo-java/demo-integrated-vectorization/readme.md) | A Java console app that calls Azure AI Search to create an index, indexer, data source, and skillset. An Azure Storage account provides the data. Azure OpenAI is called by the skillset during indexing, and again during query execution to vectorize text queries. | GA and preview | 

## demo-javascript samples

| Sample | Description | Status |
| ------ | ------------|--------|
| [JavaScriptVectorDemo](demo-javascript/readme.md) | A single folder contains three code samples. The `azure-search-vector-sample.js` script calls just Azure OpenAI and is used to generate embeddings for fields in an index. The `docs-text-openai-embeddings.js` program is an end-to-end code sample that calls Azure OpenAI for embeddings and Azure AI Seach to create, load, and query an index that contains vectors. The `query-text-openai-embeddings.js` script generates an embedding for a vector query. | GA and preview | 

## Other vector samples and tools

- [azure-ai-search-lab](https://github.com/jelledruyts/azure-ai-search-lab) A learning and experimentation lab for trying out various AI-enabled search scenarios in Azure. It includes web application front-end which uses Azure AI Search and Azure OpenAI to execute searches with a variety of options - ranging from simple keyword search, to semantic ranking, vector and hybrid search, and using generative AI to answer search queries in various ways. This allows you to quickly understand what each option does, how it affects the search results, and how various approaches compare against each other.
- [chat-with-your-data-solution-accelerator](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator) A template that deploys multiple Azure resources for a custom chat-with-your-data solution. Use this accelerator to create a production-ready solution that implements coding best practices.
- [Azure Search OpenAI Demo](https://github.com/Azure-Samples/azure-search-openai-demo/tree/vectors) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences. Use the "vectors" branch to leverage Vector retrieval.
- [Azure Search OpenAI Demo - C#](https://github.com/Azure-Samples/azure-search-openai-demo-csharp/tree/feature/embeddingSearch) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences using C#.
- [Azure OpenAI Embeddings QnA with Azure Search as a Vector Store](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) (github.com) A simple web application for a OpenAI-enabled document search. This repo uses Azure OpenAI Service for creating embeddings vectors from documents. For answering the question of a user, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences.
- [ChatGPT Retreival Plugin Azure Search Vector Database](https://github.com/openai/chatgpt-retrieval-plugin/blob/main/README.md#azure-cognitive-search) The ChatGPT Retrieval Plugin lets you easily find personal or work documents by asking questions in natural language. Azure AI Search now supported as an official vector database.
- [Azure Search Vector Search Demo Web App Template](https://github.com/farzad528/azure-search-vector-search-demo) A Vector Search Demo React Web App Template using Azure OpenAI for Text Search and Cognitive Services Florence Vision API for Image Search.
- [Azure Cognitive Search Comparison Tool](https://github.com/Azure-Samples/azure-search-comparison-tool)

## Documentation

- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)

  - [Retrieval Augmented Generation (RAG) in Azure AI Search](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
  - [Vector search overview](https://learn.microsoft.com/azure/search/vector-search-overview)
  - [Hybrid search overview](https://learn.microsoft.com/azure/search/hybrid-search-overview)
  - [Create a vector index](https://learn.microsoft.com/azure/search/vector-search-how-to-create-index)
  - [Query a vector index](https://learn.microsoft.com/azure/search/vector-search-how-to-query)
  - [Vector search algorithms](https://learn.microsoft.com/azure/search/vector-search-ranking)
  - [REST API reference](https://learn.microsoft.com/rest/api/searchservice/)

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)

- [Azure AI Vision Documentation](https://learn.microsoft.com/azure/cognitive-services/computer-vision/)
