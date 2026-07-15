$ErrorActionPreference = "Stop"

Write-Host "Loading azd .env file from current environment"
$azdValues = & azd env get-values
if ($LASTEXITCODE -ne 0) {
    throw "Failed to load the current azd environment."
}

foreach ($line in $azdValues) {
    if ($line -match "([^=]+)=(.*)") {
        $key = $matches[1]
        $value = $matches[2] -replace '^"|"$'
        [Environment]::SetEnvironmentVariable($key, $value)
    }
}
