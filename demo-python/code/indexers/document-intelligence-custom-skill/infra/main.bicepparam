using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'env_name')

param location = readEnvironmentVariable('AZURE_LOCATION', 'location')

param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', 'principal_id')

param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', 'rg-${environmentName}')

param searchServiceLocation = readEnvironmentVariable('AZURE_SEARCH_SERVICE_LOCATION', location)

param searchServiceName = readEnvironmentVariable('AZURE_SEARCH_SERVICE', '')

param searchServiceResourceGroupName = readEnvironmentVariable('AZURE_SEARCH_SERVICE_RESOURCE_GROUP', '')

param searchServiceSkuName = readEnvironmentVariable('AZURE_SEARCH_SERVICE_SKU', 'standard')

param semanticSearchSkuName = readEnvironmentVariable('AZURE_SEARCH_SEMANTIC_SEARCH_SKU', 'free')

param storageLocation = readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_LOCATION', '')

param apiServiceLocation =  readEnvironmentVariable('AZURE_API_SERVICE_LOCATION', '')

param apiServiceName =  readEnvironmentVariable('AZURE_API_SERVICE', '')

param apiServiceResourceGroupName =  readEnvironmentVariable('AZURE_API_SERVICE_RESOURCE_GROUP', '')

param appServicePlanName =  readEnvironmentVariable('AZURE_APP_SERVICE_PLAN', '')

param documentIntelligenceAccountName =  readEnvironmentVariable('AZURE_DOCUMENTINTELLIGENCE', '')

param storageAccountName =  readEnvironmentVariable('AZURE_STORAGE_ACCOUNT', '')

param storageResourceGroupName =  readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_RESOURCE_GROUP', '')

param applicationInsightsName =  readEnvironmentVariable('AZURE_APPINSIGHTS', '')

param documentIntelligenceLocation =  readEnvironmentVariable('AZURE_DOCUMENTINTELLIGENCE_LOCATION', '')

param documentIntelligenceResourceGroupName =  readEnvironmentVariable('AZURE_DOCUMENTINTELLIGENCE_RESOURCE_GROUP', '')

param logAnalyticsName =  readEnvironmentVariable('AZURE_LOG_ANALYTICS', '')

param openAiAccountName =  readEnvironmentVariable('AZURE_OPENAI_ACCOUNT', '')

param openAiEmbeddingDeploymentCapacity =  int(readEnvironmentVariable('AZURE_OPENAI_EMB_DEPLOYMENT_CAPACITY', '100'))

param openAiEmbeddingDeploymentName =  readEnvironmentVariable('AZURE_OPENAI_EMB_DEPLOYMENT', 'text-embedding-3-large')

param openAiEmbeddingModelName =  readEnvironmentVariable('AZURE_OPENAI_EMB_MODEL', 'text-embedding-3-large')

param openAiEmbeddingModelVersion =  readEnvironmentVariable('AZURE_OPENAI_EMB_MODEL_VERSION', '1')

param openAiLocation =  readEnvironmentVariable('AZURE_OPENAI_LOCATION', '')

param openAiResourceGroupName =  readEnvironmentVariable('AZURE_OPENAI_RESOURCE_GROUP', '')
