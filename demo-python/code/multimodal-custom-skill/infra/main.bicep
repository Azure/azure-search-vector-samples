targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group the deployed skills are in')
param resourceGroupName string  = ''// Set in main.parameters.json

@description('Display name of Computer Vision API account')
param computerVisionAccountName string = '' // Set in main.parameters.json

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('SKU for Computer Vision API')
@allowed([
  'F0'
  'S1'
])
param computerVisionSkuName string // Set in main.parameters.json

@description('Location for Computer Vision API')
@allowed([
  'eastus'
  'francecentral'
  'koreacentral'
  'northeurope'
  'southeastasia'
  'westeurope'
  'westus'
])
param computerVisionLocation string // Set in main.parameters.json

param computerVisionResourceGroupName string = '' // Set in main.parameters.json

param storageLocation string = '' // Set in main.parameters.json

param storageResourceGroupName string = '' // Set in main.parameters.json

param storageAccountName string = '' // Set in main.parameters.json

param appServicePlanName string = '' // Set in main.parameters.json

param appServicePlanLocation string = '' // Set in main.parameters.json

param appServicePlanResourceGroupName string = '' // Set in main.parameters.json

param keyVaultName string = '' // Set in main.parameters.json

param keyVaultLocation string = '' // Set in main.parameters.json

param keyVaultResourceGroupName string = '' // Set in main.parameters.json

param computerVisionSecretName string = 'computerVisionSecret'

param functionAppName string = '' // Set in main.parameters.json

param logAnalyticsName string = '' // Set in main.parameters.json

param applicationInsightsName string = '' // Set in main.parameters.json

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

resource appServicePlanResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(appServicePlanResourceGroupName)) {
  name: !empty(appServicePlanResourceGroupName) ? appServicePlanResourceGroupName : resourceGroup.name
}

resource storageResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(storageResourceGroupName)) {
  name: !empty(storageResourceGroupName) ? storageResourceGroupName : resourceGroup.name
}

resource computerVisionResourceGroup 'Microsoft.Resources/resourceGroups@2022-09-01' existing = if (!empty(computerVisionResourceGroupName)) {
  name: !empty(computerVisionResourceGroupName) ? computerVisionResourceGroupName : resourceGroup.name
}

resource keyVaultResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(keyVaultResourceGroupName)) {
  name: !empty(keyVaultResourceGroupName) ? keyVaultResourceGroupName : resourceGroup.name
}

// Create an App Service Plan for the custom skill
module appServicePlan './core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: appServicePlanResourceGroup
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: empty(appServicePlanLocation) ? location : appServicePlanLocation
    tags: tags
    sku: {
      name: 'Y1'
      tier: 'Dynamic'
    }
  }
}

// Backing storage for Azure functions
module storage './core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: storageResourceGroup
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    location: empty(storageLocation) ? location : storageLocation
    tags: tags
    allowBlobPublicAccess: true
  }
}

// Monitor application with Azure Monitor
module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: appServicePlanResourceGroup
  params: {
    location: empty(appServicePlanLocation) ? location : appServicePlanLocation
    tags: tags
    logAnalyticsName: !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
  }
}

// Computer vision account for vision embeddings
module computerVision 'core/ai/cognitiveservices.bicep' = {
  name: 'computervision'
  scope: computerVisionResourceGroup
  params: {
    name: !empty(computerVisionAccountName) ? computerVisionAccountName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: empty(computerVisionLocation) ? location : computerVisionLocation
    kind: 'ComputerVision'
    sku: {
      name: computerVisionSkuName
    }
  }
}

// The custom skill
module functionApp 'core/host/functions.bicep' = {
  name: 'image-embedding-skill'
  scope: appServicePlanResourceGroup
  params: {
    name: !empty(functionAppName) ? functionAppName : '${abbrs.webSitesFunctions}image-embedding-api-${resourceToken}'
    location: !empty(appServicePlanLocation) ? appServicePlanLocation : location
    keyVaultName: keyVault.outputs.name
    tags: union(tags, { 'azd-service-name': 'image-embedding-skill' })
    alwaysOn: false
    appSettings: {
      AzureWebJobsFeatureFlags: 'EnableWorkerIndexing'
      COGNITIVE_SERVICES_ENDPOINT: computerVision.outputs.endpoint
      COGNITIVE_SERVICES_API_KEY: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=${computerVisionSecretName})'
    }
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.10'
    storageAccountName: storage.outputs.name
  }
}

// Currently, we only need Key Vault for storing Computer Vision key,
module keyVault 'core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: keyVaultResourceGroup
  params: {
    name: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVaultVaults}${resourceToken}'
    location: !empty(keyVaultLocation) ? keyVaultLocation : location
    principalId: principalId
  }
}

module functionKVAccess 'core/security/keyvault-access.bicep' = {
  name: 'custom-skill-keyvault-access'
  scope: keyVaultResourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    principalId: functionApp.outputs.identityPrincipalId
  }
}

module secrets 'secrets.bicep' = {
  name: 'secrets'
  scope: keyVaultResourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    computerVisionId: computerVision.outputs.id
    computerVisionSecretName: computerVisionSecretName
  }
}

output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_STORAGE_ACCOUNT_ID string = storage.outputs.id
output AZURE_STORAGE_ACCOUNT_LOCATION string = storage.outputs.location
output AZURE_STORAGE_ACCOUNT_RESOURCE_GROUP string = storageResourceGroup.name
output AZURE_STORAGE_ACCOUNT string = storage.outputs.name
output AZURE_STORAGE_ACCOUNT_BLOB_URL string = storage.outputs.primaryBlobEndpoint
output AZURE_APP_SERVICE_PLAN string = appServicePlan.outputs.name
output AZURE_APP_SERVICE_PLAN_LOCATION string = functionApp.outputs.location
output AZURE_APP_SERVICE_PLAN_RESOURCE_GROUP string = appServicePlanResourceGroup.name
output AZURE_FUNCTION_APP_NAME string = functionApp.outputs.name
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_KEY_VAULT_LOCATION string = keyVault.outputs.location
output AZURE_KEY_VAULT_RESOURCE_GROUP string = keyVaultResourceGroup.name
output AZURE_LOG_ANALYTICS string = monitoring.outputs.logAnalyticsWorkspaceName
output AZURE_APPINSIGHTS string = monitoring.outputs.applicationInsightsName

output AZURE_COMPUTERVISION_ACCOUNT_URL string = computerVision.outputs.endpoint

output AZURE_CUSTOM_SKILL_URL string = functionApp.outputs.uri
