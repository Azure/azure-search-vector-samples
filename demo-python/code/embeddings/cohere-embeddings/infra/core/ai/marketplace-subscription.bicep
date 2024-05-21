param aiProjectName string
param name string
param modelId string

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' existing = {
  name: aiProjectName
}

resource marketplaceSubscription 'Microsoft.MachineLearningServices/workspaces/marketplaceSubscriptions@2024-04-01-preview' = {
  parent: workspace
  name: name
  properties: {
    modelId: modelId
  }
}
