param name string
param location string
param tags object
param aiProjectName string
param onlineEndpointName string
param instanceType string
param capacity int
param model string

var sku = {
  name: 'Default'
  capacity: capacity
}

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' existing = {
  name: aiProjectName
}

resource endpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2024-04-01-preview' existing = {
  name: onlineEndpointName
  parent: workspace
}

resource deployment 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints/deployments@2024-04-01-preview' = {
  name: name
  parent: endpoint
  tags: tags
  properties: {
      endpointComputeType: 'Managed'
      instanceType: instanceType
      model: model
      scaleSettings: {
        scaleType: 'Default'
      }
      requestSettings: {
        requestTimeout: 'PT90S'
        maxConcurrentRequestsPerInstance: 1
      }
      livenessProbe: {
        initialDelay: 'PT600S'
        period: 'PT10S'
        timeout: 'PT2S'
        successThreshold: 1
        failureThreshold: 30
    }
  }
  location: location
  kind: 'Managed'
  sku: sku
}

output name string = deployment.name
