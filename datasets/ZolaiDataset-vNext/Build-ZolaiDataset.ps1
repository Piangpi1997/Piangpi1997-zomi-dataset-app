param(
    [string]$ProjectPath = 'C:\Users\cmfme\AndroidStudioProjects\MyApplication2',
    [string]$OutputPath = (Join-Path $env:USERPROFILE 'Downloads\ZolaiDataset-vNext-Rebuilt')
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath (Join-Path $ProjectPath 'backend\corpus'))) { throw 'ZOLAI project backend/corpus folder missing.' }
$zolaiPython = Get-Command python -ErrorAction Stop
& $zolaiPython.Source (Join-Path $PSScriptRoot 'scripts\test_pipeline.py')
if ($LASTEXITCODE -ne 0) { throw 'Pipeline checks failed; dataset build stopped.' }
& $zolaiPython.Source (Join-Path $PSScriptRoot 'scripts\reproduce.py') --project "$ProjectPath" --output "$OutputPath"
if ($LASTEXITCODE -ne 0) { throw 'Dataset candidate build failed.' }
Write-Host "Candidate: $OutputPath\candidate. Training is disabled."
