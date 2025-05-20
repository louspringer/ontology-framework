# PowerShell script to get APIM subscription key
param(
    [string]$ApimName = "baldo-apim",
    [string]$ResourceGroup = "BALDO-DEVBOX-RG",
    [string]$ApiSuffix = "graphdb"
)

# Get the Unlimited subscription (SID is always 00000000000000000000000000000001)
$sub = az rest --method get --url "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$ResourceGroup/providers/Microsoft.ApiManagement/service/$ApimName/subscriptions/00000000000000000000000000000001?api-version=2021-08-01" | ConvertFrom-Json

if (-not $sub.primaryKey) {
    Write-Error "Could not retrieve subscription key."
    exit 1
}

$key = $sub.primaryKey
Write-Host "[INFO] Subscription key: $key"
Write-Host ""
Write-Host "[INFO] Sample curl command:"
Write-Host "curl -H 'Ocp-Apim-Subscription-Key: $key' https://$ApimName.azure-api.net/$ApiSuffix" 