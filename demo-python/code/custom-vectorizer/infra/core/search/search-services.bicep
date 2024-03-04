metadata description = 'Creates an Azure AI Search instance.'
param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'standard'
}
param authOptions object = {}
param disableLocalAuth bool = false
@allowed([
  'default'
  'highDensity'
])
param hostingMode string = 'default'
param networkRuleSet object = {
  bypass: 'None'
  ipRules: []
}
param partitionCount int = 1
@allowed([
  'enabled'
  'disabled'
])
param publicNetworkAccess string = 'enabled'
param replicaCount int = 1
@allowed([
  'disabled'
  'free'
  'standard'
])
param semanticSearch string = 'disabled'
param identity object

resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: name
  location: location
  tags: tags
  identity: identity
  properties: {
    authOptions: authOptions
    disableLocalAuth: disableLocalAuth
    hostingMode: hostingMode
    networkRuleSet: networkRuleSet
    partitionCount: partitionCount
    publicNetworkAccess: publicNetworkAccess
    replicaCount: replicaCount
    semanticSearch: semanticSearch
  }
  sku: sku
}

output id string = search.id
output endpoint string = 'https://${name}.search.windows.net/'
output name string = search.name
output location string = search.location
output principalId string = search.identity.principalId
