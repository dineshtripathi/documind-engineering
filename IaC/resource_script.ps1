# 0.1 Install/Update Az
Install-Module Az -Scope CurrentUser -Repository PSGallery -Force

# 0.2 Login + pick subscription
Connect-AzAccount
Get-AzSubscription | Format-Table Name, Id
Set-AzContext -Subscription "<SUBSCRIPTION_NAME_OR_ID>"

# 0.3 Make clean RG (we'll recreate)
$rg = "rg-documind-dev"
$loc = "westeurope"
$exists = Get-AzResourceGroup -Name $rg -ErrorAction SilentlyContinue
if ($exists) { Remove-AzResourceGroup -Name $rg -Force -AsJob; Wait-Job * | Out-Null }
New-AzResourceGroup -Name $rg -Location $loc
