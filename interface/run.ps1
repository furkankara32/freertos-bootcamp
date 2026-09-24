param([switch]$Demo)
$ErrorActionPreference = 'Stop'
$runtime = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path $runtime)) { throw 'Önce setup.ps1 çalıştırın.' }
$launchArgs = @((Join-Path $PSScriptRoot 'launch.py'))
if ($Demo) { $launchArgs += '--demo' }
& $runtime @launchArgs
