@description('Azure region for the lab resources.')
param location string = 'swedencentral'

@description('UTC deployment date used to generate a stable daily suffix.')
param deploymentDate string = utcNow('yyyyMMdd')

@description('Unique daily suffix used in globally unique resource names.')
param suffix string = take(uniqueString(resourceGroup().id, deploymentDate), 8)

param foundryResourceName string = 'foundry-hack-${suffix}'
param projectName string = 'callcenter-project'
param modelDeploymentName string = 'gpt-5.4'
param modelName string = 'gpt-5.4'
param modelVersion string = '2026-03-05'
param logAnalyticsName string = 'foundry-hack-logs-${suffix}'
param appInsightsName string = 'foundry-hack-insights-${suffix}'
param searchServiceName string = 'search-hack-${suffix}'

@allowed([
  'basic'
  'standard'
])
param searchSkuName string = 'basic'

param ragStorageAccountName string = 'stragrag${suffix}'
param ragContainerName string = 'rag-files'
param bingCustomSearchName string = 'bing-custom-hack-${suffix}'

param tags object = {
  environment: 'hack'
}

var searchServiceContributorRoleId = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
var searchIndexDataContributorRoleId = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var cognitiveServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: foundryResourceName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: foundryResourceName
    allowProjectManagement: true
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundry
  name: projectName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: { displayName: projectName }
}

resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  sku: { name: searchSkuName }
  identity: { type: 'SystemAssigned' }
  tags: tags
  properties: {
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    hostingMode: 'default'
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    replicaCount: 1
  }
}

resource foundrySearchServiceContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, foundry.id, searchServiceContributorRoleId)
  scope: searchService
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchServiceContributorRoleId)
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource foundrySearchDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, foundry.id, searchIndexDataContributorRoleId)
  scope: searchService
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchIndexDataContributorRoleId)
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource projectSearchServiceContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, project.id, searchServiceContributorRoleId)
  scope: searchService
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchServiceContributorRoleId)
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource projectSearchDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchService.id, project.id, searchIndexDataContributorRoleId)
  scope: searchService
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchIndexDataContributorRoleId)
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource ragStorageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: ragStorageAccountName
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  identity: { type: 'SystemAssigned' }
  tags: tags
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource ragBlobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: ragStorageAccount
  name: 'default'
}

resource ragContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: ragBlobService
  name: ragContainerName
  properties: {
    publicAccess: 'None'
  }
}

resource foundryRagStorageBlobDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(ragStorageAccount.id, foundry.id, storageBlobDataContributorRoleId)
  scope: ragStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource projectRagStorageBlobDataContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(ragStorageAccount.id, project.id, storageBlobDataContributorRoleId)
  scope: ragStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource bingCustomSearch 'Microsoft.Bing/accounts@2020-06-10' = {
  name: bingCustomSearchName
  location: 'global'
  kind: 'Bing.GroundingCustomSearch'
  sku: { name: 'G2' }
  tags: tags
  properties: {
    statisticsEnabled: false
  }
}

resource bingCustomSearchConfig 'Microsoft.Bing/accounts/customSearchConfigurations@2025-05-01-preview' = {
  parent: bingCustomSearch
  name: 'default'
  properties: {}
}

resource foundryBingGroundingRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(bingCustomSearch.id, foundry.id, cognitiveServicesUserRoleId)
  scope: bingCustomSearch
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource projectBingGroundingRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(bingCustomSearch.id, project.id, cognitiveServicesUserRoleId)
  scope: bingCustomSearch
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Bing keys are the auth mechanism required by the GroundingWithCustomSearch connection category
resource bingCustomSearchConnection 'Microsoft.CognitiveServices/accounts/connections@2025-06-01' = {
  parent: foundry
  name: 'bing-custom-grounding-conn'
  properties: {
    category: 'GroundingWithCustomSearch'
    target: bingCustomSearch.properties.endpoint
    authType: 'ApiKey'
    credentials: { key: bingCustomSearch.listKeys().key1 }
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: bingCustomSearch.id
      Location: 'global'
      type: 'bing_custom_search'
    }
  }
  dependsOn: [
    foundryBingGroundingRole
    projectBingGroundingRole
  ]
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: foundry
  name: modelDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
  dependsOn: [project]
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: { retentionInDays: 30 }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

resource appInsightsConnection 'Microsoft.CognitiveServices/accounts/connections@2025-06-01' = {
  parent: foundry
  name: 'appinsights-conn'
  properties: {
    category: 'AppInsights'
    target: appInsights.id
    authType: 'ApiKey'
    credentials: { key: appInsights.properties.ConnectionString }
    isSharedToAll: true
    metadata: {
      ApiType: 'Azure'
      ResourceId: appInsights.id
    }
  }
}

output subscriptionId string = subscription().id
output resourceGroupName string = resourceGroup().name
output foundryResourceName string = foundry.name
output projectName string = project.name
output foundryEndpoint string = foundry.properties.endpoint
output projectConnectionString string = 'https://${foundry.name}.services.ai.azure.com/api/projects/${project.name}'
output modelDeploymentName string = modelDeployment.name
output searchServiceName string = searchService.name
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'
output searchResourceId string = searchService.id
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output ragStorageAccountName string = ragStorageAccount.name
output ragStorageAccountId string = ragStorageAccount.id
output ragStorageBlobEndpoint string = ragStorageAccount.properties.primaryEndpoints.blob
output ragContainerName string = ragContainer.name
output bingCustomSearchName string = bingCustomSearch.name
output bingCustomSearchResourceId string = bingCustomSearch.id
output bingCustomSearchConfigName string = bingCustomSearchConfig.name
output bingCustomSearchConnectionName string = bingCustomSearchConnection.name
