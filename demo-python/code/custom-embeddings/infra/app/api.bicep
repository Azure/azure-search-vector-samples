param name string
param location string = resourceGroup().location
param tags object = {}

param allowedOrigins array = []
param applicationInsightsName string = ''
param appServicePlanId string
param appSettings object = {}
param serviceName string = 'api'
param storageAccountName string
param alwaysOn bool = false
param minimumElasticInstanceCount int = -1
param scmDoBuildDuringDeployment bool = false

module api '../core/host/functions.bicep' = {
  name: '${serviceName}-functions-python-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    allowedOrigins: allowedOrigins
    alwaysOn: alwaysOn
    appSettings: appSettings
    applicationInsightsName: applicationInsightsName
    appServicePlanId: appServicePlanId
    numberOfWorkers: 1
    minimumElasticInstanceCount: minimumElasticInstanceCount
    runtimeName: 'python'
    runtimeVersion: '3.10'
    storageAccountName: storageAccountName
    scmDoBuildDuringDeployment: scmDoBuildDuringDeployment
  }
}

output SERVICE_API_IDENTITY_PRINCIPAL_ID string = api.outputs.identityPrincipalId
output SERVICE_API_NAME string = api.outputs.name
output SERVICE_API_URI string = api.outputs.uri
output location string = api.outputs.location
output id string = api.outputs.id
