param([ValidateSet(115200,460800)][int]$Baud=115200, [string]$Port)
$ErrorActionPreference = 'Stop'
$weekRoot = Split-Path $PSScriptRoot -Parent
$runtime = Join-Path $weekRoot 'projects/v2/interface/.venv/Scripts/python.exe'
$launcher = Join-Path $weekRoot 'projects/v2/interface/launch.py'
if (-not (Test-Path -LiteralPath $runtime)) { throw 'Ortak Python ortamı eksik: projects/v2/interface/setup.ps1 çalıştırın.' }
$launchArgs = @($launcher, '--baud', $Baud)
if ($Port) { $launchArgs += @('--port', $Port) }
& $runtime @launchArgs
