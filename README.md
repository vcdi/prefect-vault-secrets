# Vault Secrets for prefect
An implementation of [Prefect](https://www.prefect.io) secrets sourced from a local [Hashicorp Vault](https://www.vaultproject.io) service.

`VaultSecret` extends [`PrefectSecret`](https://docs.prefect.io/core/concepts/secrets.html)

Like PrefectSecrets, VaultSecrets, both local mode for local development and remote vault service is supported.

Both Vault Token and AppRole authentication methods are supported.

## Overview
1. Vault client credentials, either token or approle/secret, are stored as a Prefect Secret.
2. A flow parameter, `vault.credentials`, is set to the PrefectSecret key.
3. The parameter is explicitly added to the flow, to be referenced by VaultSecret in tasks.

Values are retrieved from the Vault service referencing a key/value path defined for the
Vault secret: `"<secret-mount-point>/<secret-path>/<secret-key>"`, e.g. `"secret/fake/secret/path/key-1"`
The value for the key is returned by VaultSecret.

## Configuration and Setup
VaultSecret uses the [Hashicorp hvac](https://hvac.readthedocs.io/en/stable/overview.html) python module for interacting with Vault and
supports the envrironment variables supported by `hvac`.

### Set vault addr url
Set the vault service address `VAULT_ADDR` env var.  Both `VAULT_ADDR` and `vault_addr`
are supported.

For local development, set the `VAULT_ADDR` env var.  If the vault service uses a local or
self-signed certificate authority for TLS/https, also set the `REQUESTS_CA_BUNDLE` env var.
```bash
export REQUESTS_CA_BUNDLE=<path-to-vault-tls-ca-cert-or-bundle>
export VAULT_ADDR="https://vault.example.com:8200"
```

For agent based flow execution, set the VAULT_ADDR env var in the agent config.

If using a k8s based agent, the agent can be configured to pass the env var to the job
execution environment.  Note that UPPER_CASE vars are converted to lower case in the
execution environment.
```yaml
prefect:
  job:
    envVars:
      - name: VAULT_ADDR
        value: "https://vault.example.com:8200"
```

### Create a PrefectSecret for vault.credentials parameter
Create a PrefectSecret with Vault client credentials to be referenced by the
`vault.credentials` parameter.

#### Local PrefectSecret
Set the secret locally via env var or in the `config.toml` prefect config file.

Example env vars
```bash
# client token
export PREFECT__CONTEXT__SECRETS__<prefect-secret-key>="{ VAULT_TOKEN=<vault-client-token> }"

# or AppRole
export PREFECT__CONTEXT__SECRETS__<prefect-secret-key>="""{
  VAULT_ROLE_ID=<vault-role-id>
  VAULT_SECRET_ID=<vault-secret-id>
}"""
```

Example section entries in the prefect `config.toml` file setting the PrefectSecret locally. 
```toml
# client token
[context.secrets]
<prefect-secret-key>.VAULT_TOKEN = "<vault-token>"

# or AppRole
[context.secrets]
<prefect-secret-key>.VAULT_ROLE_ID = "<vault-role-id>"
<prefect-secret-key>.VAULT_SECRET_ID = "<vault-secret-id>"
```

#### Prefect Cloud PrefectSecret
Set the secret Prefect Cloud via the UI as json value.  The name of this secret will be referenced
in the `vault.credentials` parameter.  Both the access token and appRole vault authentication
methods are supported.

Example definition of a `<prefect-secret-key>` PrefectSecret in Prefect Cloud.
```json
{
    "VAULT_TOKEN": "<vault-token>"
}

{
    "VAULT_ROLE_ID": "<vault-role-id>",
    "VAULT_SECRET_ID": "<vault-secret-id>"
}
```

## Set `vault.credentials` parameter
Set a `vault.credentials` parameter to the name of the credentials secret in the Flow
defintion.  As the parameter is referenced with a `VaultSecret.run()` call, but not
passed as a task argument, the Parameter must be explicitly added to the Flow definition.

This prepares the flow so that `VaultSecret`s can be referenced in flow tasks.

```python
from prefect_vault_secrets.vault_secrets import VaultSecret

@task
def my_task_with_vault_secrets():
    secret = VaultSecret('<vault-secret-path>').run()
    return True

with Flow('my-flow') as flow:

    # declare Paramater and explicitly add to the flow
    vault_creds = Parameter('vault.credentials', default={})
    flow.add_task(vault_creds)
    
```
   
## VaultSecrets module installation
As of 2021-06-10, the `prefect-vault-secrets` module is not published to `pypi.org`.
The module needs to be installed either from source or a local repository.
```bash
# local pip module repository
export PIP_EXTRA_INDEX_URL=https://<my-local-pip-module-repo/>
pip install prefect-vault-secrets --extra-index-url ${PIP_EXTRA_INDEX_URL}
```

### Development and test
To run tests during development, create a virtual env environment and 
install the module in edit mode:
```bash
# in venv python environment
pip install --editable ./.

pytest
```

For a small code base, `watchdog` can be used to run pytests when
source code module or test files are saved.
```bash
# in the venv python environment
pip install "watchdog[watchmedo]"

watchmedo shell-command \
    --patterns "./src/*/*.py;./tests/*/*.py" \
    --recursive \
    --drop \
    --command "pytest -v -s"
```