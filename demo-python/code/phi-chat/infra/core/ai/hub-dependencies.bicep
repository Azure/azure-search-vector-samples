param location string = resourceGroup().location
param tags object = {}

@description('Name of the key vault')
param keyVaultName string
@description('Name of the storage account')
param storageAccountName string
param storageContainerName string
@description('Name of the OpenAI cognitive services')
param openAiName string
param openAiModelDeployments array = []
param openAiLocation string
param openAiResourceGroupName string = ''
@description('Name of the Log Analytics workspace')
param logAnalyticsName string = ''
@description('Name of the Application Insights instance')
param appInsightsName string = ''
@description('Name of the container registry')
param containerRegistryName string = ''
@description('Name of the Azure Cognitive Search service')
param searchName string = ''
param searchSku string = ''
param searchSemanticSku string = ''
param searchAuthOptions object = {}
param searchLocation string = ''
param searchResourceGroupName string = ''

module keyVault '../security/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    location: location
    tags: tags
    name: keyVaultName
  }
}

module storageAccount '../storage/storage-account.bicep' = {
  name: 'storageAccount'
  params: {
    location: location
    tags: tags
    name: storageAccountName
    containers: [
      {
        name: 'default'
      }
      {
        name: storageContainerName
      }
    ]
    files: [
      {
        name: 'default'
      }
    ]
    queues: [
      {
        name: 'default'
      }
    ]
    tables: [
      {
        name: 'default'
      }
    ]
    corsRules: [
      {
        allowedOrigins: [
          'https://mlworkspace.azure.ai'
          'https://ml.azure.com'
          'https://*.ml.azure.com'
          'https://ai.azure.com'
          'https://*.ai.azure.com'
          'https://mlworkspacecanary.azure.ai'
          'https://mlworkspace.azureml-test.net'
        ]
        allowedMethods: [
          'GET'
          'HEAD'
          'POST'
          'PUT'
          'DELETE'
          'OPTIONS'
          'PATCH'
        ]
        maxAgeInSeconds: 1800
        exposedHeaders: [
          '*'
        ]
        allowedHeaders: [
          '*'
        ]
      }
    ]
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      enabled: false
    }
    shareDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

module logAnalytics '../monitor/loganalytics.bicep' =
  if (!empty(logAnalyticsName)) {
    name: 'logAnalytics'
    params: {
      location: location
      tags: tags
      name: logAnalyticsName
    }
  }

module appInsights '../monitor/applicationinsights.bicep' =
  if (!empty(appInsightsName) && !empty(logAnalyticsName)) {
    name: 'appInsights'
    params: {
      location: location
      tags: tags
      name: appInsightsName
      logAnalyticsWorkspaceId: !empty(logAnalyticsName) ? logAnalytics.outputs.id : ''
    }
  }

module containerRegistry '../host/container-registry.bicep' =
  if (!empty(containerRegistryName)) {
    name: 'containerRegistry'
    params: {
      location: location
      tags: tags
      name: containerRegistryName
    }
  }

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(openAiResourceGroupName)) {
  scope: subscription()
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup().name
}

module aiServices '../ai/aiservices.bicep' = {
  name: 'aiServices'
  scope: openAiResourceGroup
  params: {
    location: !empty(openAiLocation) ? openAiLocation : location
    tags: tags
    name: openAiName
    kind: 'OpenAI'
    deployments: openAiModelDeployments
  }
}

resource searchResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(searchResourceGroupName)) {
  scope: subscription()
  name: !empty(searchResourceGroupName) ? searchResourceGroupName : resourceGroup().name
}

module search '../search/search-services.bicep' =
  if (!empty(searchName)) {
    name: 'search'
    scope: searchResourceGroup
    params: {
      location: !empty(searchLocation) ? searchLocation : location
      tags: tags
      name: searchName
      semanticSearch: searchSemanticSku
      sku: {
        name: searchSku
      }
      authOptions: empty(searchAuthOptions) ? null : searchAuthOptions
    }
  }

output keyVaultId string = keyVault.outputs.id
output keyVaultName string = keyVault.outputs.name
output keyVaultEndpoint string = keyVault.outputs.endpoint

output storageAccountId string = storageAccount.outputs.id
output storageAccountName string = storageAccount.outputs.name
output storageAccountBlobUrl string = storageAccount.outputs.blobEndpoint

output containerRegistryId string = !empty(containerRegistryName) ? containerRegistry.outputs.id : ''
output containerRegistryName string = !empty(containerRegistryName) ? containerRegistry.outputs.name : ''
output containerRegistryEndpoint string = !empty(containerRegistryName) ? containerRegistry.outputs.loginServer : ''

output appInsightsId string = !empty(appInsightsName) ? appInsights.outputs.id : ''
output appInsightsName string = !empty(appInsightsName) ? appInsights.outputs.name : ''
output logAnalyticsWorkspaceId string = !empty(logAnalyticsName) ? logAnalytics.outputs.id : ''
output logAnalyticsWorkspaceName string = !empty(logAnalyticsName) ? logAnalytics.outputs.name : ''

output openAiId string = aiServices.outputs.id
output openAiName string = aiServices.outputs.name
output openAiEndpoint string = aiServices.outputs.endpoints['OpenAI Language Model Instance API']

output searchId string = !empty(searchName) ? search.outputs.id : ''
output searchName string = !empty(searchName) ? search.outputs.name : ''
output searchEndpoint string = !empty(searchName) ? search.outputs.endpoint : ''
output searchPrincipalId string = !empty(searchName) ? search.outputs.principalId : ''
