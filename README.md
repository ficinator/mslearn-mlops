# MLOps in Azure

## Prerequisites

* Azure subscription (free for 1 month, $200 of credit)

## Create Azure resources

For running an ML job you will need:

* ML workspace
* Compute
* Data asset (optional)

### Create Azure ML Workspace

In [Azure Portal](https://portal.azure.com/) 

* Create a resource > Azure Machine learning
* Resource group: **learn**
* Workspace name: **learn-mlops**
* Create > Go to resource > Launch studio

### Create Compute

In [Azure ML Studio workspace](https://ml.azure.com/?tid=6571d690-b42e-4b19-90e7-d85b945aa165&wsid=/subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourceGroups/learn/providers/Microsoft.MachineLearningServices/workspaces/mlops)

* Compute > + New
* Compute name: **tmp-instance** (must be unique in the whole region)
* Virtual machine size: **Standard_A1_v2** (1 cores, 2 GB RAM, 10 GB disk)
* Create > wait for it...

Now it is accessible in the job YAML file as `azureml:cheapest-instance`

> **important**: do not forget to stop it after you're done!

### Create Data asset (optional)

TODO...

## Create a ML job using `azure-cli`

### Install `azure-cli`

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

### Create an ML job

1. log into azure (opens a web page)

    ```
    az login
    ```

2. run the job
    ```
    az ml job create -g learn -w learn-mlops -f src/job.yml
    ```

## Use GH Actions for model training

### Create Service Principal

In [Azure Active Directory](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) register a new app or create a service principal directly with `azure-cli`

```
az ad sp create-for-rbac --name github-aml-sp --role contributor --scopes /subscriptions/b42b69cf-27c0-4ee2-99a0-a718ebd91945/resourceGroups/learn/providers/Microsoft.MachineLearningServices/workspaces/learn-mlops
```

### Create GitHub Action Secret

* [mslearn-mlops  settings](https://github.com/ficinator/mslearn-mlops/settings/secrets/actions) > New repository secret
* Name: **AZURE_CREDENTIALS**
* Secret: **\<output from the previous command\>**

