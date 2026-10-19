$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force validation | Out-Null
$python = Join-Path (Get-Location) '.venv/Scripts/python.exe'
$cli = Join-Path (Get-Location) '.venv/Scripts/viralforecast.exe'
if (Test-Path work/tools/ffprobe.exe) { $env:FFPROBE = Join-Path (Get-Location) 'work/tools/ffprobe.exe' }
$records = [System.Collections.Generic.List[object]]::new()
function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments, [int]$Expected = 0)
    $result = & $Executable @Arguments 2>&1 | Out-String
    $code = $LASTEXITCODE
    $records.Add([ordered]@{ executable = Split-Path $Executable -Leaf; arguments = $Arguments; expected_exit = $Expected; actual_exit = $code; output = $result.Trim() })
    if ($code -ne $Expected) { throw "Expected $Expected, got $code : $result" }
    Write-Host "$($Arguments[0]): exit $code (expected $Expected)"
}
try {
    Invoke-Checked $python @('examples/generate.py','--out','examples/data')
    Invoke-Checked $cli @('analyze','--video','examples/data/demo.mp4','--title','How to make a clear opening?','--caption','Try one change #demo','--cover','examples/data/cover.png','--transcript','examples/data/transcript.json','--platform','tiktok','--out','outputs/demo/mode-a')
    Invoke-Checked $cli @('predict','--analysis','outputs/demo/mode-a/analysis.json','--history','examples/data/synthetic_history.csv','--account','demo','--platform','tiktok','--as-of','2026-10-19T00:00:00Z','--out','outputs/demo/mode-b')
    Invoke-Checked $cli @('backtest','--history','examples/data/synthetic_history.csv','--account','demo','--platform','tiktok','--step','5','--out','outputs/demo/backtest')
    Invoke-Checked $cli @('compare','--prediction','outputs/demo/mode-b/prediction.json','--actual','examples/data/actual.json','--out','outputs/demo/compare')
    Invoke-Checked $cli @('report','--input','outputs/demo/mode-b/prediction.json','--out','outputs/demo/rendered')
    Invoke-Checked $cli @('predict','--analysis','outputs/demo/mode-a/analysis.json','--history','examples/data/synthetic_history.csv','--account','demo','--platform','tiktok','--as-of','2020-06-01T00:00:00Z','--out','outputs/demo/downgrade')
    foreach ($file in @('invalid.csv','empty.csv')) {
        Invoke-Checked $cli @('backtest','--history',"examples/data/$file",'--account','demo','--platform','tiktok','--out','outputs/demo/expected-error') 2
    }
    $oldProbe = $env:FFPROBE
    try {
        $env:FFPROBE = Join-Path (Get-Location) 'work/intentionally-missing-ffprobe.exe'
        Invoke-Checked $cli @('analyze','--video','examples/data/demo.mp4','--out','outputs/demo/expected-error') 2
    } finally { $env:FFPROBE = $oldProbe }
} finally {
    $records | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 validation/demo-commands.json
}
