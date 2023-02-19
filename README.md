# MLOps in Azure

## Prerequisites

* Azure subscription (free for 1 month, $200 of credit)

## 0: Create Azure resources

For running an ML job you will need:

* ML workspace
* Compute
* Data asset (optional)

### 0.1: Create Azure ML workspace

In [Azure Portal](https://portal.azure.com/) 

* Create a resource > Azure Machine learning
* Resource group: **learn**
* Workspace name: **learn-mlops**
* Create > Go to resource > Launch studio

### 0.2: Create Compute instance

In [Azure ML Studio workspace](https://ml.azure.com/?tid=6571d690-b42e-4b19-90e7-d85b945aa165&wsid=/subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourceGroups/learn/providers/Microsoft.MachineLearningServices/workspaces/mlops)

* Compute > + New
* Compute name: **cheapest-instance** (must be unique in the whole region)
* Virtual machine size: **Standard_A1_v2** (1 cores, 2 GB RAM, 10 GB disk)
* Create > wait for it...

Now it is accessible in the job YAML file as `azureml:cheapest-instance`

> **important**: do not forget to stop it after you're done!

### 0.3: Create Data asset (optional)

TODO...

## 1: Create a ML job using `azure-cli`

### 1.1: Install `azure-cli`

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
    az ml job create -g learn -w learn-mlops -f src/job.yml
    ```

## 2: Use GH Actions for model training

### 2.1: Create Service Principal

In [Azure Active Directory](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) register a new app or create a service principal directly with `azure-cli`

```
az ad sp create-for-rbac --name github-aml-sp --role contributor --scopes /subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourceGroups/learn/providers/Microsoft.MachineLearningServices/workspaces/learn-mlops --sdk-auth
```

> no idea what `--sdk-auth` means, but it is deprecated

### 2.2: Create GitHub Action Secret

* [mslearn-mlops settings](https://github.com/ficinator/mslearn-mlops/settings/secrets/actions) > New repository secret
* Name: **AZURE_CREDENTIALS**
* Secret: **\<output from the previous command\>**

### 2.3: Create Compute cluster

For some reason the service principal is only allowed to run jobs in compute cluster, not instance.

In [Azure ML Studio workspace](https://ml.azure.com/?tid=6571d690-b42e-4b19-90e7-d85b945aa165&wsid=/subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourceGroups/learn/providers/Microsoft.MachineLearningServices/workspaces/mlops)

* Compute > Compute clusters > + New
* Virtual machine size: **Standard_A1_v2** (1 cores, 2 GB RAM, 10 GB disk)
* Next
* Compute name: **cheapest-cluster** (must be unique in the whole region)
* Create > wait for it...

Now it is accessible in the job YAML file as `azureml:cheapest-cluster`

> **important**: do not forget to stop it after you're done!

### 2.4: Run GH Action

* [mslearn-mlops action](https://github.com/ficinator/mslearn-mlops/actions/workflows/02-manual-trigger-job.yml) > Run workflow > hopefully it runs

## 3: Trigger workflow on PR

### 3.1: Create branch protection rule

* [mslearn-mlops settings](https://github.com/ficinator/mslearn-mlops/settings) > Branches > Add branch protection rule
* Branch name pattern: **main**
* Require a pull request before merging > Require approvals
* Create

### 3.2: Create workflow triggered on PR creation

```yml
on: [pull_request]
```

## 4: Trigger linting and unit testing on PR

### 4.1: 


* [mslearn-mlops settings](https://github.com/ficinator/mslearn-mlops/settings) > Branches > main branch protection rule
* Require status checks to pass before merging > Require branches to be up to date before merging 
* Status checks that are required: ****