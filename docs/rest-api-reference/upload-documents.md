# Add, Update, or Delete Documents

**API Version: 2023-07-01-preview**

This article supplements [Add, Update or Delete Documents](https://learn.microsoft.com/rest/api/searchservice/addupdate-or-delete-documents) on [learn.microsoft.com](https://learn.microsoft.com) with content created for vector search scenarios. Limiting the amount of information makes it easier to find the new additions. 

**2023-07-01-preview** adds:

+ support for vector fields, an array of single-precision floating point numbers, or double-precision floating point numbers.

You can push documents that contain vector fields into a specified index using HTTP POST. For a large update, batching (up to 1000 documents per batch, or about 16 MB per batch) is recommended and will significantly improve indexing performance.  

```http  
POST https://[service name].search.windows.net/indexes/[index name]/docs/index?api-version=2023-07-01-preview  
  Content-Type: application/json   
  api-key: [admin key]  
```  

## URI Parameters

| Parameter	  | Description  | 
|-------------|--------------|
| service name | Required. Set this to the unique, user-defined name of your search service. |
| index name  | Required on the URI, specifying which index to post documents. You can only post documents to one index at a time.  |
| api-version | Required. Use 2023-07-01-preview for this preview.|

## Request Headers

The following table describes the required and optional request headers.  

|Fields              |Description      |  
|--------------------|-----------------|  
|Content-Type|Required. Set this to `application/json`|  
|api-key| Optional if you're using [Azure roles](https://learn.microsoft.com/azure/search/search-security-rbac) and a bearer token is provided on the request, otherwise a key is required. An api-key is a unique, system-generated string that authenticates the request to your search service. Uploading documents requires an admin API key. See [Connect to Cognitive Search using key authentication](https://learn.microsoft.com/azure/search/search-security-api-keys) for details.| 

## Request Body

The body of the request contains one or more documents to be indexed. Documents are identified by a unique case-sensitive key. Each document is associated with an action: "upload", "delete", "merge", or "mergeOrUpload". Upload requests must include the document data as a set of key/value pairs.  

Vector fields can contain thousands of embeddings, depending on the complexity, length, or type of the original content. Cognitive Search doesn't convert content to embeddings. The documents that you push into an index must contain embeddings that you've previously generated.

```json
{  
  "value": [  
    {  
      "@search.action": "upload (default) | merge | mergeOrUpload | delete",  
      "key_field_name": "unique_key_of_document", (key/value pair for key field from index schema)  
      "field_name": field_value (key/value pairs matching index schema)  
        ...  
    },  
    ...  
  ]  
}  
```  

| Property | Description |
|----------|-------------|
| @search.action | Required. Valid values are "upload", "delete", "merge", or "mergeOrUpload". Defaults to "upload". |
| key_field_name | Required. A field definition in the index that serves as the document key and contains only unique values. Document keys can only contain letters, numbers, dashes (`"-"`), underscores (`"_"`), and equal signs (`"="`) and are case-sensitive. 
| field_name | Required. Name-value pairs, where the name of the field corresponds to a field name in the index definition. The value is user-defined but must be valid for the field type. |

## Response

Status code: 200 is returned for a successful response, meaning that all items have been stored durably and will start to be indexed. Indexing runs in the background and makes new documents available (that is, queryable and searchable) a few seconds after the indexing operation completed. The specific delay depends on the load on the service.

Successful indexing is indicated by the status property being set to true for all items, as well as the statusCode property being set to either 201 (for newly uploaded documents) or 200 (for merged or deleted documents).

## Examples

**Example: Upload two documents with text and vector content**

For readability, the following example show a subset of documents and embeddings. The body of the Upload Documents request consists of 108 documents, each with a full set of embeddings for "titleVector" and "contentVector".

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/index?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "value": [
        {
            "id": "1",
            "title": "Azure App Service",
            "content": "Azure App Service is a fully managed platform for building, deploying, and scaling web apps. You can host web apps, mobile app backends, and RESTful APIs. It supports a variety of programming languages and frameworks, such as .NET, Java, Node.js, Python, and PHP. The service offers built-in auto-scaling and load balancing capabilities. It also provides integration with other Azure services, such as Azure DevOps, GitHub, and Bitbucket.",
            "category": "Web",
            "titleVector": [
                -0.02250031754374504,
                 . . . 
                        ],
            "contentVector": [
                -0.024740582332015038,
                 . . .
            ],
            "@search.action": "upload"
        },
        {
            "id": "2",
            "title": "Azure Functions",
            "content": "Azure Functions is a serverless compute service that enables you to run code on-demand without having to manage infrastructure. It allows you to build and deploy event-driven applications that automatically scale with your workload. Functions support various languages, including C#, F#, Node.js, Python, and Java. It offers a variety of triggers and bindings to integrate with other Azure services and external services. You only pay for the compute time you consume.",
            "category": "Compute",
            "titleVector": [
                -0.020159931853413582,
                . . .
            ],
            "contentVector": [
                -0.02780858241021633,,
                 . . .
            ],
            "@search.action": "upload"
        }
        . . .
    ]
}
```

> [!NOTE]
> When you upload `DateTimeOffset` values with time zone information to your index, Azure Cognitive Search normalizes these values to UTC. For example, 2019-01-13T14:03:00-08:00 will be stored as 2019-01-13T22:03:00Z. If you need to store time zone information, you will need to add an extra column to your index.

# See also

+ [Add, Update or Delete Documents](https://learn.microsoft.com/rest/api/searchservice/addupdate-or-delete-documents) on [learn.microsoft.com](https://learn.microsoft.com)