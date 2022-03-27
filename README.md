### pre-commit

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

## Good-2-Know

### External Table vs Native Tables in BigQuery
by Quora [Question](https://www.quora.com/What-is-the-difference-between-native-and-external-tables-in-Google-Big-Query)
~Native tables are tables that you import the full data inside Google BigQuery like you would do in any other common database system. In contrast, external tables are tables where the data is not stored inside Google BigQuery, but instead references the data from an external source, such as a data lake.

The advantages of creating external tables is that they are fast to create (you skip the part of importing data) and no additional monthly billing storage costs are accrued to your account (you only get charged the data that is stored in the data lake, which is comperatively cheaper than storing it in BigQuery). The disadvantages is that the queries against external tables are comparably slow as compared to native tables, especially if the files are very big. Otherwise, if the data is split into small files and is infrequently used by users, keeping them in a bucket in Google Cloud Storage can be a good use case to save storage costs.

There are other competitors like Amazon that provides the ability to create external tables as well. For instance, Amazon Redshift Spectrum allows you to create external tables in Redshift which references files in their S3 cloud storage~

For futher information please check limitations of [external](https://cloud.google.com/bigquery/docs/external-tables#external_table_limitations) and naive tables[].

# dtc-capstone-project

1. Follow the instructions in iac to setup, GCP authentication and creating

* Problem description [dataset] -> The slack data...
    * 0 points: Problem is not described
    * 1 point: Problem is described but shortly or not clearly
    * 2 points: Problem is well described and it's clear what the problem the project solves
* Cloud [4] by 15.03
    * 4 points: The project is developed on the clound and IaC tools are used
* Data ingestion (choose either batch or stream)
    * Batch / Workflow orchestration [airflow]
        * 0 points: No workflow orchestration
        * 2 points: Partial workflow orchestration: some steps are orchestrated, some run manually
        * 4 points: End-to-end pipeline: multiple steps in the DAG, uploading data to data lake (with or without Cloud Compooser :D )
    * Stream[x]
        * 0 points: No streaming system (like Kafka, Pulsar, etc)
        * 2 points: A simple pipeline with one consumer and one producer
        * 4 points: Using consumer/producers and streaming technologies (like Kafka streaming, Spark streaming, Flink, etc)
* Data warehouse [bigquery]
    * 0 points: No DWH is used
    * 2 points: Tables are created in DWH, but not optimized
    * 4 points: Tables are partitioned and clustered in a way that makes sense for the upstream queries (with explanation)
* Transformations (dbt, spark, etc) [spark] [dagster-dbt]
    * 0 points: No tranformations
    * 2 points: Simple SQL transformation (no dbt or similar tools)
    * 4 points: Tranformations are defined with dbt, Spark or similar technologies
* Dashboard [dash] [streamlit]
    * 0 points: No dashboard
    * 2 points: A dashboard with 1 tile
    * 4 points: A dashboard with 2 tiles
* Reproducibility
    * 0 points: No instructions how to run code at all
    * 2 points: Some instructions are there, but they are not complete
    * 4 points: Instructions are clear, it's easy to run the code, and the code works


### bugs & improvements:
Data Related
- user_identity table contains column names  as row value
- In user data, there is mismatch between ts column type

Infra-Related
- terraform was failing because of cloud api
- Add count to module cloud-composer (as I didnt finish dataloc)
- Automate loading logic to GCP Datalocs (optional)

Dags:
(optional) message-data : create dag factory out of it to be able to load all messages from other channels easily
- course-ml-zoomcamp (at least that one)
- announcements
- announcements-course-data-engineering
- book-of-the-week (book relations)
- general
- welcome (this one too)
--->
- (ignore)shameless-content
- (ignore)shameless-events
- (ignore)shamesless-promotion
- (ignore)shameless-social

DWH
- the tables do not take the schema changes automatically (will cause issue)
- (missing) do some partitioning and clustering on external table.. (maybe new dag, not sure yet)


Visualization
- Automated creation of the (Jupyter Notebook) out of the pipeline
- Questions to answer:
    - Most used reaction?
    - Most replied users? -> merge with user_identities
    - Most questioned topic? (done)
    - Message frequency by time?
    - Is there any correlation between people reply each other and locations..\
- (definetly wont finish)visualize your graphs (maybe dash, but might not be my highest priority)

