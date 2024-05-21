@minLength(1)
@description('Primary location for all resources')
param location string

@description('The AI Hub resource name.')
param hubName string
@description('The AI Project resource name.')
param projectName string
param serverlessModelId string
param serverlessModelVersion string
param serverlessEndpointName string
param marketplaceSubscriptionName string
@description('The Key Vault resource name.')
param keyVaultName string
@description('The Storage Account resource name.')
param storageAccountName string
param storageContainerName string
@description('The Log Analytics resource name.')
param logAnalyticsName string = ''
@description('The Application Insights resource name.')
param appInsightsName string = ''
@description('The Container Registry resource name.')
param containerRegistryName string = ''
@description('The Azure Search resource name.')
param searchName string = ''
param searchSku string = ''
param searchSemanticSku string = ''
param searchAuthOptions object = {}
param searchLocation string = ''
param searchResourceGroupName string = ''

param tags object = {}

module hubDependencies '../ai/hub-dependencies.bicep' = {
  name: 'hubDependencies'
  params: {
    location: location
    tags: tags
    keyVaultName: keyVaultName
    storageAccountName: storageAccountName
    storageContainerName: storageContainerName
    containerRegistryName: containerRegistryName
    appInsightsName: appInsightsName
    logAnalyticsName: logAnalyticsName
    searchName: searchName
    searchSku : searchSku
    searchSemanticSku: searchSemanticSku
    searchAuthOptions: searchAuthOptions
    searchLocation: searchLocation
    searchResourceGroupName: searchResourceGroupName
  }
}

module hub '../ai/hub.bicep' = {
  name: 'hub'
  params: {
    location: location
    tags: tags
    name: hubName
    displayName: hubName
    keyVaultId: hubDependencies.outputs.keyVaultId
    storageAccountId: hubDependencies.outputs.storageAccountId
    containerRegistryId: hubDependencies.outputs.containerRegistryId
    appInsightsId: hubDependencies.outputs.appInsightsId
    aiSearchName: hubDependencies.outputs.searchName
    searchResourceGroupName: searchResourceGroupName
  }
}

module project '../ai/project.bicep' = {
  name: 'project'
  params: {
    location: location
    tags: tags
    name: projectName
    displayName: projectName
    hubName: hub.outputs.name
    keyVaultName: hubDependencies.outputs.keyVaultName
  }
}

module marketplaceSubscription '../ai/marketplace-subscription.bicep' = {
  name: 'marketplaceSubscription'
  params: {
    aiProjectName: project.outputs.name
    name: marketplaceSubscriptionName
    modelId: serverlessModelId
  }
}

module serverlessEndpoint 'serverless-endpoint.bicep' = {
  name: 'serverlessEndpoint'
  params: {
    location: location
    tags: tags
    name: serverlessEndpointName
    aiProjectName: project.outputs.name
    modelId: !empty(serverlessModelVersion) ? '${serverlessModelId}/versions/${serverlessModelVersion}' : serverlessModelId
  }
  dependsOn: [ marketplaceSubscription ]
}

// Outputs
// Resource Group
output resourceGroupName string = resourceGroup().name

// Hub
output hubName string = hub.outputs.name
output hubPrincipalId string = hub.outputs.principalId

// Project
output projectName string = project.outputs.name
output projectPrincipalId string = project.outputs.principalId

// Serverless endpoint
output endpointName string = serverlessEndpoint.outputs.name
output marketplaceSubscriptionName string = marketplaceSubscription.outputs.name

// Key Vault
output keyVaultName string = hubDependencies.outputs.keyVaultName
output keyVaultEndpoint string = hubDependencies.outputs.keyVaultEndpoint

// Application Insights
output appInsightsName string = hubDependencies.outputs.appInsightsName
output logAnalyticsWorkspaceName string = hubDependencies.outputs.logAnalyticsWorkspaceName

// Container Registry
output containerRegistryName string = hubDependencies.outputs.containerRegistryName
output containerRegistryEndpoint string = hubDependencies.outputs.containerRegistryEndpoint

// Storage Account
output storageAccountName string = hubDependencies.outputs.storageAccountName
output storageAccountId string = hubDependencies.outputs.storageAccountId
output storageAccountBlobUrl string = hubDependencies.outputs.storageAccountBlobUrl

// Search
output searchName string = hubDependencies.outputs.searchName
output searchEndpoint string = hubDependencies.outputs.searchEndpoint
output searchPrincipalId string = hubDependencies.outputs.searchPrincipalId
