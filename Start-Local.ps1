param([int]$Port = 0)
$ErrorActionPreference = 'Stop'
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython -X utf8 (Join-Path $PSScriptRoot 'tools\serve.py') --port $Port
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -X utf8 (Join-Path $PSScriptRoot 'tools\serve.py') --port $Port
} else {
    throw 'Python 3.10 or newer is required. No packages or model downloads are needed for the default preview.'
}
