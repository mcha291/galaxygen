// galaxygen on Azure Container Apps (BUILD_IV Phase W4): two apps in one Consumption environment, sized to stay
// inside the free grants at zero traffic.
//
//   ${name}         the gateway (gateway/Dockerfile): the viewer, the caches, the limits, the share links;
//                   external ingress on 8080
//   ${name}-model   the Python model and its bundles (Dockerfile.model): internal ingress only on 8000, reached
//                   by the gateway alone, so it wakes only when an answer is not already cached (ruling 8)
//
// Both scale 0-1 (ruling 9): the Consumption grant is per subscription each month (180,000 vCPU-seconds,
// 360,000 GiB-seconds, 2 million requests), and a replica bills only while it runs; a warm replica all month
// would cost several times the grant. maxReplicas 1 caps the burn and is what the gateway's limits assume (one
// model computing one request at a time).
//
// The gateway is pinned to the model image's model.hash (modelHash, read by deploy.ps1 from the image's label
// org.galaxygen.model_hash), so a cache hit never wakes the model to ask its hash.
//
// No Azure Container Registry (its cheapest tier is billed daily): the images are public on GitHub Container
// Registry, built by .github/workflows/image.yml. Log Analytics keeps its first 5 GB a month free; the daily cap
// holds it there. Storage (Table for the share links' records, Blob for their answers) bills per GB and per
// operation: at zero traffic, nothing but the few bytes stored.

@description('Short lowercase name every resource name is derived from.')
@minLength(3)
@maxLength(16)
param name string = 'galaxygen'

param location string = resourceGroup().location

@description('The model image, e.g. ghcr.io/mcha291/galaxygen-model:add6034.')
param modelImage string

@description('The gateway image, e.g. ghcr.io/mcha291/galaxygen-gateway:add6034.')
param gatewayImage string

@description('The model image\'s /api/version model.hash (32 hex characters): the gateway\'s pin.')
@minLength(32)
@maxLength(32)
param modelHash string

// Consumption pairs are 0.25 vCPU / 0.5Gi to 2 vCPU / 4Gi in steps of 0.25 vCPU, memory twice the vCPU.
@description('The model\'s vCPU. Measured S75: a seed change with two galaxies cached peaks at 1.2 GB working set, 1.6 GB committed.')
@allowed(['0.25', '0.5', '0.75', '1.0', '1.25', '1.5', '1.75', '2.0'])
param modelCpu string = '1.0'

@allowed(['0.5Gi', '1Gi', '1.5Gi', '2Gi', '2.5Gi', '3Gi', '3.5Gi', '4Gi'])
param modelMemory string = '2Gi'

@allowed(['0.25', '0.5', '0.75', '1.0'])
param gatewayCpu string = '0.5'

@allowed(['0.5Gi', '1Gi', '1.5Gi', '2Gi'])
param gatewayMemory string = '1Gi'

@description('Days a share link\'s stored answer is kept in the results container after it was last written.')
@minValue(1)
param resultsTtlDays int = 30

// At most 24 lowercase letters and digits, unique per resource group.
var storageName = take('${toLower(replace(name, '-', ''))}${uniqueString(resourceGroup().id)}', 24)

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${name}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    workspaceCapping: { dailyQuotaGb: json('0.1') }
  }
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${name}-env'
  location: location
  properties: {
    workloadProfiles: [
      { name: 'Consumption', workloadProfileType: 'Consumption' }
    ]
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

// --- Storage for the share links (BUILD_IV 2c): the records in Table `shares`, their answers in Blob `results` --
resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true // the gateway authenticates with the account's connection string
  }
}

resource tables 'Microsoft.Storage/storageAccounts/tableServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource sharesTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tables
  name: 'shares'
}

resource blobs 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource resultsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobs
  name: 'results'
  properties: { publicAccess: 'None' }
}

// Nothing in the gateway deletes a stored answer (gateway/README.md, left to W4): the account's lifecycle rule does.
// A link's record outlives its answer; a link opened after the TTL recomputes and stores the answer again.
resource lifecycle 'Microsoft.Storage/storageAccounts/managementPolicies@2023-05-01' = {
  parent: storage
  name: 'default'
  properties: {
    policy: {
      rules: [
        {
          enabled: true
          name: 'results-ttl'
          type: 'Lifecycle'
          definition: {
            filters: {
              blobTypes: ['blockBlob']
              prefixMatch: ['${resultsContainer.name}/']
            }
            actions: {
              baseBlob: { delete: { daysAfterModificationGreaterThan: resultsTtlDays } }
            }
          }
        }
      ]
    }
  }
}

var storageConnection = 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${storage.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'

// --- The model: internal ingress only -----------------------------------------------------------------------------
resource model 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${name}-model'
  location: location
  properties: {
    managedEnvironmentId: env.id
    workloadProfileName: 'Consumption'
    configuration: {
      ingress: {
        external: false
        targetPort: 8000
        transport: 'auto'
        allowInsecure: true // the gateway speaks plain http inside the environment
      }
    }
    template: {
      containers: [
        {
          name: 'model'
          image: modelImage
          // --verbose: one log line per request, so the logs show whether a visit reached the model (W4's gate).
          command: ['python', '-m', 'galaxy.api', '--verbose']
          resources: {
            cpu: json(modelCpu)
            memory: modelMemory
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

// --- The gateway: the one public origin ---------------------------------------------------------------------------
resource gateway 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  properties: {
    managedEnvironmentId: env.id
    workloadProfileName: 'Consumption'
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
        allowInsecure: false
      }
      secrets: [
        { name: 'storage-connection', value: storageConnection }
      ]
    }
    template: {
      containers: [
        {
          name: 'gateway'
          image: gatewayImage
          resources: {
            cpu: json(gatewayCpu)
            memory: gatewayMemory
          }
          env: [
            { name: 'Gateway__Model__BaseUrl', value: 'http://${model.properties.configuration.ingress.fqdn}' }
            { name: 'Gateway__Model__ContentHash', value: modelHash }
            // The client is X-Forwarded-For's last entry, the one the ingress wrote (gateway/README.md).
            { name: 'Gateway__Limits__TrustForwardedFor', value: 'true' }
            { name: 'ConnectionStrings__shares', secretRef: 'storage-connection' }
            { name: 'ConnectionStrings__results', secretRef: 'storage-connection' }
          ]
          probes: [
            {
              // /healthz answers 503 on a pin mismatch (the image's model.hash is not the pin), which takes the
              // replica out of rotation by design: a gateway keyed on the wrong hash serves nothing rather than
              // stale answers. The fix is a redeploy with the right modelHash.
              type: 'Readiness'
              httpGet: { path: '/healthz', port: 8080 }
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
            http: { metadata: { concurrentRequests: '50' } }
          }
        ]
      }
    }
  }
}

output url string = 'https://${gateway.properties.configuration.ingress.fqdn}'
output modelFqdn string = model.properties.configuration.ingress.fqdn
output storageAccount string = storage.name
