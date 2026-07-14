. ./scripts/init_azd_env.ps1

. ./scripts/init_python_env.ps1

& $venvPythonPath ./scripts/download_embedding_model.py
if ($LASTEXITCODE -ne 0) {
    throw "Failed to download the embedding model."
}
