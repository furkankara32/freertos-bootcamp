param([string]$CubeIDE = 'C:\ST\STM32CubeIDE_2.2.0\STM32CubeIDE')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../.cube-workspace-native'))
$builder = Join-Path $CubeIDE 'headless-build.bat'
if (-not (Test-Path -LiteralPath $builder)) { throw 'CubeIDE yolunu -CubeIDE ile belirtin.' }
& $builder -data $workspace -import $PSScriptRoot -build 'RTOS_Hafta_3_L476RG/Debug'
if ($LASTEXITCODE -ne 0) { throw 'CubeIDE derlemesi başarısız.' }

if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "Debug/RTOS_Hafta_3_L476RG.elf"))) { throw "CubeIDE did not produce an ELF. Inspect the build log." }
