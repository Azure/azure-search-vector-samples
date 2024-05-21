targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group to deploy resources in')
param resourceGroupName string  = ''// Set in main.parameters.json

param storageAccountName string = '' // Set in main.parameters.json

param storageContainerName string = 'content'

param searchServiceLocation string = '' // Set in main.parameters.json

param searchServiceResourceGroupName string = '' // Set in main.parameters.json

param searchServiceName string = '' // Set in main.parameters.json

@allowed([ 'basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2' ])
param searchServiceSkuName string // Set in main.parameters.json

param searchServiceSemanticRanker string // Set in main.parameters.json

param searchIndexName string // Set in main.parameters.json

param aiHubName string = '' // Set in main.parameters.json

param aiHubLocation string = '' // Set in main.parameters.json

param aiProjectName string = '' // Set in main.parameters.json

param serverlessEndpointName string = '' // Set in main.parameters.json

param serverlessModelId string = '' // Set in main.parameters.json

param serverlessModelVersion string = '' // Set in main.parameters.json

param marketplaceSubscriptionName string = '' // Set in main.parameters.json

param logAnalyticsName string = '' // Set in main.parameters.json

param appInsightsName string  = '' // Set in main.parameters.json

param containerRegistryName string = '' // Set in main.parameters.json

param keyVaultName string = '' // Set in main.parameters.json


// Tags that should be applied to all resources.
// 
// Note that 'azd-service-name' tags should be applied separately to service host resources.
// Example usage:
//   tags: union(tags, { 'azd-service-name': <service name in azure.yaml> })
var tags = {
  'azd-env-name': environmentName
}

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

resource resourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: empty(resourceGroupName) ? '${abbrs.resourcesResourceGroups}${environmentName}' : resourceGroupName
  location: location
  tags: tags
}

module ai 'core/host/ai-environment.bicep' = {
  name: 'ai'
  scope: resourceGroup
  params: {
    location: !empty(aiHubLocation) ? aiHubLocation : location
    tags: tags
    hubName: !empty(aiHubName) ? aiHubName : 'ai-hub-${resourceToken}'
    projectName: !empty(aiProjectName) ? aiProjectName : 'ai-project-${resourceToken}'
    logAnalyticsName: !empty(logAnalyticsName)
      ? logAnalyticsName
      : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    appInsightsName: !empty(appInsightsName) ? appInsightsName : '${abbrs.insightsComponents}${resourceToken}'
    containerRegistryName: !empty(containerRegistryName)
      ? containerRegistryName
      : '${abbrs.containerRegistryRegistries}${resourceToken}'
    keyVaultName: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVaultVaults}${resourceToken}'
    storageAccountName: !empty(storageAccountName)
      ? storageAccountName
      : '${abbrs.storageStorageAccounts}${resourceToken}'
    storageContainerName: storageContainerName
    serverlessEndpointName: !empty(serverlessEndpointName) ? serverlessEndpointName : 'serverless-${resourceToken}'
    marketplaceSubscriptionName: !empty(marketplaceSubscriptionName) ? marketplaceSubscriptionName : 'serverless-${resourceToken}'
    serverlessModelId: serverlessModelId
    serverlessModelVersion: serverlessModelVersion
    searchName: !empty(searchServiceName) ? searchServiceName : 'srch-${resourceToken}'
    searchSku: searchServiceSkuName
    searchSemanticSku: searchServiceSemanticRanker
    searchAuthOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http403'
      }
    }
    searchLocation: searchServiceLocation
    searchResourceGroupName: searchServiceResourceGroupName
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name
output AZURE_SEARCH_SERVICE string = ai.outputs.searchName
output AZURE_STORAGE_ACCOUNT_ID string = ai.outputs.storageAccountId
output AZURE_STORAGE_ACCOUNT string = ai.outputs.storageAccountName
output AZURE_STORAGE_ACCOUNT_BLOB_URL string = ai.outputs.storageAccountBlobUrl
output AZURE_STORAGE_CONTAINER string = storageContainerName
output AZURE_SEARCH_INDEX string = searchIndexName
output AZURE_SEARCH_SKILLSET string = '${searchIndexName}-skillset'
output AZURE_SEARCH_DATASOURCE string = '${searchIndexName}-datasource'
output AZURE_SEARCH_INDEXER string = '${searchIndexName}-indexer'
output AZURE_SEARCH_ENDPOINT string = ai.outputs.searchEndpoint
output AZUREAI_HUB_NAME string = ai.outputs.hubName
output AZUREAI_PROJECT_NAME string = ai.outputs.projectName
output AZUREAI_SERVERLESS_MODEL string = serverlessModelId
output AZUREAI_SERVERLESS_ENDPOINT_NAME string = ai.outputs.endpointName
