targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string

@description('Name of the resource group the search service and deployed embedding model are in')
param resourceGroupName string

// Free tier does not support managed identity which is used in the sample
@allowed([ 'basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2' ])
param searchServiceSkuName string // Set in main.parameters.json

param searchServiceLocation string // set in main.parameters.json

param searchServiceName string // Set in main.parameters.json

param searchServiceResourceGroupName string // Set in main.parameters.json

param semanticSearchSkuName string // Set in main.parameters.json

param storageLocation string // Set in main.parameters.json

param storageResourceGroupName string // Set in main.parameters.json

param storageAccountName string // Set in main.parameters.json

param appServicePlanName string // Set in main.parameters.json

param apiServiceName string // Set in main.parameters.json

param apiServiceLocation string // Set in main.parameters.json

param apiServiceResourceGroupName string // Set in main.parameters.json

param documentIntelligenceAccountName string // Set in main.parameters.json

param documentIntelligenceLocation string // Set in main.parameters.json

param documentIntelligenceResourceGroupName string // Set in main.parameters.json

param openAiAccountName string // Set in main.parameters.json

param openAiLocation string // Set in main.parameters.json

param openAiEmbeddingDeploymentName string

param openAiEmbeddingModelName string

param openAiEmbeddingDeploymentCapacity int

param openAiEmbeddingModelVersion string

param openAiEmbeddingModelDimensions string

param openAiResourceGroupName string // Set in main.parameters.json

param logAnalyticsName string // Set in main.parameters.json

param applicationInsightsName string // Set in main.parameters.json

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

resource documentIntelligenceResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(documentIntelligenceResourceGroupName)) {
  name: !empty(documentIntelligenceResourceGroupName) ? documentIntelligenceResourceGroupName : resourceGroup.name
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

module searchService 'br/public:avm/res/search/search-service:0.4.4' = {
  name: 'search-service'
  scope: searchServiceResourceGroup
  params: {
    name: empty(searchServiceName) ? '${abbrs.searchSearchServices}${resourceToken}' : searchServiceName
    location: empty(searchServiceLocation) ? location : searchServiceLocation
    authOptions: null
    disableLocalAuth: true
    managedIdentities: { systemAssigned: true }
    sku: searchServiceSkuName
    semanticSearch: semanticSearchSkuName
    tags: tags
    partitionCount: 1
    replicaCount: 1
    publicNetworkAccess: 'enabled'
  }
}

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


// Backing AI Services account for Document Intelligence
module documentIntelligence 'br/public:avm/res/cognitive-services/account:0.5.4' = {
  name: 'documentintelligence'
  scope: documentIntelligenceResourceGroup
  params: {
    location: empty(documentIntelligenceLocation) ? location : documentIntelligenceLocation
    kind: 'FormRecognizer'
    customSubDomainName: !empty(documentIntelligenceAccountName) ? documentIntelligenceAccountName : '${abbrs.cognitiveServicesDocumentIntelligence}${resourceToken}'
    name: !empty(documentIntelligenceAccountName) ? documentIntelligenceAccountName : '${abbrs.cognitiveServicesDocumentIntelligence}${resourceToken}'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
    restrictOutboundNetworkAccess: false
    sku: 'S0'
    disableLocalAuth: true
  }
}

var openAiDeployments = [
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
  }
}

// Storage contributor role to upload sample data
module storageContribRoleUser 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  scope: resourceGroup
  name: 'storage-contribrole-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: 'User'
    resourceId:  storage.outputs.resourceId
  }
}

// Storage blob reader role for indexer
module storageReaderRoleSearchService 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  scope: storageResourceGroup
  name: 'storage-readerrole-search'
  params: {
    principalId: searchService.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: 'ServicePrincipal'
    resourceId:  storage.outputs.resourceId
  }
}

// For document intelligence custom skill
module cognitiveServicesRoleFunction 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  scope: resourceGroup
  name: 'cognitiveservices-role-function'
  params: {
    principalId: functionApp.outputs.identityPrincipalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908'
    principalType: 'ServicePrincipal'
    resourceId:  documentIntelligence.outputs.resourceId
  }
}

// For function connection to storage
module storageOwnerRoleFunction 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  scope: resourceGroup
  name: 'storage-owner-role-function'
  params: {
    principalId: functionApp.outputs.identityPrincipalId
    roleDefinitionId: 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
    principalType: 'ServicePrincipal'
    resourceId:  storage.outputs.resourceId
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
      AZURE_DOCUMENTINTELLIGENCE_ENDPOINT: documentIntelligence.outputs.endpoint
    }
    appServicePlanId: appServicePlan.outputs.resourceId
    runtimeName: 'python'
    runtimeVersion: '3.10'
    storageAccountName: storage.outputs.name
    applicationInsightsName: applicationInsights.outputs.name
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name
output AZURE_SEARCH_SERVICE string = searchService.outputs.name
output AZURE_SEARCH_SERVICE_RESOURCE_GROUP string = searchServiceResourceGroup.name
output AZURE_SEARCH_SERVICE_LOCATION string = searchService.outputs.location

output AZURE_STORAGE_ACCOUNT_ID string = storage.outputs.resourceId
output AZURE_STORAGE_ACCOUNT_LOCATION string = storage.outputs.location
output AZURE_STORAGE_ACCOUNT_RESOURCE_GROUP string = storageResourceGroup.name
output AZURE_STORAGE_ACCOUNT string = storage.outputs.name
output AZURE_STORAGE_ACCOUNT_BLOB_URL string = storage.outputs.primaryBlobEndpoint
output AZURE_STORAGE_SUFFIX string = environment().suffixes.storage
output AZURE_APP_SERVICE_PLAN string = appServicePlan.outputs.name
output AZURE_API_SERVICE string = functionApp.outputs.name
output AZURE_API_SERVICE_LOCATION string = location
output AZURE_API_SERVICE_RESOURCE_GROUP string = apiServiceResourceGroup.name
output AZURE_LOG_ANALYTICS string = logAnalytics.outputs.location
output AZURE_APPINSIGHTS string = applicationInsights.outputs.name
output AZURE_OPENAI_LOCATION string = openAi.outputs.location
output AZURE_OPENAI_ACCOUNT string = openAi.outputs.name
output AZURE_OPENAI_RESOURCE_GROUP string = openAi.outputs.resourceGroupName
output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_EMB_DEPLOYMENT string = openAiEmbeddingDeploymentName
output AZURE_OPENAI_EMB_MODEL string = openAiEmbeddingModelName
output AZURE_OPENAI_EMB_MODEL_DIMENSIONS string = openAiEmbeddingModelDimensions

output AZURE_FUNCTION_URL string = functionApp.outputs.uri
