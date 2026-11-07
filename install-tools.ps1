$ErrorActionPreference = 'Stop'
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { throw 'Python 3.10+ required. Install Python, then rerun.' }
& $py.Source -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ required.' }
& $py.Source (Join-Path $PSScriptRoot 'install-tools.py')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
