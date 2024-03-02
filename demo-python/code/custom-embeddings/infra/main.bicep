targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Name of the resource group the search service and deployed embedding model are in')
param resourceGroupName string  = ''// Set in main.parameters.json

// Free tier does not support managed identity which is used in the sample
@allowed([ 'basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2' ])
param searchServiceSkuName string // Set in main.parameters.json

param searchServiceLocation string = '' // set in main.parameters.json

param searchServiceName string = '' // Set in main.parameters.json

param searchServiceResourceGroupName string = ''// Set in main.parameters.json

param semanticSearchSkuName string = '' // Set in main.parameters.json

param storageLocation string = '' // Set in main.parameters.json

param storageResourceGroupName string = '' // Set in main.parameters.json

param storageAccountName string = '' // Set in main.parameters.json

param appServicePlanName string = '' // Set in main.parameters.json

param apiServiceName string = '' // Set in main.parameters.json

param apiServiceLocation string = '' // Set in main.parameters.json

param apiServiceResourceGroupName string = '' // Set in main.parameters.json

param logAnalyticsName string = '' // Set in main.parameters.json

param applicationInsightsName string = '' // Set in main.parameters.json

param sentenceTransformersTextEmbeddingModel string = '' // Set in main.parameters.json

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

resource searchServiceResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(searchServiceResourceGroupName)) {
  name: !empty(searchServiceResourceGroupName) ? searchServiceResourceGroupName : resourceGroup.name
}

resource apiServiceResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(apiServiceResourceGroupName)) {
  name: !empty(apiServiceResourceGroupName) ? apiServiceResourceGroupName : resourceGroup.name
}

resource storageResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(storageResourceGroupName)) {
  name: !empty(storageResourceGroupName) ? storageResourceGroupName : resourceGroup.name
}

module searchService 'core/search/search-services.bicep' = {
  name: 'search-service'
  scope: searchServiceResourceGroup
  params: {
    name: empty(searchServiceName) ? '${abbrs.searchSearchServices}${resourceToken}' : searchServiceName
    location: empty(searchServiceLocation) ? location : searchServiceLocation
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'  
      }
    }
    identity: {
      type: 'SystemAssigned'
    }
    sku: {
      name: searchServiceSkuName
    }
    semanticSearch: semanticSearchSkuName
    tags: tags
  }
}

// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan './core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: apiServiceResourceGroup
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: empty(apiServiceLocation) ? location : apiServiceLocation
    tags: tags
    sku: {
      name: 'EP1'
      tier: 'ElasticPremium'
      family: 'EP'
    }
    kind: 'elastic'
    properties: {
      maximumElasticWorkerCount: 2
      reserved: true // This property determines if the app service plan is Linux https://github.com/Azure/bicep/discussions/7029
    }
  }
}

// Backing storage for Azure functions backend API and sample data
module storage './core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: storageResourceGroup
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    location: empty(storageLocation) ? location : storageLocation
    tags: tags
  }
}

// Storage contributor role to upload sample data
module storageContribRoleUser 'core/security/role.bicep' = {
  scope: storageResourceGroup
  name: 'storage-contribrole-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: 'User'
  }
}

// Storage blob reader role for indexer
module storageReaderRoleSearchService 'core/security/role.bicep' = {
  scope: storageResourceGroup
  name: 'storage-readerrole-search'
  params: {
    principalId: searchService.outputs.principalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: 'ServicePrincipal'
  }
}

// Monitor application with Azure Monitor
module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: apiServiceResourceGroup
  params: {
    location: location
    tags: tags
    logAnalyticsName: !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
  }
}

// The application backend
module api './app/api.bicep' = {
  name: 'api'
  scope: apiServiceResourceGroup
  params: {
    name: !empty(apiServiceName) ? apiServiceName : '${abbrs.webSitesFunctions}api-${resourceToken}'
    location: location
    tags: tags
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    appServicePlanId: appServicePlan.outputs.id
    storageAccountName: storage.outputs.name
    alwaysOn: false
    minimumElasticInstanceCount: 1
    scmDoBuildDuringDeployment: true
    appSettings: {
      SENTENCE_TRANSFORMERS_TEXT_EMBEDDING_MODEL: sentenceTransformersTextEmbeddingModel
      AzureWebJobsFeatureFlags: 'EnableWorkerIndexing'
    }
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name
output AZURE_SEARCH_SERVICE string = searchService.outputs.name
output AZURE_SEARCH_SERVICE_RESOURCE_GROUP string = searchServiceResourceGroup.name
output AZURE_SEARCH_SERVICE_LOCATION string = searchService.outputs.location

output AZURE_STORAGE_ACCOUNT_ID string = storage.outputs.id
output AZURE_STORAGE_ACCOUNT_LOCATION string = storage.outputs.location
output AZURE_STORAGE_ACCOUNT_RESOURCE_GROUP string = storageResourceGroup.name
output AZURE_STORAGE_ACCOUNT string = storage.outputs.name
output AZURE_STORAGE_ACCOUNT_BLOB_URL string = storage.outputs.primaryBlobEndpoint
output AZURE_APP_SERVICE_PLAN string = appServicePlan.outputs.name
output AZURE_API_SERVICE string = api.outputs.SERVICE_API_NAME
output AZURE_API_SERVICE_LOCATION string = api.outputs.location
output AZURE_API_SERVICE_RESOURCE_GROUP string = apiServiceResourceGroup.name
output AZURE_LOG_ANALYTICS string = monitoring.outputs.logAnalyticsWorkspaceName
output AZURE_APPINSIGHTS string = monitoring.outputs.applicationInsightsName

output AZURE_FUNCTION_URL string = api.outputs.SERVICE_API_URI
