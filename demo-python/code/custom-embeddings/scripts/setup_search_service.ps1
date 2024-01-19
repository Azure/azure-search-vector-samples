. ./scripts/init_azd_env.ps1

. ./scripts/init_python_env.ps1

Start-Process -FilePath $venvPythonPath -ArgumentList "./scripts/setup_search_service.py" -Wait -NoNewWindow
