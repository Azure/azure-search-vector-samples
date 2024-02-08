param keyVaultName string
param computerVisionId string
param computerVisionSecretName string

module computerVisionKVSecret 'core/security/keyvault-secret.bicep' = {
  name: 'keyvault-secret'
  params: {
    keyVaultName: keyVaultName
    name: computerVisionSecretName
    secretValue: listKeys(computerVisionId, '2023-05-01').key1
  }
}
