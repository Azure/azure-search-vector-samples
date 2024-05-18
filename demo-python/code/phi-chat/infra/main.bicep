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

@description('Id of the user or app to assign application roles')
param principalId string = ''

param openAiAccountName string = '' // Set in main.parameters.json

param openAiResourceGroupName string = '' // Set in main.parameters.json

param openAiLocation string = '' // Set in main.parameters.json

param openAiEmbeddingModelName string // Set in main.parameters.json

param openAiEmbeddingDeploymentName string // Set in main.parameters.json

param openAiEmbeddingDeploymentCapacity int // Set in main.parameters.json

param openAiEmbeddingModelVersion string // Set in main.parameters.json

param openAiEmbeddingModelDimensions int // Set in main.parameters.json

param enableGpt35Turbo bool // Set in main.parameters.json

param openAiGpt35TurboDeploymentName string // Set in main.parameters.json

param openAiGpt35TurboVersion string // Set in main.parameters.json

param openAiGpt35TurboCapacity int // Set in main.parameters.json

param enableGpt4 bool // Set in main.parameters.json

param openAiGpt4DeploymentName string // Set in main.parameters.json

param openAiGpt4Version string // set in main.parameters.json

param openAiGpt4Capacity int // Set in main.parameters.json

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

param aiProjectName string = '' // Set in main.parameters.json

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

var openAiModelDeployments = concat(
  [
    {
      name: openAiEmbeddingDeploymentName
      model: {
        format: 'OpenAI'
        name: openAiEmbeddingModelName
        version: openAiEmbeddingModelVersion
      }
      sku: {
        name: 'Standard'
        capacity: openAiEmbeddingDeploymentCapacity
      }
    }
  ],
  enableGpt35Turbo ? [ {
    name: openAiGpt35TurboDeploymentName
    model: {
      format: 'OpenAI'
      name: 'gpt-35-turbo'
      version: openAiGpt35TurboVersion
    }
    sku: {
      name: 'Standard'
      capacity: openAiGpt35TurboCapacity
    }
  } ] : [],
  enableGpt4 ? [ {
    name: openAiGpt4DeploymentName
    model: {
      format: 'OpenAI'
      name: 'gpt-4'
      version: openAiGpt4Version
    }
    sku: {
      name: 'Standard'
      capacity: openAiGpt4Capacity
    }
  } ] : [] 
)

module ai 'core/host/ai-environment.bicep' = {
  name: 'ai'
  scope: resourceGroup
  params: {
    location: location
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
    openAiName: openAiAccountName
    openAiModelDeployments: openAiModelDeployments
    openAiLocation: openAiLocation
    openAiResourceGroupName: openAiResourceGroupName
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

// Blob contributor role (Upload sample images)
module storageContribRoleUser 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'storage-contrib-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: 'User'
  }
}

// To use OpenAI embeddings 
module openAIRoleSearch 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'openai-role-search'
  params: {
    principalId: ai.outputs.searchPrincipalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908'
    principalType: 'ServicePrincipal'
  }
}

// To read blobs in the indexer
module storageBlobDataReaderRole 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'storage-role-search'
  params: {
    principalId: ai.outputs.searchPrincipalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: 'ServicePrincipal'
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_STORAGE_ACCOUNT_ID string = ai.outputs.storageAccountId
output AZURE_STORAGE_ACCOUNT string = ai.outputs.storageAccountName
output AZURE_STORAGE_ACCOUNT_BLOB_URL string = ai.outputs.storageAccountBlobUrl
output AZURE_STORAGE_CONTAINER string = storageContainerName
output AZURE_SEARCH_INDEX string = searchIndexName
output AZURE_SEARCH_SKILLSET string = '${searchIndexName}-skillset'
output AZURE_SEARCH_DATASOURCE string = '${searchIndexName}-datasource'
output AZURE_SEARCH_INDEXER string = '${searchIndexName}-indexer'
output AZURE_SEARCH_ENDPOINT string = ai.outputs.searchEndpoint
output AZURE_OPENAI_ENDPOINT string = ai.outputs.openAiEndpoint
output AZURE_OPENAI_EMB_MODEL_NAME string = openAiEmbeddingModelName
output AZURE_OPENAI_EMB_MODEL_DIMENSIONS int = openAiEmbeddingModelDimensions
output AZURE_OPENAI_EMB_MODEL_VERSION string = openAiEmbeddingModelVersion
output AZURE_OPENAI_EMB_DEPLOYMENT string = openAiEmbeddingDeploymentName
output AZURE_OPENAI_EMB_DEPLOYMENT_CAPACITY int = openAiEmbeddingDeploymentCapacity
output USE_GPT35TURBO bool = enableGpt35Turbo
output AZURE_OPENAI_GPT35TURBO_DEPLOYMENT_NAME string = openAiGpt35TurboDeploymentName
output AZURE_OPENAI_GPT35TURBO_VERSION string = openAiGpt35TurboVersion
output AZURE_OPENAI_GPT35_TURBO_CAPACITY int = openAiGpt35TurboCapacity
output USE_GPT4TURBO bool = enableGpt4
output AZURE_OPENAI_GPT4_DEPLOYMENT_NAME string = openAiGpt4DeploymentName
output AZURE_OPENAI_GPT4_VERSION string = openAiGpt4Version
output AZURE_OPENAI_GPT4_CAPACITY int = openAiGpt4Capacity
