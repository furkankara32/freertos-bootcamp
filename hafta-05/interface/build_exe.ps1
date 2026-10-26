param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$weekRoot = Split-Path -Parent $PSScriptRoot
& $Python -m PyInstaller --noconfirm --windowed --onedir --name Hafta5Lab --paths $weekRoot --distpath (Join-Path $weekRoot 'dist') --workpath (Join-Path $PSScriptRoot 'build') --specpath $PSScriptRoot (Join-Path $PSScriptRoot 'main.py')
if ($LASTEXITCODE -ne 0) { throw 'EXE paketleme başarısız' }
# Qt imports the Windows ICU API. A third-party icuuc.dll on PATH can be
# collected by PyInstaller even though it exports incompatible suffixed APIs.
# Let Windows resolve its own ICU DLLs instead of shipping those copies.
$bundleRoot = [IO.Path]::GetFullPath((Join-Path $weekRoot 'dist/Hafta5Lab/_internal'))
foreach ($name in @('icuuc.dll', 'icuin.dll', 'icudt78.dll')) {
    $candidate = Join-Path $bundleRoot $name
    if (Test-Path -LiteralPath $candidate) { Remove-Item -LiteralPath $candidate }
}
