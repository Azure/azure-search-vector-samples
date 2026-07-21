. ./scripts/init_azd_env.ps1

. ./scripts/init_python_env.ps1

& $venvPythonPath ./scripts/setup_search_service.py
if ($LASTEXITCODE -ne 0) {
    throw "Failed to configure Azure AI Search."
}
