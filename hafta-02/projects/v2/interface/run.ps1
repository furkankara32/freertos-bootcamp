param([switch]$Demo, [ValidateSet(115200,460800)][int]$Baud=460800, [string]$Port, [string]$Build)
$ErrorActionPreference = 'Stop'
$runtime = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $runtime)) { throw 'Önce setup.ps1 çalıştırın.' }
$launchArgs = @((Join-Path $PSScriptRoot 'launch.py'))
$launchArgs += @('--baud', $Baud)
if ($Port) { $launchArgs += @('--port', $Port) }
if ($Build) { $launchArgs += @('--build', $Build) }
if ($Demo) { $launchArgs += '--demo' }
& $runtime @launchArgs
