# Project Overview

In this project, I am aiming to practice different tool sets that we have learned as part of Data Talks Clubs Data Engieering Zoomcamp course.

To practice that, the **Data Talks Clubs** **Slack data** is selected as *dataset*. Therefore as final output, the project is aiming to create dashboard with analysis of, most talked topics, most used reactions, community netwpork graph, etc...

In the project includes following subfolders for respective capabilities.

| SubFolder                         | Capabilty                                                |
| ----------------------------------|----------------------------------------------------------|
| [.google](./.google/)             | Expected to store the google service account keys        |                  
| [.github](./.github/)             | CI/CD with GitHub Actions workflows                      |
| [iac](./iac/)                     | Infrastructure as Code for creating GCP resources        |
| [aiflow](./airflow/)              | ETL pipeline  with Airflow and Spark                     |
| [visualization](./visualization/) | Data Visualization with JupyterNotebooks and Plotly      |

---
## Infrastructure as Code (Terrafrom and Google Cloud)

To setup the required GCP resources, please follow the [detailed steps](./iac/README.md)
At the end of successfully completing the steps, you will be able to see the GCP resources in GCP console including: GSC bucket,BigQuery dataset, CloudComposer, IAM access rights, etc.


## Data Ingestion with Airflow

To initiate ETL pipeline that is responsible with:
    - Ingesting Raw Data to GCS Data Lake
    - Transforming Data with Spark
    - Ingesting Transformed Data to Google Cloud Storage
    - Ingesting Data from GCS to Google BigQuery
please follow the [detailed steps](./airflow/README.md).

## Visualization and Analysis

To create dashboard and visualizations please follow the [detailed steps](./visualization/README.md)

# Suggested Set-Up for the project
## Code Standardization & Code Formatting  with Pre-commit ((optional))
Follow the instructions below to install and setup pre-commit for the project.
In below, the steps to setup in **MacOs** will be given, for any other operating system,
please check [pre-commit](https://pre-commit.com/) documentation

1  Install pre-commit on machine
```shell
brew install pre-commit
pre-commit --version
```

2 (no action needed) Add pre-commit plugins to the project 
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





- CI/CD with GitHub Actions *(all workflows reside in [`.github`](./.github/) folder)*
- Infrastructure as Code for creating GCP resources *([`iac`](./iac/))*
- ETL creation with Airflow *([`airflow`](./airflow/))*
    - Building Docker Image for Airflow and Spark
    - Ingesting Raw Data to Google Cloud Storage
    - Transforming Data with Spark
    - Ingesting Transformed Data to Google Cloud Storage
    - Ingesting Data from GCS to Google BigQuery
- Data Visualization *([`visualization`](./visualization/))*
    - Understand most talked topics with Messages




















