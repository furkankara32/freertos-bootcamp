param([string]$BuildDirectory = "build")
& (Join-Path $PSScriptRoot "build_week3.ps1") -BuildDirectory $BuildDirectory
