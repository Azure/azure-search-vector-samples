# (ARCHIVED) Change-List for the private preview

Please visit our "What's new" REST API documentation to keep up with the change tracking. https://learn.microsoft.com/azure/search/whats-new

As the private preview progresses, we'll have updates on bugs or behavior changes, doc updates, and demo updates. Check back here for a status summary of those updates.

| Version | Date       | Changes | Regions |  
| ------- | ---------- | ------- | --------|  
| v0.1    | 2023-04-06 | Initial release | All |  
| v0.2    | 2023-04-24 | **[BREAKING]** Updated "vectorSearch" configuration properties, enabled on existing indexes and all tiers, add "efSearch" property to "hnsw". | All | 
| NA      | 2023-06-09 | Removed obsolete Postman collection (v0.1) | NA |
| NA      | 2023-07-07 | Private preview is concluded. Vector search is now in public preview. | All |

## v0.2 changes

Our latest deployment includes a breaking change to the 2023-07-01-preview REST APIs. You must immediately update your code to continue testing.

1. In index definitions, "algorithmConfiguration" has been changed to "vectorSearchConfiguration".

2. In index definitions, we added a new "hnswParameter": "efSearch". This property allows you to tune the size of the dynamic list containing the nearest neighbors, which is used during search time. Increasing this parameter may improve the quality search results, at the expense of performance. Increasing this parameter to larger values eventually leads to diminishing returns. A default value 500 will be used if the parameter is omitted or null. The allowable range is 100 to 1000.

3. In index definitions, "vectorSearch.algorithmConfigurations.algorithm" is now "vectorSearch.algorithmConfigurations.kind". 

The following example illustrates the v0.2 updates:

```json
"fields": [
   {
    "name": "contentVector",
    "type": "Collection(Edm.Single)",
    "searchable": true,
    "retrievable": true,
    "dimensions": 1536,
    "vectorSearchConfiguration": "my-vector-config"
   }
],
"vectorSearch": {
    "algorithmConfigurations": [
        {
            "name": "my-vector-config",
            "kind": "hnsw",
            "hnswParameters": {
                "m": 4,
                "efConstruction": 400,
                "metric": "cosine",
                "efSearch": 500
            }
        }
      ]
  }
```
