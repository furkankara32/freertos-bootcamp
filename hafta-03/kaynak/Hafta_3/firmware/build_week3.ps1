param([string]$ArmBin, [string]$BuildDirectory = 'build')
$ErrorActionPreference = 'Stop'
if (!$ArmBin -and !(Get-Command arm-none-eabi-gcc -ErrorAction SilentlyContinue)) {
    if (Test-Path -LiteralPath 'C:\ST') {
        $gcc = Get-ChildItem -LiteralPath 'C:\ST' -Filter arm-none-eabi-gcc.exe -Recurse -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
        if ($gcc) { $ArmBin = $gcc.DirectoryName }
    }
}
if ($ArmBin) { $env:PATH = "$ArmBin;$env:PATH" }
if (!(Get-Command arm-none-eabi-gcc -ErrorAction SilentlyContinue)) { throw 'Arm GCC bulunamadi. -ArmBin ile bin klasorunu belirtin.' }
cmake -S $PSScriptRoot -B (Join-Path $PSScriptRoot $BuildDirectory) -G Ninja
if ($LASTEXITCODE -ne 0) { throw 'CMake yapilandirmasi basarisiz.' }
cmake --build (Join-Path $PSScriptRoot $BuildDirectory)
if ($LASTEXITCODE -ne 0) { throw 'Derleme basarisiz.' }
