$ErrorActionPreference = "Stop"

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  # fallback to python3 if python not found
  $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    throw "Python 3 is required to deploy this sample."
}

$venvPythonPath = "./scripts/.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./scripts/.venv/bin/python"
}

if (-not (Test-Path -Path $venvPythonPath)) {
    Write-Host 'Creating python virtual environment "scripts/.venv"'
    & $pythonCmd.Source -m venv ./scripts/.venv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the deployment helper virtual environment."
    }
}

Write-Host 'Installing dependencies from "requirements.txt" into virtual environment'
& $venvPythonPath -m pip install -r ./scripts/requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install deployment helper dependencies."
}
