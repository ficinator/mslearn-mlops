[Azure Portal]: https://portal.azure.com/
[Azure ML Studio workspace]: https://ml.azure.com/?tid=6571d690-b42e-4b19-90e7-d85b945aa165&wsid=/subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourceGroups/learn/providers/Microsoft.MachineLearningServices/workspaces/mlops
[Azure Active Directory]: https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps
[mslearn-mlops settings]: https://github.com/ficinator/mslearn-mlops/settings

# MLOps in Azure

## Prerequisites

* Azure subscription (free for 1 month, $200 of credit)

## 0: Create Azure resources

For running an ML job you will need:

* ML workspace
* Compute
* Data asset (optional)

### 0.1: Create Azure ML workspace

In [Azure Portal]

* Create a resource > Azure Machine learning
* Resource group: **learn**
* Workspace name: **mlops**
* Create > Go to resource > Launch studio

### 0.2: Create Compute instance

In [Azure ML Studio workspace]

* Compute > + New
* Compute name: **cheapest-instance** (must be unique in the whole region)
* Virtual machine size: **Standard_A1_v2** (1 cores, 2 GB RAM, 10 GB disk)
* Create > wait for it...

Now it is accessible in the job YAML file as `azureml:cheapest-instance`

> **important**: do not forget to stop it after you're done!

### 0.3: Create Data asset (optional)

In [Azure ML Studio workspace]

* Data > (Data assets) > Create
* Name: **diabetes-dev-dir**
* Type: **uri_folder**
* Next
* From local files > Next
* Datastore: **workspaceblobstore**
* Next
* Upload > Upload folder: `experimentation/data` > Next
* Create

Now its first version can be referenced in the ML job input as `azureml:diabetes-dev-dir:1`:

```yml
inputs:
  training_data: 
    type: uri_folder
    path: azureml:diabetes-dev-dir:1
    mode: ro_mount
```

## 1: Create an ML job

We'll use `azure-cli` this time.

### 1.1: Install `azure-cli`

Find your environment in the [install page](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) or read below for Ubuntu/Debian.

1. download MS keyring
    ```
    curl -sLS https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/microsoft.gpg > /dev/null
    sudo chmod go+r /etc/apt/keyrings/microsoft.gpg
    ```
2. sign the source
    ```
    echo "deb [arch=`dpkg --print-architecture` signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/azure-cli.list
    ```

3. update apt and install
    ```
    sudo apt update
    sudo apt install azure-cli
    ```

4. download ML extension
    ```
    az extension add -n ml -y
    ```

### 1.2: Create an ML job

1. log into azure (opens a web page)

    ```
    az login
    ```

2. run the job
    ```
    az ml job create -g learn -w mlops -f src/job.yml
    ```

## 2: Use GH Actions for model training

### 2.1: Create Service Principal

* In [Azure Active Directory] register a new app:
    * App registration > + New registration
    * Name: **github-aml-sp**
    * Register
* In [Azure ML workspace](https://portal.azure.com/#@filippovolnygmail.onmicrosoft.com/resource/subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourcegroups/learn/providers/Microsoft.MachineLearningServices/workspaces/mlops/users) assign a role to the app:
    * Access control (IAM) > + Add > Add role assignment > Contributor > Next
    * + Select members > github-aml-sp > Select


Create a service principal directly with `azure-cli`:

```
az ad sp create-for-rbac --name github-aml-sp --role contributor --scopes /subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourceGroups/learn/providers/Microsoft.MachineLearningServices/workspaces/mlops --sdk-auth
```

> TODO: what to use once deprecated `--sdk-auth` option is removed?

### 2.2: Create GitHub Action Secret

* [mslearn-mlops settings] > Secrets and variables > Actions > New repository secret
* Name: **AZURE_CREDENTIALS**
* Secret: [**\<output from the previous command\>**](#2.1:-create-service-principal)

### 2.3: Create Compute cluster

For some reason the service principal is only allowed to run jobs in compute cluster, not instance.

In [Azure ML Studio workspace]

* Compute > Compute clusters > + New
* Virtual machine size: **Standard_A1_v2** (1 cores, 2 GB RAM, 10 GB disk)
* Next
* Compute name: **cheapest-cluster** (must be unique in the whole region)
* Create > wait for it...

Now it is accessible in the job YAML file as `azureml:cheapest-cluster`

> **important**: do not forget to stop it after you're done!

### 2.4: Run GH Action manually

* [mslearn-mlops action](https://github.com/ficinator/mslearn-mlops/actions/workflows/02-manual-trigger-job.yml) > Run workflow > hopefully it runs

## 3: Trigger workflow on PR

### 3.1: Create branch protection rule

* [mslearn-mlops settings] > Branches > Add branch protection rule
* Branch name pattern: **main**
* Require a pull request before merging > Require approvals
* Create

### 3.2: Create workflow triggered on PR creation

```yml
on: [pull_request]
```

## 4: Trigger linting and unit testing on PR

### 4.1: Python linting in vs code

In the UI:

* `pip install flake8 black`
* Extensions > Python (`ms-python.python`) > Install
* Settings (cogwheel)
* Python > Linting: **Enabled**, **Flake8 Enabled**, **Lint On Save**
* Python > Formatting > Provider: **black**
* Python > Testing: **Pytest Enabled** 
* Ctrl + Shift + P > Preferences: Configure Language Specific Settings... > Python
* Editor: **Format On Save**, **Default Formatter: Pylance**

or in the JSON:

Ctrl + Shift + P > Preferences: Open User Settings (JSON)

and add the following properties:

```json
{
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    },
    "python.testing.pytestEnabled": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}

```

### 4.2: Update code checks workflow

```yml
name: Code checks

on: [pull_request]

jobs:
  linting:
    ...
    steps:
    - ...
    - name: Install Flake8
      run: python -m pip install flake8
    - name: Run linting tests
      run: flake8 src/model/

  unit-tests:
    ...
    steps:
    - ...
    - name: Install requirements
      run: python -m pip install -r requirements.txt
    - name: Run unit tests
      run: pytest
```

### 4.3: Add jobs to branch protection rule

The above created jobs `linting` and `unit-tests` must be specified in the required status checks inside the protection rule for the main branch

* [mslearn-mlops settings] > Branches > main branch protection rule
* Require status checks to pass before merging > Require branches to be up to date before merging 
* Status checks that are required: **linting**, **unit-tests**

## 5: Use GH environments

### 5.1: Create an environment

One can configure an environment with:
* **protection rules**: somebody must explicitly approve before the job runs in this env
* **variables**: like repo variables, but available only in the env
* **secrets**: like repo secrets, but available only in the env

Steps:
* [mslearn-mlops settings] > Environments > New environment
* Name: **dev**
* Configure environment
* Add Secret
* Name: **AZURE_CREDENTIALS**
* Value: [**\<output from the create service principal command\>**](#2.1:-create-service-principal)

### 5.2: Create production environment with production data

* create production environment **prod** like in the [previous step](#5.1:-create-an-environment)
* create production data asset **diabetes-prod-dir** similar to [data asset for dev](#0.3:-create-data-asset-(optional))

### 5.3: Create new ML job yaml files

To use different data asset in each job, create an ML job file for each environment

> TODO: check if one can reuse parts of ML jobs in the [docs](https://learn.microsoft.com/en-us/azure/machine-learning/reference-yaml-overview)

`src/job-dev.yml`
```yml
inputs:
  training_data: 
    type: uri_folder
    path: azureml:diabetes-dev-dir:1
    mode: ro_mount
  reg_rate: 0.01
environment: azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu@latest
compute: azureml:cheapest-cluster
experiment_name: diabetes-dev-data-example
description: Train a classification model on diabetes data using a registered dataset as input.
```

### 5.4: Create GH Action workflow

It will run two jobs on push to main branch: one for *dev* and other for *prod* environment. The env secrets can be accessed the same way as repo secrets, e.g. `${{secrets.AZURE_CREDENTIALS}}`

The *prod* job runs only if the *dev* job finishes successfully (ML job ran successfully too). To do so, one must add
* `needs` keyword to specify dependencies of the job
* add `--stream` option to the ML job command to forward its output to GH

`.github/workflows/05-trigger-ml-jobs.yml`
```yml
on:
  push:
    branches:
    - main

jobs:
  experiment:
    ...
    environment: dev
    steps:
    - ...
      run: |
        az ml job create \
        --file src/job-dev.yml \
        ...
        --stream

  production:
    ...
    environment: prod
    needs: experiment
    steps:
    - ...
      run: |
        az ml job create \
        --file src/job-prod.yml \
        ...
```

## 6: Deploy the model

Can follow [this guide](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-mlflow-models-online-endpoints?tabs=cli) or read further...

To configure the default resource group and workspace run

```
az configure --defaults workspace=mlops group=learn
```

Now they can be ommited from subsequent `azure-cli` commands.

### 6.1.: Register a model

In the [Azure ML Studio workspace]:

* Models > Register (From a job output)
* check the latest `diabetes-prod-data-example` job > Next > Next
* Name: **diabetes-classifier**
* Next > Register

In `azure-cli`:

```
az ml model create --name sklearn-diabetes --type mlflow_model --path azureml://jobs/<run_id>/outputs/artifacts/model
```


### 6.2: Create an online (real-time) endpoint

In the [Azure ML Studio workspace]:

* Endpoints > (Real-time endpoints) > Create (Real-time endpoint (quick))
* Select a model: **sklearn-diabetes**
* Virtual machine: **Standard_DS1_v2 (1 core, 3.5 GB RAM, 7 GB disk)**
* Endpoint name: **mlops-diabetes**
* Deployment name: **sklearn-diabetes-1**
* Deploy > wait for it...

In `azure-cli`:

```
az ml online-endpoint create --name mlops-diabetes
az ml online-deployment create --file src/deployment.yml --all-traffic
```

### 6.3: Invoke the endpoint

In the [Azure ML Studio workspace]:

* Endpoints > mlops-diabetes > Test
* copy the content of `experimentation/sample-request.json` file
* Test

In `azure-cli`:

```
az ml online-endpoint invoke --name mlops-diabetes --request-file experimentation/sample-request.json
```

In `curl`:

* get credentials (key):
    * in [Azure ML Studio workspace]: Endpoints > mlops-diabetes > Consume > Primary key
    * or `ENDPOINT_CRED=$(az ml online-endpoint get-credentials --name mlops-diabetes --output tsv --query primaryKey)`

* send the request
    ```
    curl -X POST https://mlops-diabetes.eastus2.inference.ml.azure.com/score \
        -H "Authorization: Bearer $ENDPOINT_CRED" \
        -H 'Content-Type: application/json' \
        -d @experimentation/sample-request.json
    ```

### 6.4: Put everything into GH Action workflow

* in the "Set up azure-cli" step the ml extension is installed and the default resource group and ML workspace are configured. Now we are able to drop these options from subsequent commands.
* allow "Create endpoint" step to fail in case the endpoint already exists (not ideal, but I'm just learning) 

`.github/workflows/06-deploy.yml`
```yml
jobs:
  deploy:
    ...
    steps:
    ...
    - name: Set up azure-cli
      run: |
        az extension add -n ml -y
        az configure --defaults workspace=mlops group=learn
    - name: Create endpoint
      run: az ml online-endpoint create --file src/endpoint.yml
      continue-on-error: true
    - name: Deploy model
      run: az ml online-deployment create --file src/deployment.yml --all-traffic
    - name: Test model
      run: az ml online-endpoint invoke --name mlops-diabetes --request-file experimentation/sample-request.json 

```
