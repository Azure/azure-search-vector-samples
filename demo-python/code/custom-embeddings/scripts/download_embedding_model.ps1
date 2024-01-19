. ./scripts/init_azd_env.ps1

. ./scripts/init_python_env.ps1

Start-Process -FilePath $venvPythonPath -ArgumentList "./scripts/download_embedding_model.py" -Wait -NoNewWindow
