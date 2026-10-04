param([ValidateSet('S0','S1','S2','S3','S4','S5')][string]$Scenario='S0', [ValidateRange(1,100)][int]$Windows=1, [ValidateRange(50,2000)][int]$WindowMs=500, [string]$Port='COM5')
$ErrorActionPreference='Stop'
$weekRoot=Split-Path $PSScriptRoot -Parent
& "$weekRoot/projects/v2/interface/.venv/Scripts/python.exe" "$PSScriptRoot/capture_v1.py" --port $Port --scenario $Scenario --windows $Windows --window-ms $WindowMs --label observation
if ($LASTEXITCODE -ne 0) { throw 'Kayıt tamamlanamadı. Logları inceleyin; aktif koşu varsa kartı yeniden başlatıp tekrar deneyin.' }
