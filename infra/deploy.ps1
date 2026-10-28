<#
.SYNOPSIS
  Deploy galaxygen to Azure Container Apps: the gateway and the model, from their public images on ghcr.io.

.DESCRIPTION
  .github/workflows/image.yml builds both images on every push, smoke-tests them together and pushes them tagged
  with the short commit; the model image carries the label org.galaxygen.model_hash, the /api/version model.hash it
  publishes. This script only creates or updates the Azure side (infra/main.bicep): it reads that label from
  ghcr.io anonymously and pins the gateway to it, so a cached answer never wakes the model. The label is the truth:
  a -ModelHash that differs from it is refused unless -Force is given. Re-running with a new tag rolls out new
  revisions.

  The environment is recreated (the apps in it and the environment deleted first, said before deleting) only when
  an environment named "<Name>-env" exists without workload profiles - a consumption-only environment, whose type
  the template cannot change - or with -Recreate. A Failed app alone deletes nothing: it needs -Recreate. The Log
  Analytics workspace and the storage account are kept.

  -Preview does everything read-only: the checks (a disabled subscription is a warning), the label, what would be
  deleted, and az deployment group what-if in place of the deployment (skipped, with the reason, when the
  subscription is disabled or the resource group does not exist).

.EXAMPLE
  az login
  ./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag add6034 -Preview
  # The first run of the two-app deployment: today's Failed app and its environment are replaced.
  ./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag add6034 -Recreate
  # Every later run, a new tag rolling out new revisions:
  ./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Tag 1c5500c
#>
param(
  [Parameter(Mandatory)] [string] $ResourceGroup,
  [string] $Location = 'australiaeast',
  [string] $Name = 'galaxygen',
  [string] $Owner = 'mcha291',
  [string] $Tag = $((git rev-parse HEAD).Substring(0, 7)), # the 7 characters image.yml tags with
  [string] $ModelTag = '',
  [string] $GatewayTag = '',
  [string] $ModelHash = '',
  [switch] $Recreate,
  [switch] $Force,
  [switch] $Preview
)

$ErrorActionPreference = 'Stop'
# A fresh winget install is not on this shell's PATH until a new terminal opens.
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
  $env:PATH += ';C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin'
}
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

if (-not $ModelTag) { $ModelTag = $Tag }
if (-not $GatewayTag) { $GatewayTag = $Tag }
$modelRepo = "$Owner/galaxygen-model"
$gatewayRepo = "$Owner/galaxygen-gateway"
$modelImage = "ghcr.io/${modelRepo}:$ModelTag"
$gatewayImage = "ghcr.io/${gatewayRepo}:$GatewayTag"
$ignoreCase = [StringComparison]::OrdinalIgnoreCase

function Invoke-Az {
  $out = & az @args
  if ($LASTEXITCODE -ne 0) { throw "az $($args -join ' ') failed ($LASTEXITCODE)" }
  $out
}

function Test-Same([string] $A, [string] $B) { [string]::Equals($A, $B, $ignoreCase) }

# --- The images on ghcr.io, read anonymously (they are public) ----------------------------------------------------
function Get-RegistryJson([string] $Url, [hashtable] $Headers) {
  $r = Invoke-WebRequest -Uri $Url -Headers $Headers -UseBasicParsing
  $text = $r.Content
  if ($text -is [byte[]]) { $text = [Text.Encoding]::UTF8.GetString($text) }
  $text | ConvertFrom-Json
}

# The image's config for linux/amd64: an index (what buildx pushes, with its attestations) resolved to its manifest.
function Get-ImageConfig([string] $Repo, [string] $Reference) {
  $token = (Get-RegistryJson "https://ghcr.io/token?scope=repository:${Repo}:pull" @{}).token
  $accept = @(
    'application/vnd.oci.image.index.v1+json',
    'application/vnd.docker.distribution.manifest.list.v2+json',
    'application/vnd.oci.image.manifest.v1+json',
    'application/vnd.docker.distribution.manifest.v2+json'
  ) -join ', '
  $headers = @{ Authorization = "Bearer $token"; Accept = $accept }
  try {
    $manifest = Get-RegistryJson "https://ghcr.io/v2/$Repo/manifests/$Reference" $headers
  } catch {
    throw "ghcr.io/${Repo}:$Reference was not found (or is not public): has image.yml pushed this tag? ($($_.Exception.Message))"
  }
  if ($manifest.manifests) {
    $amd64 = $manifest.manifests | Where-Object { $_.platform.os -eq 'linux' -and $_.platform.architecture -eq 'amd64' } | Select-Object -First 1
    if (-not $amd64) { throw "ghcr.io/${Repo}:$Reference has no linux/amd64 image" }
    $manifest = Get-RegistryJson "https://ghcr.io/v2/$Repo/manifests/$($amd64.digest)" $headers
  }
  if (-not $manifest.config.digest) { throw "ghcr.io/${Repo}:$Reference has no image config" }
  Get-RegistryJson "https://ghcr.io/v2/$Repo/blobs/$($manifest.config.digest)" @{ Authorization = "Bearer $token" }
}

Write-Host "1/5 the subscription"
# The containerapp commands below need the extension current; once, before any of them.
Invoke-Az extension add --name containerapp --upgrade --only-show-errors
$subscription = Invoke-Az account show --query id --output tsv
$state = Invoke-Az rest --method get --url "https://management.azure.com/subscriptions/${subscription}?api-version=2022-12-01" --query state --output tsv
$disabled = -not (Test-Same $state 'Enabled')
if ($disabled) {
  $message = "subscription $subscription is $state (read only): re-enable it in the Azure portal (a free trial that ended needs an upgrade to pay-as-you-go) and run this again"
  if (-not $Preview) { throw $message }
  Write-Warning $message
}

Write-Host "2/5 the images: $modelImage, $gatewayImage"
$modelConfig = Get-ImageConfig $modelRepo $ModelTag
$null = Get-ImageConfig $gatewayRepo $GatewayTag
$label = $null
if ($modelConfig.config.Labels) { $label = $modelConfig.config.Labels.'org.galaxygen.model_hash' }
if (-not $ModelHash) {
  if (-not $label) {
    throw "$modelImage carries no label org.galaxygen.model_hash (built before W4, or not by image.yml): pass -ModelHash, the image's /api/version model.hash"
  }
  $ModelHash = $label
} elseif ($label -and -not (Test-Same $label $ModelHash)) {
  $message = "-ModelHash $ModelHash is not the image's label ${label}: the gateway would answer 503 at /healthz once it reaches the model"
  if (-not $Force) { throw "$message (the label is the truth; -Force deploys the given hash anyway)" }
  Write-Warning "$message (-Force)"
}
if ($ModelHash -cnotmatch '^[0-9a-f]{32}$') { throw "model hash '$ModelHash' is not 32 lowercase hex characters" }
Write-Host "    model.hash $ModelHash (the gateway's pin)"

Write-Host "3/5 resource group $ResourceGroup in $Location"
$groupExists = Test-Same (Invoke-Az group exists --name $ResourceGroup) 'true'
if ($groupExists) {
  $envName = "$Name-env"
  $apps = @(Invoke-Az containerapp list --resource-group $ResourceGroup --query "[].{name:name, state:properties.provisioningState, env:properties.managedEnvironmentId}" --output json | Out-String | ConvertFrom-Json)
  $envs = @(Invoke-Az containerapp env list --resource-group $ResourceGroup --query "[].{name:name, profiles:properties.workloadProfiles}" --output json | Out-String | ConvertFrom-Json)
  $ourEnv = $envs | Where-Object { Test-Same $_.name $envName } | Select-Object -First 1
  $front = $apps | Where-Object { Test-Same $_.name $Name } | Select-Object -First 1
  $why = $null
  if ($Recreate) { $why = '-Recreate' }
  elseif ($ourEnv -and @($ourEnv.profiles | Where-Object { $_ }).Count -eq 0) {
    $why = "environment $envName is consumption-only (no workload profiles), a type the template cannot change"
  }
  if ($why) {
    # Our two apps, and any other app in the environment (an environment with apps in it cannot be deleted).
    $doomed = @($apps | Where-Object {
        (Test-Same $_.name $Name) -or (Test-Same $_.name "$Name-model") -or
        ($ourEnv -and $_.env -and $_.env.EndsWith("/managedEnvironments/$envName", $ignoreCase))
      })
    $appList = ($doomed | ForEach-Object { $_.name }) -join ', '
    if (-not $appList) { $appList = 'none' }
    $envList = 'none'
    if ($ourEnv) { $envList = $ourEnv.name }
    Write-Host "    recreating ($why): deleting app(s) $appList and environment $envList"
    if ($Preview) {
      Write-Host '    (preview: nothing deleted)'
    } else {
      foreach ($app in $doomed) {
        Write-Host "    az containerapp delete $($app.name)"
        Invoke-Az containerapp delete --resource-group $ResourceGroup --name $app.name --yes --output none
      }
      if ($ourEnv) {
        Write-Host "    az containerapp env delete $($ourEnv.name)"
        Invoke-Az containerapp env delete --resource-group $ResourceGroup --name $ourEnv.name --yes --output none
      }
    }
  } elseif ($front -and (Test-Same $front.state 'Failed')) {
    Write-Host "    app $Name is in a Failed state: run again with -Recreate to delete the apps and $envName and create them anew"
  }
} elseif ($Preview) {
  Write-Host '    (preview: the group does not exist and is not created)'
}
if (-not $Preview) {
  Invoke-Az group create --name $ResourceGroup --location $Location --output none
}

$deploy = @(
  '--resource-group', $ResourceGroup,
  '--template-file', (Join-Path $PSScriptRoot 'main.bicep'),
  '--parameters', "name=$Name", "location=$Location", "modelImage=$modelImage", "gatewayImage=$gatewayImage", "modelHash=$ModelHash"
)
if ($Preview) {
  if ($disabled) {
    Write-Host '4/5 what-if skipped: the subscription is disabled, and ARM refuses to validate a deployment on it'
  } elseif (-not $groupExists) {
    Write-Host "4/5 what-if skipped: resource group $ResourceGroup does not exist (a run without -Preview creates it)"
  } else {
    Write-Host '4/5 what-if (preview)'
    Invoke-Az deployment group what-if @deploy
  }
  Write-Host '5/5 preview done: nothing changed'
  return
}

Write-Host "4/5 environment, storage and both apps"
$outputs = Invoke-Az deployment group create @deploy --query properties.outputs --output json | Out-String | ConvertFrom-Json

Write-Host "5/5 done"
Write-Host "    galaxygen $GatewayTag / model $ModelTag is live at $($outputs.url.value)"
Write-Host "    the model (internal): $($outputs.modelFqdn.value); storage: $($outputs.storageAccount.value)"
Write-Host '    both scale to zero between visits: the first request starts the gateway, and only an uncached one the model'
