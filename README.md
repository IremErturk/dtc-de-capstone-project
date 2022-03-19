# dtc-capstone-project

1. Follow the instructions in iac to setup, GCP authentication and creating 

* Problem description [dataset] -> The slack data...
    * 0 points: Problem is not described
    * 1 point: Problem is described but shortly or not clearly 
    * 2 points: Problem is well described and it's clear what the problem the project solves
* Cloud [4] by 15.03
    * 4 points: The project is developed on the clound and IaC tools are used
* Data ingestion (choose either batch or stream)
    * Batch / Workflow orchestration [airflow] [dagster]
        * 0 points: No workflow orchestration
        * 2 points: Partial workflow orchestration: some steps are orchestrated, some run manually
        * 4 points: End-to-end pipeline: multiple steps in the DAG, uploading data to data lake (with Cloud Compooser)
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

[dvc] [mlflow] [pachyderm]