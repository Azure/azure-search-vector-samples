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

param openAiSkuName string // Set in main.parameters.json

param openAiLocation string = '' // Set in main.parameters.json

param openAiResourceGroupName string = '' // Set in main.parameters.json

param openAiEmbeddingModelName string // Set in main.parameters.json

param openAiEmbeddingDeploymentName string // Set in main.parameters.json


param openAiEmbeddingDeploymentCapacity int // Set in main.parameters.json

param openAiEmbeddingModelDimensions int // Set in main.parameters.json


param storageLocation string = '' // Set in main.parameters.json

param storageResourceGroupName string = '' // Set in main.parameters.json

param storageAccountName string = '' // Set in main.parameters.json

param storageContainerName string = 'content'

param storageSkuName string // Set in main.parameters.json

param searchServiceLocation string = '' // Set in main.parameters.json

param searchServiceResourceGroupName string = '' // Set in main.parameters.json

param searchServiceName string = '' // Set in main.parameters.json

@allowed([ 'basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2' ])
param searchServiceSkuName string // Set in main.parameters.json

param searchServiceSemanticRanker string // Set in main.parameters.json

param searchIndexName string // Set in main.parameters.json

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

resource storageResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(storageResourceGroupName)) {
  name: !empty(storageResourceGroupName) ? storageResourceGroupName : resourceGroup.name
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

resource searchServiceResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(searchServiceResourceGroupName)) {
  name: !empty(searchServiceResourceGroupName) ? searchServiceResourceGroupName : resourceGroup.name
}

// Storage for documents for text embeddings
module storage './core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: storageResourceGroup
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    location: empty(storageLocation) ? location : storageLocation
    tags: tags
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    containers: [
      {
        name: storageContainerName
        publicAccess: 'None'
      }
    ]
    sku: {
      name: storageSkuName
    }
  }
}

// Azure OpenAI account for text embeddings
module openAi 'core/ai/aiservices.bicep' = {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiAccountName) ? openAiAccountName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: empty(openAiLocation) ? location : openAiLocation
    kind: 'OpenAI'
    sku: {
      name: openAiSkuName
    }
    deployments: [
      {
        name: openAiEmbeddingDeploymentName
        model: {
          format: 'OpenAI'
          name: openAiEmbeddingModelName
          version: 1
        }
        sku: {
          name: 'Standard'
          capacity: openAiEmbeddingDeploymentCapacity
        }
      }
    ]
  }
}

// Search service for indexer
module search 'core/search/search-services.bicep' = {
  name: 'search'
  scope: searchServiceResourceGroup
  params: {
    name: !empty(searchServiceName) ? searchServiceName : '${abbrs.searchSearchServices}${resourceToken}'
    location: empty(searchServiceLocation) ? location : searchServiceLocation
    sku: {
      name: searchServiceSkuName
    }
    semanticSearch: searchServiceSemanticRanker
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http403'
      }
    }
  }
}

// Blob contributor role (Upload sample images)
module storageContribRoleUser 'core/security/role.bicep' = {
  scope: storageResourceGroup
  name: 'storage-contrib-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: 'User'
  }
}

// To use OpenAI embeddings 
module openAIRoleSearch 'core/security/role.bicep' = {
  scope: openAiResourceGroup
  name: 'openai-role-search'
  params: {
    principalId: search.outputs.principalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908'
    principalType: 'ServicePrincipal'
  }
}

// To read blobs in the indexer
module storageBlobDataReaderRole 'core/security/role.bicep' = {
  scope: storageResourceGroup
  name: 'storage-role-search'
  params: {
    principalId: search.outputs.principalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: 'ServicePrincipal'
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_STORAGE_ACCOUNT_ID string = storage.outputs.id
output AZURE_STORAGE_ACCOUNT_LOCATION string = storage.outputs.location
output AZURE_STORAGE_ACCOUNT_RESOURCE_GROUP string = storageResourceGroup.name
output AZURE_STORAGE_ACCOUNT string = storage.outputs.name
output AZURE_STORAGE_ACCOUNT_BLOB_URL string = storage.outputs.primaryBlobEndpoint
output AZURE_STORAGE_CONTAINER string = storageContainerName
output AZURE_SEARCH_INDEX string = searchIndexName
output AZURE_SEARCH_SKILLSET string = '${searchIndexName}-skillset'
output AZURE_SEARCH_DATASOURCE string = '${searchIndexName}-datasource'
output AZURE_SEARCH_INDEXER string = '${searchIndexName}-indexer'
output AZURE_SEARCH_ENDPOINT string = search.outputs.endpoint
output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_EMB_MODEL_NAME string = openAiEmbeddingModelName
output AZURE_OPENAI_EMB_MODEL_DIMENSIONS int = openAiEmbeddingModelDimensions
output AZURE_OPENAI_EMB_DEPLOYMENT string = openAiEmbeddingDeploymentName
output AZURE_OPENAI_EMB_DEPLOYMENT_CAPACITY int = openAiEmbeddingDeploymentCapacity
