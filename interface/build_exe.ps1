$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
$previousBuildPath = $env:PATH
try {
    # Do not collect unrelated ICU/OpenSSL/UCRT DLLs from document tools on PATH.
    # Qt on Windows uses the OS ICU forwarder; Poppler's same-named ICU DLL has
    # different exports and causes QtCore import to fail in the frozen app.
    $basePython = & ./.venv/Scripts/python.exe -c "import sys; print(sys.base_prefix)"
    $env:PATH = "$PSScriptRoot/.venv/Scripts;$basePython;$env:SystemRoot/System32;$env:SystemRoot"
    & ./.venv/Scripts/python.exe -m PyInstaller --noconfirm --clean --onedir --windowed --name BootcampMonitorV2 --paths .. launch.py
    if ($LASTEXITCODE) { throw 'Paketleme başarısız' }
} finally { $env:PATH = $previousBuildPath; Pop-Location }
