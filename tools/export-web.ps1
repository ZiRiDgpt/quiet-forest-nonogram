$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$enginePath = Join-Path $env:LOCALAPPDATA 'Programs\GDevelop\GDevelop.exe'
if (-not (Test-Path -LiteralPath $enginePath)) { throw 'GDevelop is not installed at the expected path.' }
Push-Location -LiteralPath $projectRoot
try {
  $exportInput = Join-Path $projectRoot '.generated-export.json'
  Copy-Item -LiteralPath (Join-Path $projectRoot 'game.json') -Destination $exportInput -Force
  $arguments = '"' + $exportInput + '" --run-command EXPORT_HTML5_EXTERNAL'
  $exportProcess = Start-Process -FilePath $enginePath -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $projectRoot 'validation\export.stdout.log') -RedirectStandardError (Join-Path $projectRoot 'validation\export.stderr.log')
  $exportHandle = $exportProcess.Handle
  $exportProcess.WaitForExit()
  $exportExitCode = $exportProcess.ExitCode
  $exportLog = Get-Content -LiteralPath (Join-Path $projectRoot 'validation\export.stdout.log') -Raw
  if (($null -ne $exportExitCode -and $exportExitCode -ne 0) -or $exportLog -notmatch '\[CLI\] Command "EXPORT_HTML5_EXTERNAL" finished successfully\.') { throw ('GDevelop export failed: ' + $exportExitCode) }
  python (Join-Path $PSScriptRoot 'package-web.py')
  if ($LASTEXITCODE -ne 0) { throw 'Web packaging failed.' }
  Write-Output 'GDevelop web export is ready in build/.'
} finally { Pop-Location }
