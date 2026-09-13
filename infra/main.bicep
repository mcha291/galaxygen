// galaxygen on Azure Container Apps: one registry, one environment, one app.
//
// Deployed twice by infra/deploy.ps1: first with deployApp=false (registry and
// the pull identity exist, so an image can be built into the registry), then
// with deployApp=true and the image tag that build produced.

@description('Short lowercase name used to derive every resource name.')
@minLength(3)
@maxLength(16)
param name string = 'galaxygen'

param location string = resourceGroup().location

@description('False on the first pass: create the registry only.')
param deployApp bool = true

@description('Image tag in the registry, e.g. 45460b7.')
param imageTag string = 'latest'

@description('Replicas kept warm; 1 avoids a cold start on the first visitor.')
@minValue(0)
param minReplicas int = 1

@minValue(1)
param maxReplicas int = 3

// Registry names are global and alphanumeric only.
var registryName = '${replace(name, '-', '')}${uniqueString(resourceGroup().id)}'

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: false }
}

// The app pulls with this identity; no registry password exists anywhere.
resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${name}-pull'
  location: location
}

var acrPullRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')

resource pullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, pullIdentity.id, acrPullRole)
  scope: registry
  properties: {
    principalId: pullIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPullRole
  }
}

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = if (deployApp) {
  name: '${name}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = if (deployApp) {
  name: '${name}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        // Same deployApp condition as this resource, so logs exists whenever this runs.
        customerId: logs!.properties.customerId
        sharedKey: logs!.listKeys().primarySharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = if (deployApp) {
  name: name
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${pullIdentity.id}': {} }
  }
  properties: {
    managedEnvironmentId: environment!.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: registry.properties.loginServer
          identity: pullIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'galaxygen'
          image: '${registry.properties.loginServer}/galaxygen:${imageTag}'
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
          probes: [
            {
              // /api is the route table: metadata only, no stage runs (rule D4).
              type: 'Readiness'
              httpGet: { path: '/api', port: 8000 }
              periodSeconds: 10
            }
            {
              type: 'Liveness'
              httpGet: { path: '/api', port: 8000 }
              periodSeconds: 30
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            // Generation is CPU-bound and serialised per replica; add one per few concurrent requests.
            name: 'http'
            http: { metadata: { concurrentRequests: '4' } }
          }
        ]
      }
    }
  }
  dependsOn: [ pullRole ]
}

output registryName string = registry.name
output loginServer string = registry.properties.loginServer
output url string = deployApp ? 'https://${app!.properties.configuration.ingress.fqdn}' : ''
