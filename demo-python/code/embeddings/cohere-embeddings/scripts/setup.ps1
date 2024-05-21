$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  # fallback to python3 if python not found
  $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

Write-Host 'Creating python virtual environment ".venv"'
Start-Process -FilePath ($pythonCmd).Source -ArgumentList "-m venv ./.venv" -Wait -NoNewWindow

$venvPythonPath = "./.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./.venv/bin/python"
}

Write-Host 'Installing dependencies from "requirements.txt" into virtual environment'
Start-Process -FilePath $venvPythonPath -ArgumentList "-m pip install -r ./cohere-embeddings-requirements.txt" -Wait -NoNewWindow

Write-Host "Loading azd .env file from current environment"
foreach ($line in (& azd env get-values)) {
    if ($line -match "([^=]+)=(.*)") {
        $key = $matches[1]
        $value = $matches[2] -replace '^"|"$'
	    [Environment]::SetEnvironmentVariable($key, $value)
    }
}

Start-Process -FilePath $venvPythonPath -ArgumentList "./scripts/setup.py" -Wait -NoNewWindow
