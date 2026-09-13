// galaxygen on Azure Container Apps, sized to stay inside the free grants.
//
// Consumption plan, free each month per subscription: 180,000 vCPU-seconds,
// 360,000 GiB-seconds and 2 million requests. At 0.5 vCPU / 1 GiB that is 100
// hours of a running replica, and a replica only runs while there is traffic:
// minReplicas 0 scales to zero between visits, maxReplicas 1 caps the burn.
// Measured locally: a full galaxy with the two-galaxy cache peaks at ~230 MB.
//
// No Azure Container Registry (its cheapest tier is billed daily): the image is
// public on GitHub Container Registry, built by .github/workflows/image.yml.
// Log Analytics keeps its first 5 GB a month free; the daily cap holds it there.

@description('Short lowercase name used to derive every resource name.')
@minLength(3)
@maxLength(16)
param name string = 'galaxygen'

param location string = resourceGroup().location

@description('Full image reference, e.g. ghcr.io/mcha291/galaxygen:add6034.')
param image string

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${name}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    workspaceCapping: { dailyQuotaGb: json('0.1') }
  }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${name}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'galaxygen'
          image: image
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              // /api is the route table: metadata only, no stage runs (rule D4).
              type: 'Readiness'
              httpGet: { path: '/api', port: 8000 }
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: { metadata: { concurrentRequests: '10' } }
          }
        ]
      }
    }
  }
}

output url string = 'https://${app.properties.configuration.ingress.fqdn}'
