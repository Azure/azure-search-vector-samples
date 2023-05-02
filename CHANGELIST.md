# Change-List for the private preview

As the private preview progresses, we'll have updates on bugs or behavior changes, doc updates, and demo updates. Check back here for a status summary of those updates.

| Version | Date       | Changes                                                                                                                             |
| ------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| v0.1    | 2023-04-06 | Initial release                                                                                                                     |
| v0.2    | 2023-04-24 | **[BREAKING]** Updated vectorSearch configuration properties, enabled existing indexes and all tiers, add efSearch property to hnsw |

Our latest deployment includes a breaking change to the API 2023-07-01 Preview API Version that you must update in your testing.

1. In your index definition, **algorithmConfiguration** has been updated to **vectorSearchConfiguration**

2. In your index definition, we have added a new hnswParamater **efSearch**. This property allows you to tune the size of the dynamic list containing the nearest neighbors, which is used during search time. Increasing this parameter may improve search results, at the expense of slower search. Increasing this parameter eventually leads to diminishing returns. A default value 800 will be used if this is omitted or null. The allowable range will be 100 to 1000.

3. In your index definition, **vectorSearch.algorithmConfigurations.algorithm** is now **vectorSearch.algorithmConfigurations.kind**. See below sample of the required updates:

```
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
