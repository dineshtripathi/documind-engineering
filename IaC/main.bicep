targetScope = 'resourceGroup'

@description('Location, e.g., westeurope or uksouth')
param location string = resourceGroup().location

@description('AIServices (Foundry) account name (globally unique subdomain)')
param aiName string

@description('Default Project name to create under AIServices')
param projectName string = 'documind-dev'

@description('Key Vault name (globally unique within tenant)')
param keyVaultName string

@description('Azure OpenAI (kind=OpenAI) account name (custom subdomain)')
param aoaiName string

@description('Azure AI Vision account name')
param visionName string

@description('Azure AI Search service name')
param searchName string

@description('Azure AI Search SKU')
@allowed([
  'basic'
  'standard'
  'standard2'
  'standard3'
  'storage_optimized_l1'
  'storage_optimized_l2'
])
param searchSku string = 'basic'

@description('Enable Defender for AI on AIServices')
@allowed(['Enabled','Disabled'])
param defenderForAI string = 'Disabled'

@description('Public network access for AIServices')
@allowed(['Enabled','Disabled'])
param publicNetworkAccess string = 'Enabled'

// -----------------------
// Key Vault (RBAC)
// -----------------------
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enablePurgeProtection: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
  tags: { app: 'documind', env: 'dev' }
}

// ---------------------------------------
// Azure OpenAI (classic Cognitive Services)
// ---------------------------------------
resource aoai 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: aoaiName
  location: location
  sku: { name: 'S0' }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: aoaiName
    publicNetworkAccess: 'Enabled'
  }
  tags: { app: 'documind', service: 'openai', env: 'dev' }
}

// ---------------------------
// Azure AI Vision (ComputerVision)
// ---------------------------
resource vision 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: visionName
  location: location
  sku: { name: 'S1' }
  kind: 'ComputerVision'
  properties: {
    publicNetworkAccess: 'Enabled'
  }
  tags: { app: 'documind', service: 'vision', env: 'dev' }
}

// ---------------------------
// Azure AI Search
// ---------------------------
resource search 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchName
  location: location
  sku: { name: searchSku }
  properties: {
    hostingMode: 'default'
    partitionCount: 1
    replicaCount: 1
    publicNetworkAccess: 'enabled'
  }
  tags: { app: 'documind', service: 'ai-search', env: 'dev' }
}

// ---------------------------------------
// Azure AI (AIServices) + Project (Foundry-aligned)
// ---------------------------------------
resource ai 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: aiName
    publicNetworkAccess: publicNetworkAccess
    allowProjectManagement: true
    defaultProject: projectName
    associatedProjects: [ projectName ]
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    apiProperties: {}
  }
  tags: { app: 'documind', env: 'dev', service: 'aiservices' }
}

resource defender 'Microsoft.CognitiveServices/accounts/defenderForAISettings@2025-06-01' = {
  parent: ai
  name: 'Default'
  properties: { state: defenderForAI }
}

// Default RAI policy — tweak later per org stance
resource raiDefault 'Microsoft.CognitiveServices/accounts/raiPolicies@2025-06-01' = {
  parent: ai
  name: 'Microsoft.DefaultV2'
  properties: {
    mode: 'Blocking'
    contentFilters: [
      { name: 'Hate',     severityThreshold:'Medium', blocking:true, enabled:true, source:'Prompt' }
      { name: 'Hate',     severityThreshold:'Medium', blocking:true, enabled:true, source:'Completion' }
      { name: 'Sexual',   severityThreshold:'Medium', blocking:true, enabled:true, source:'Prompt' }
      { name: 'Sexual',   severityThreshold:'Medium', blocking:true, enabled:true, source:'Completion' }
      { name: 'Violence', severityThreshold:'Medium', blocking:true, enabled:true, source:'Prompt' }
      { name: 'Violence', severityThreshold:'Medium', blocking:true, enabled:true, source:'Completion' }
      { name: 'Selfharm', severityThreshold:'Medium', blocking:true, enabled:true, source:'Prompt' }
      { name: 'Selfharm', severityThreshold:'Medium', blocking:true, enabled:true, source:'Completion' }
      { name: 'Jailbreak', blocking:true, enabled:true, source:'Prompt' }
      { name: 'Protected Material Text', blocking:true, enabled:true, source:'Completion' }
      { name: 'Protected Material Code', blocking:false, enabled:true, source:'Completion' }
    ]
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: ai
  name: projectName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    displayName: projectName
    description: 'DocuMind default project'
  }
  tags: { app: 'documind', env: 'dev' }
}

// ---------------------------
// Outputs (symbolic references)
// ---------------------------
output keyVaultNameOut string = kv.name

output aoaiEndpoint string = 'https://${aoai.name}.openai.azure.com/'
output aoaiResourceId string = aoai.id

output visionEndpoint string = vision.properties.endpoint
output visionResourceId string = vision.id

output searchEndpoint string = 'https://${search.name}.search.windows.net'
output searchResourceId string = search.id

output aiId string = ai.id
output aiEndpoint string = 'https://${ai.name}.services.ai.azure.com/'
output projectId string = project.id
