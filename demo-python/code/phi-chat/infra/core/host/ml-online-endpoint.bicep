metadata description = 'Creates an Azure Container Registry.'
param name string
param serviceName string = ''
param location string = resourceGroup().location
param tags object = {}
param aiProjectName string
param aiHubName string
param keyVaultName string
param kind string = 'Managed'
param authMode string = 'Key'

resource endpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2023-10-01' = {
  name: name
  location: location
  parent: workspace
  kind: kind
  tags: !empty(serviceName) ? union(tags, { 'azd-service-name': serviceName }) : tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    authMode: authMode
  }
}

var azureMLDataScientist = resourceId('Microsoft.Authorization/roleDefinitions', 'f6c7c914-8db3-469d-8ca1-694a8f32e121')

resource azureMLDataScientistRoleHub 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, resourceGroup().id, aiHubName, name, azureMLDataScientist)
  scope: hubWorkspace
  properties: {
    principalId: endpoint.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: azureMLDataScientist
  }
}

resource azureMLDataScientistRoleWorkspace 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, resourceGroup().id, aiProjectName, name, azureMLDataScientist)
  scope: workspace
  properties: {
    principalId: endpoint.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: azureMLDataScientist
  }
}

var azureMLWorkspaceConnectionSecretsReader = resourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ea01e6af-a1c1-4350-9563-ad00f8c72ec5'
)

module openaiRoleUser '../../core/security/role.bicep' = {
  name: 'openai-role-user'
  params: {
    principalId: endpoint.identity.principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' //Cognitive Services OpenAI User
    principalType:  'ServicePrincipal'
  }
}

resource azureMLWorkspaceConnectionSecretsReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, resourceGroup().id, aiProjectName, name, azureMLWorkspaceConnectionSecretsReader)
  scope: endpoint
  properties: {
    principalId: endpoint.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: azureMLWorkspaceConnectionSecretsReader
  }
}

module keyVaultAccess '../security/keyvault-access.bicep' = {
  name: '${name}-keyvault-access'
  params: {
    keyVaultName: keyVaultName
    principalId: endpoint.identity.principalId
  }
}

resource hubWorkspace 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' existing = {
  name: aiHubName
}

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-08-01-preview' existing = {
  name: aiProjectName
}

output scoringEndpoint string = endpoint.properties.scoringUri
output swaggerEndpoint string = endpoint.properties.swaggerUri
output principalId string = endpoint.identity.principalId
output name string = endpoint.name
