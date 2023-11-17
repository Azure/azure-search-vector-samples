# Vector search samples - Azure AI Search

This repository provides code samples for the [vector search](https://learn.microsoft.com/azure/search/vector-search-overview) in Azure AI Search.

Vector search is generally available, but it also has capabilities that are still in preview, under [Supplemental Terms of Use](https://azure.microsoft.com/support/legal/preview-supplemental-terms/), without a service level agreement. Vector indexing and queries are generally available. 

[Integrated data chunking and vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization), which takes a dependency on indexers and skillsets, is in preview.

## Content

| Sample | Description | Status |
| ------ | ------------|--------|
| [demo-dotnet/DotNetVectorDemo](demo-dotnet/DotNetVectorDemo/readme.md) | A .NET Console App that calls Azure OpenAI to create vectorized data. It then calls Azure AI Search to create, load, and query the data.| Generally available (GA) |
| [demo-dotnet/DotNetIntegratedVectorizationDemo](demo-dotnet/DotNetIntegratedVectorizationDemo/readme.md) | A .NET Console App that calls Azure AI Search to create an index, indexer, data source, and skillset. An Azure Storage account provides the data. Azure OpenAI is called by the skillset during indexing, and again during query execution to vectorize text queries. | Public preview |
| [demo-javaScript/JavaScriptVectorDemo](demo-javascript/JavaScriptVectorDemo/readme.md) | There are three code samples. One is an end-to-end code sample that calls Azure OpenAI for embeddings and Azure AI Seach to create, load, and query an index that contains vectors. Another sample calls just Azure OpenAI and is used to generate embeddings for fields in an index. The last one also calls just Azure OpenAI and is used to generate an embedding for a vector query. | GA |
| [demo-python](demo-python/readme.md) |  A series of notebooks that demonstrate aspects of vector search, including data chunking and vectorization of both text and image content. | GA and preview | 
| [Postman collection](postman-collection/Vector%20Search%20QuickStart.postman_collection%20v1.0.json)| A collection of REST API calls to an Azure AI Search instance to create, load, and query a search index that contains text and vector fields. The requests in this collection include an index schema, sample documents, and sample queries. Use the [Postman app](https://www.postman.com/downloads/) and import the collection. | GA and preview | 

## Related samples and tools

- [chat-with-your-data-solution-accelerator](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator) A template that deploys multiple Azure resources for a custom chat-with-your-data solution. Use this accelerator to create a production-ready solution that implements coding best practices.
- [Azure Search OpenAI Demo](https://github.com/Azure-Samples/azure-search-openai-demo/tree/vectors) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences. Use the "vectors" branch to leverage Vector retrieval.
- [Azure Search OpenAI Demo - C#](https://github.com/Azure-Samples/azure-search-openai-demo-csharp/tree/feature/embeddingSearch) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences using C#.
- [Azure OpenAI Embeddings QnA with Azure Search as a Vector Store](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) (github.com) A simple web application for a OpenAI-enabled document search. This repo uses Azure OpenAI Service for creating embeddings vectors from documents. For answering the question of a user, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences.
- [ChatGPT Retreival Plugin Azure Search Vector Database](https://github.com/openai/chatgpt-retrieval-plugin/blob/main/README.md#azure-cognitive-search) The ChatGPT Retrieval Plugin lets you easily find personal or work documents by asking questions in natural language. Azure AI Search now supported as an official vector database.
- [Azure Search Vector Search Demo Web App Template](https://github.com/farzad528/azure-search-vector-search-demo) A Vector Search Demo React Web App Template using Azure OpenAI for Text Search and Cognitive Services Florence Vision API for Image Search.
- [Azure Cognitive Search Comparison Tool](https://github.com/Azure-Samples/azure-search-comparison-tool)

## Documentation

- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)

  - [REST API reference](https://learn.microsoft.com/rest/api/searchservice/)
  - [Vector search overview](https://learn.microsoft.com/azure/search/vector-search-overview)
  - [Hybrid search overview](https://learn.microsoft.com/azure/search/vector-search-overview)
  - [Create a vector index](https://learn.microsoft.com/azure/search/vector-search-how-to-create-index)
  - [Query a vector index](https://learn.microsoft.com/azure/search/vector-search-how-to-query)
  - [Vector search algorithms](https://learn.microsoft.com/azure/search/vector-search-ranking)

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)

- [Azure AI Vision Documentation](https://learn.microsoft.com/azure/cognitive-services/computer-vision/)
