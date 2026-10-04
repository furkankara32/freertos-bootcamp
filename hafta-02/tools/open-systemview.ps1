param([string]$Trace)
$ErrorActionPreference='Stop'
$weekRoot=Split-Path $PSScriptRoot -Parent
if (!$Trace) {
    $candidate=Get-ChildItem "$weekRoot/traces/v2" -Filter trace.json -Recurse | Sort-Object LastWriteTime -Descending | Where-Object { (Get-Content $_.FullName -Raw | ConvertFrom-Json).clean } | Select-Object -First 1
    if (!$candidate) { throw 'Temiz kayıt bulunamadı.' }
    $Trace=Join-Path $candidate.DirectoryName 'recording.SVDat'
}
$resolvedTrace=(Resolve-Path -LiteralPath $Trace).Path
Start-Process "$PSScriptRoot/SystemView-4.10a/SystemView.exe" -ArgumentList ('-load "'+$resolvedTrace+'"')
