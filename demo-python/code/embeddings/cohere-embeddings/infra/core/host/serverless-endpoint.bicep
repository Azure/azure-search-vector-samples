param aiProjectName string
param name string
param modelId string
param location string = resourceGroup().location
param tags object = {}
param sku object = {
  name: 'Consumption'
}

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' existing = {
  name: aiProjectName
}

resource serverlessEndpoint 'Microsoft.MachineLearningServices/workspaces/serverlessEndpoints@2024-04-01-preview' = {
  name: name
  parent: workspace
  location: location
  tags: tags
  sku: sku
  properties: {
    modelSettings: {
      modelId: modelId
    }
    authMode: 'Key'
  }
}

output name string = serverlessEndpoint.name
