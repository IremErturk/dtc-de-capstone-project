# Project Overview

# Setting Up Environment and Pre-requsites

### (optional) pre-commit
Follow the instructions to install and setup pre-commit for the project.
In below, the steps to setup in **MacOs** will be given, for any other operating system,
please check [pre-commit](https://pre-commit.com/) documentation

1 Install pre-commit on machine
```shell
brew install pre-commit
pre-commit --version
```

2 Add pre-commit plugins to the project (no action needed)
Create `.pre-commit-config.yaml` configuration file on root to setup plugins.


3 To run pre-commit againts your git repository. There is two
approaches that can be followed.
- (Option 1) Install pre-pommit Git Hook Script which will ensure running pre-commit automatically with every `git commit`.
    ```shell
    cd <project-git-repo>
    pre-commit install
    ```
- (Option 2) Run pre-commit against all files manually, which is more transparent way as you have more control over changes.
    ```shell
    pre-commit run --all-files
    ```

4 (optional) To update hooks to latest version automatically.
```shell
 pre-commit autoupdate
```


# Infrastructure as Code (Terrafrom and Google Cloud)
[todo: add link to README in iac]

# Data Ingestion with Airflow

[todo: add link to README in airflow]

# Visualization and Analysis
[todo: add link to README in visualization]
