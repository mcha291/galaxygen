<#
.SYNOPSIS
  Build galaxygen in Azure and deploy it to Container Apps. No local Docker needed.

.EXAMPLE
  az login
  ./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Location australiaeast

  Re-running deploys the current commit as a new revision; the registry, identity
  and environment are left as they are.
#>
param(
  [Parameter(Mandatory)] [string] $ResourceGroup,
  [string] $Location = 'australiaeast',
  [string] $Name = 'galaxygen',
  [string] $Tag = $(git rev-parse --short HEAD)
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$template = Join-Path $PSScriptRoot 'main.bicep'

function Invoke-Az {
  & az @args
  if ($LASTEXITCODE -ne 0) { throw "az $($args -join ' ') failed ($LASTEXITCODE)" }
}

if (git -C $root status --porcelain) {
  Write-Warning "Working tree has uncommitted changes; the image is built from the files on disk, tagged $Tag."
}

Write-Host "1/4 resource group $ResourceGroup in $Location"
Invoke-Az group create --name $ResourceGroup --location $Location --output none

Write-Host "2/4 registry and pull identity"
$registry = Invoke-Az deployment group create --resource-group $ResourceGroup --template-file $template `
  --parameters name=$Name deployApp=false --query properties.outputs.registryName.value --output tsv

Write-Host "3/4 building galaxygen:$Tag in $registry"
Invoke-Az acr build --registry $registry --image "galaxygen:$Tag" --file (Join-Path $root 'Dockerfile') $root

Write-Host "4/4 container app"
$url = Invoke-Az deployment group create --resource-group $ResourceGroup --template-file $template `
  --parameters name=$Name deployApp=true imageTag=$Tag --query properties.outputs.url.value --output tsv

Write-Host "galaxygen:$Tag is live at $url"
