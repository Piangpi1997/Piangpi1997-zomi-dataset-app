param([string]$OutputPath = (Join-Path $env:USERPROFILE 'Downloads\ZolaiDataset-vNext-Rebuilt'))
$ErrorActionPreference = 'Stop'
$dataset = Join-Path $PSScriptRoot 'datasets\ZolaiDataset-vNext'
& python (Join-Path $dataset 'scripts\test_pipeline.py')
if ($LASTEXITCODE -ne 0) { throw 'Pipeline checks failed.' }
& python (Join-Path $dataset 'scripts\reproduce.py') --baseline (Join-Path $dataset 'baseline') --output "$OutputPath"
if ($LASTEXITCODE -ne 0) { throw 'Candidate build failed.' }
Copy-Item -LiteralPath (Join-Path $dataset 'TrainingGate.json') -Destination (Join-Path $OutputPath 'candidate\TrainingGate.json')
& python (Join-Path $dataset 'scripts\verify_package.py') --directory (Join-Path $OutputPath 'candidate')
if ($LASTEXITCODE -ne 0) { throw 'Serialized verification failed.' }
Write-Host "Candidate built at $OutputPath\candidate. Training is disabled."
