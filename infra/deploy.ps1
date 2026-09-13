<#
.SYNOPSIS
  Deploy galaxygen to Azure Container Apps from its public image on ghcr.io.

.DESCRIPTION
  The image is built by .github/workflows/image.yml on every push and tagged with
  the short commit. This script only creates or updates the Azure side, sized for
  the free grants (see infra/main.bicep). Re-running with a new tag rolls out a
  new revision.

.EXAMPLE
  az login
  ./infra/deploy.ps1 -ResourceGroup galaxygen-rg -Location australiaeast -Tag add6034
#>
param(
  [Parameter(Mandatory)] [string] $ResourceGroup,
  [string] $Location = 'australiaeast',
  [string] $Name = 'galaxygen',
  [string] $Image = 'ghcr.io/mcha291/galaxygen',
  [string] $Tag = $(git rev-parse --short HEAD)
)

$ErrorActionPreference = 'Stop'
# A fresh winget install is not on this shell's PATH until a new terminal opens.
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
  $env:PATH += ';C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin'
}

function Invoke-Az {
  & az @args
  if ($LASTEXITCODE -ne 0) { throw "az $($args -join ' ') failed ($LASTEXITCODE)" }
}

Write-Host "1/2 resource group $ResourceGroup in $Location"
Invoke-Az group create --name $ResourceGroup --location $Location --output none

Write-Host "2/2 environment and app, image ${Image}:$Tag"
$url = Invoke-Az deployment group create --resource-group $ResourceGroup `
  --template-file (Join-Path $PSScriptRoot 'main.bicep') `
  --parameters name=$Name image="${Image}:$Tag" --query properties.outputs.url.value --output tsv

Write-Host "galaxygen:$Tag is live at $url (scaled to zero between visits; the first request starts a replica)"
