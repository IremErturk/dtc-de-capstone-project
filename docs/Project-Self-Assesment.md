# Project Self Assessment

* Problem description
    * 0 points: Problem is not described
    * 1 point: Problem is described but shortly or not clearly 
    * [x] 2 points: Problem is well described and it's clear what the problem the project solves
* Cloud
    * 0 points: Cloud is not used, things run only locally
    * 2 points: The project is developed on the cloud
    * [x] 4 points: The project is developed on the clound and IaC tools are used
* Data ingestion (choose either batch or stream)
    * [x] Batch / Workflow orchestration
        * 0 points: No workflow orchestration
        * 2 points: Partial workflow orchestration: some steps are orchestrated, some run manually
        * [x] 4 points: End-to-end pipeline: multiple steps in the DAG, uploading data to data lake
    * Stream
        * 0 points: No streaming system (like Kafka, Pulsar, etc)
        * 2 points: A simple pipeline with one consumer and one producer
        * 4 points: Using consumer/producers and streaming technologies (like Kafka streaming, Spark streaming, Flink, etc)
* Data warehouse
    * 0 points: No DWH is used
    * [x] 2 points: Tables are created in DWH, but not optimized
    * 4 points: Tables are partitioned and clustered in a way that makes sense for the upstream queries (with explanation)
* Transformations (dbt, spark, etc)
    * 0 points: No tranformations
    * 2 points: Simple SQL transformation (no dbt or similar tools)
    * [x] 4 points: Tranformations are defined with dbt, Spark or similar technologies
* Dashboard
    * 0 points: No dashboard
    * 2 points: A dashboard with 1 tile
    * [x] 4 points: A dashboard with 2 tiles
* Reproducibility
    * 0 points: No instructions how to run code at all
    * 2 points: Some instructions are there, but they are not complete
    * [x] 4 points: Instructions are clear, it's easy to run the code, and the code works


# Further Improvements:

**Infra-Related**
- fix: Terraform was failing because of cloud api (not sure if persist)
- fix: default.tfstate for storing terraform state files and locks in the gcp bucket?
- Automate loading logic to GCP Datalocs (optional)


**Airflow Dags**
- Message Factory, to enable to load all channels messages without needing to create new dag.
For instance, following channels: course-ml-zoomcamp,announcements, announcements-course-data-engineering, book-of-the-week (book relations), general, welcome
- Adding tests

**DWH**
- fix: The BigQuery tables do not take the schema changes automatically. 
- Add some partitioning and clustering on tables
