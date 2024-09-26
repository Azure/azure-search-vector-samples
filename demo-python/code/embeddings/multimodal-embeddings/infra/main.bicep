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

param aiServicesAccountName string = '' // Set in main.parameters.json

param aiServicesSkuName string // Set in main.parameters.json

@description('Location for AI Services Account')
@allowed([
  'eastus'
  'francecentral'
  'koreacentral'
  'northeurope'
  'southeastasia'
  'westeurope'
  'westus'
])
param aiServicesLocation string // Set in main.parameters.json

param aiServicesResourceGroupName string = '' // Set in main.parameters.json

param storageLocation string = '' // Set in main.parameters.json

param storageResourceGroupName string = '' // Set in main.parameters.json

param storageAccountName string = '' // Set in main.parameters.json

param storageContainerName string = 'content'

param searchServiceLocation string = '' // Set in main.parameters.json

param searchServiceResourceGroupName string = '' // Set in main.parameters.json

param searchServiceName string = '' // Set in main.parameters.json

@allowed([ 'basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2' ])
param searchServiceSkuName string // Set in main.parameters.json

param searchServiceSemanticRanker string // Set in main.parameters.json

param searchIndexName string // Set in main.parameters.json

param openAiAccountName string = ''// Set in main.parameters.json

param openAiLocation string = ''// Set in main.parameters.json

param openAiChatGptDeploymentName string = ''

param openAiChatGptModelName string = ''

param openAiChatGptDeploymentCapacity string = ''

param openAiChatGptModelVersion string = ''

param openAiResourceGroupName string = '' // Set in main.parameters.json

param appServicePlanName string = ''// Set in main.parameters.json

param apiServiceName string = ''// Set in main.parameters.json

param apiServiceLocation string = ''// Set in main.parameters.json

param apiServiceResourceGroupName string = ''// Set in main.parameters.json


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

resource aiServicesResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(aiServicesResourceGroupName)) {
  name: !empty(aiServicesResourceGroupName) ? aiServicesResourceGroupName : resourceGroup.name
}

resource searchServiceResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(searchServiceResourceGroupName)) {
  name: !empty(searchServiceResourceGroupName) ? searchServiceResourceGroupName : resourceGroup.name
}

resource apiServiceResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(apiServiceResourceGroupName)) {
  name: !empty(apiServiceResourceGroupName) ? apiServiceResourceGroupName : resourceGroup.name
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

param logAnalyticsName string // Set in main.parameters.json

param applicationInsightsName string // Set in main.parameters.json

var functionAppName = !empty(apiServiceName) ? apiServiceName : '${abbrs.webSitesFunctions}api-${resourceToken}'
// Backing storage for Azure functions backend API and sample data
module storage 'br/public:avm/res/storage/storage-account:0.11.0' = {
  name: 'storage'
  scope: storageResourceGroup
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    location: empty(storageLocation) ? location : storageLocation
    tags: tags
    allowSharedKeyAccess: true
    blobServices: {
      containers: [
        {
          name: functionAppName
        }
      ]
    }
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// Multi-services cognitive services account for vision embeddings
module aiServices 'core/ai/aiservices.bicep' = {
  name: 'aiservices'
  scope: aiServicesResourceGroup
  params: {
    name: !empty(aiServicesAccountName) ? aiServicesAccountName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: empty(aiServicesLocation) ? location : aiServicesLocation
    kind: 'AIServices'
    sku: {
      name: aiServicesSkuName
    }
  }
}

var openAiDeployments = [
  {
    name: openAiChatGptDeploymentName
    model: {
      format: 'OpenAI'
      name: openAiChatGptModelName
      version: openAiChatGptModelVersion
    }
    sku: {
      name: 'Standard'
      capacity: openAiChatGptDeploymentCapacity
    }
  }
]

// Backing OpenAI account for Azure OpenAI
module openAi 'br/public:avm/res/cognitive-services/account:0.5.4' = {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiAccountName) ? openAiAccountName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: empty(openAiLocation) ? location : openAiLocation
    tags: tags
    kind: 'OpenAI'
    customSubDomainName: !empty(openAiAccountName) ? openAiAccountName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    sku: 'S0'
    deployments: openAiDeployments
    disableLocalAuth: true
    restrictOutboundNetworkAccess: false
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

// To use AI Services 
module aiServicesRoleSearch 'core/security/role.bicep' = {
  scope: aiServicesResourceGroup
  name: 'ai-services-role-search'
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

// For captioning custom skill
module openAiRoleFunction 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  scope: apiServiceResourceGroup
  name: 'cognitiveservices-role-function'
  params: {
    principalId: functionApp.outputs.identityPrincipalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'ServicePrincipal'
    resourceId:  openAi.outputs.resourceId
  }
}

// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan 'br/public:avm/res/web/serverfarm:0.2.2' = {
  name: 'appServicePlan'
  scope: apiServiceResourceGroup
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: empty(apiServiceLocation) ? location : apiServiceLocation
    tags: tags
    skuName: 'FC1'
    skuCapacity: 1
    kind: 'Linux'
  }
}

module functionApp 'core/host/functions-flex.bicep' = {
  name: 'api'
  scope: apiServiceResourceGroup
  params: {
    name: functionAppName
    location: location
    tags: union(tags, { 'azd-service-name': 'api' })
    alwaysOn: false
    appSettings: {
      FUNCTIONS_EXTENSION_VERSION: '~4'
      AzureWebJobsStorage__accountName: storage.outputs.name
      AZURE_OPENAI_ENDPOINT: openAi.outputs.endpoint
      AZURE_OPENAI_API_VERSION: '2024-06-01'
    }
    appServicePlanId: appServicePlan.outputs.resourceId
    runtimeName: 'python'
    runtimeVersion: '3.10'
    storageAccountName: storage.outputs.name
    applicationInsightsName: applicationInsights.outputs.name
  }
}

// Monitor application with Azure Monitor
module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.4.0' = {
  name: 'logAnalytics'
  scope: apiServiceResourceGroup
  params: {
    location: location
    tags: tags
    name: !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
  }
}

module applicationInsights 'br/public:avm/res/insights/component:0.3.1' = {
  name: 'appInsights'
  scope: apiServiceResourceGroup
  params: {
    location: location
    tags: tags
    workspaceResourceId: logAnalytics.outputs.resourceId
    name: !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_STORAGE_ACCOUNT_ID string = storage.outputs.resourceId
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
output AZURE_AI_SERVICES_ENDPOINT string = aiServices.outputs.endpoint
output AZURE_STORAGE_SUFFIX string = environment().suffixes.storage
