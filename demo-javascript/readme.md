---
page_type: sample
languages:
  - javascript
name: Vector search in Node.js
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using @azure/search-documents and Node.js, index and query vectors in a RAG pattern or a traditional search solution.
urlFragment: vector-search-javascript
---

# Vector search using Node.js  (Azure AI Search)  

The JavaScript demo in this repository creates vectorized data that can be indexed and queried on Azure AI Search.

| Samples | Description |
|---------|-------------|
| **azure-search-vector-sample.js** | [End-to-end sample](#run-the-end-to-end-sample-program). It uses **@azure/search-documents** in the Azure SDK for JavaScript. You can use this to either revectorize the included sample data in `text-sample.json`, or you can use it to initialize a new index on your Azure AI Search service with the pre-vectorized sample data. When revectorizing or querying, it accesses a deployed model on your Azure OpenAI resource. |

## Prerequisites

+ An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access). You must have the Azure OpenAI service name and an API key.

+ Node.js (these instructions were tested with version Node.js version 16.0)

+ A deployment of the **text-embedding-3-large** embedding model. For the deployment name, the deployment name is the same as the model, "text-embedding-3-large".

+ Model capacity should be sufficient to handle the load.

+ For the end-to-end sample, you also need an Azure AI Search service. Provide the full endpoint, an Admin API key, and an index name as environment variables.

You can use [Visual Studio Code with the JavaScript extension](https://code.visualstudio.com/docs/nodejs/extensions) for this demo. For help setting up the environment, see this [JavaScript quickstart](https://learn.microsoft.com/azure/search/search-get-started-javascript).

## Setup

1. Clone this repository.

1. Copy the .env-sample file to a .env file in the same directory and fill out the missing variables. API-key usage is optional if RBAC is setup. Keys and endpoints can be found in the Azure portal pages for your Azure OpenAI resource and your Azure AI Search resoruce.

1. Select **Terminal** and **New Terminal** to get a command line prompt. Install `npm` dependencies:

   ```bash
   cd demo-javascript/code
   npm install
   ```

## Run the end-to-end sample program


This section explains how to run the separate vectorization programs that call Azure OpenAI. Enter the following statement at the command line:

```bash
node .\azure-search-vector-sample.js -h
```

Output should look similar to this:

```
Usage: azure-search-vector-sample [options]

Options:
  -e, --embed                       Recreate embeddings in text-sample.json
  -u, --upload                      Upload embeddings and data in text-sample.json to the search index
  -q, --query <text>                Text of query to issue to search, if any
  -k, --query-kind <kind>           Kind of query to issue. Defaults to hybrid (choices: "text", "vector", "hybrid", default: "hybrid")
  -c, --category-filter <category>  Category to filter results to
  -t, --include-title               Search over the title field as well as the content field
  --no-semantic-reranker            Do not use semantic reranker. Defaults to false
  -h, --help                        display help for command```
```

#### Upload the sample data

The sample includes data and text-embedding-3-large embeddings for that data in the data/text-sample.json file. You can setup a search index using this sample data and the credentials in the .env file you created as part of setup. Use the following command to upload the sample data:

```bash
node .\azure-search-vector-sample.js --upload
```

Output should look similar to this:

```
Creating index...
Reading data/text-sample.json...
Uploading documents to the index...
Finished uploading documents
```

Once the sample data and embeddings have been uploaded, continue to issue a query.

#### Query the sample data

You can issue vector, text, and hybrid queries. The semantic re-ranker is used by default but can be disabled. You can also issue a cross-field vector query against both the content and the title embeddings, and filter based on the category field. Below is a sample query and its result:

```bash
node .\azure-search-vector-sample.js  --query "what is azure search" --query-kind hybrid --include-title
```

Output should look similar to this:

```
Semantic answer: Azure Cognitive Search is<em> a fully managed search-as-a-service that enables you to build rich search experiences for your applications.</em> It provides features like full-text search, faceted navigation, and filters. Azure Cognitive Search supports various data sources, such as Azure SQL Database, Azure Blob Storage, and Azure Cosmos DB.
Semantic answer score: 0.98583984375

----
Title: Azure AI Search
Score: 0.05000000447034836
Reranker Score: 3.0303308963775635
Content: Azure Cognitive Search is a fully managed search-as-a-service that enables you to build rich search experiences for your applications. It provides features like full-text search, faceted navigation, and filters. Azure Cognitive Search supports various data sources, such as Azure SQL Database, Azure Blob Storage, and Azure Cosmos DB. You can use Azure Cognitive Search to index your data, create custom scoring profiles, and integrate with other Azure services. It also integrates with other Azure services, such as Azure Cognitive Services and Azure Machine Learning.
Category: AI + Machine Learning
Caption: <em>Azure</em> Cognitive<em> Search</em> is a fully managed search-as-a-service that enables you to build rich<em> search</em> experiences for your applications. It provides features like full-text<em> search,</em> faceted navigation, and filters.<em> Azure</em> Cognitive<em> Search</em> supports various data sources, such as<em> Azure</em> SQL Database,<em> Azure</em> Blob Storage, and<em> Azure</em> Cosmos DB.
----


----
Title: Azure Cognitive Services
Score: 0.047642678022384644
Reranker Score: 2.1211702823638916
Content: Azure Cognitive Services is a collection of AI services and APIs that enable you to build intelligent applications using pre-built models and algorithms. It provides features like computer vision, speech recognition, and natural language processing. Cognitive Services supports various platforms, such as .NET, Java, Node.js, and Python. You can use Azure Cognitive Services to build chatbots, analyze images and videos, and process and understand text. It also integrates with other Azure services, such as Azure Machine Learning and Azure Cognitive Search.
Category: AI + Machine Learning
Caption: Azure Cognitive Services is a collection of AI services and APIs that enable you to build intelligent applications using pre-built models and algorithms. It provides features like computer vision, speech recognition, and natural language processing. Cognitive Services supports various platforms, such as .NET, Java, Node.js, and Python.
----


----
Title: Azure Data Explorer
Score: 0.03652850165963173
Reranker Score: 2.0093204975128174
Content: Azure Data Explorer is a fast, fully managed data analytics service for real-time analysis on large volumes of data. It provides features like ingestion, querying, and visualization. Data Explorer supports various data sources, such as Azure Event Hubs, Azure IoT Hub, and Azure Blob Storage. You can use Data Explorer to analyze logs, monitor applications, and gain insights into your data. It also integrates with other Azure services, such as Azure Synapse Analytics and Azure Machine Learning.
Category: Analytics
Caption: Azure Data Explorer is a fast, fully managed data analytics service for real-time analysis on large volumes of data. It provides features like ingestion, querying, and visualization. Data Explorer supports various data sources, such as Azure Event Hubs, Azure IoT Hub, and Azure Blob Storage.
----
```


#### Re-creating the sample embeddings

The text-sample.json file already contains the text-embedding-3-large embeddings for both the content and the title fields. You can re-embed the sample data using the following command:

```bash
node .\azure-search-vector-sample.js --embed
```

Output should look similar to this:

```bash
Reading data/text-sample.json...
Generating embeddings with Azure OpenAI...
Wrote embeddings to data/text-sample.json
```

If you get an error, such as error code 429 or a server error, verify the model deployment capacity is sufficient to process the sample input. 

The generated output consists of embeddings for the title and content fields of the input data (`data/text-sample.json`).

## Troubleshoot errors

If you get error 429 from Azure OpenAI, it means the resource is over capacity:

+ Check the Activity Log of the Azure OpenAI service to see what else might be running.

+ Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.

+ Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).
