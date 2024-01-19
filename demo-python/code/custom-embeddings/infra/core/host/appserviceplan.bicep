param name string
param location string = resourceGroup().location
param tags object = {}

param kind string = ''
param sku object
param properties object

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  kind: kind
  properties: properties
}

output id string = appServicePlan.id
output name string = appServicePlan.name
