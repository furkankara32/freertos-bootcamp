$ErrorActionPreference = 'Stop'
python -m venv (Join-Path $PSScriptRoot '.venv')
if ($LASTEXITCODE) { throw 'venv oluşturulamadı' }
& (Join-Path $PSScriptRoot '.venv/Scripts/python.exe') -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
if ($LASTEXITCODE) { throw 'Bağımlılıklar kurulamadı' }
