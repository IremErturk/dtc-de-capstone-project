# Project Overview

In this project, I am aiming to practice different tool sets that we have learned as part of Data Talks Clubs Data Engieering Zoomcamp course.

To practice that, the **Data Talks Clubs** **Slack data** is selected as *dataset*. Therefore as final output, the project is aiming to create dashboard with analysis of, most talked topics, most used reactions, community netwpork graph, etc...

In the project includes following subfolders for respective capabilities.

| SubFolder                         | Capabilty                                                                                     |
| ----------------------------------|----------------------------------------------------------                                     |
| [.google](./.google/)             | Expected to store the google service account keys (not pushed to GitHub for security reasons) |
| [.github](./.github/workflows)    | CI/CD with GitHub Actions workflows                      |
| [iac](./iac/)                     | Infrastructure as Code for creating GCP resources        |
| [aiflow](./airflow/)              | ETL pipeline  with Airflow and Spark                     |
| [visualization](./visualization/) | Data Visualization with JupyterNotebooks and Plotly      |

---
## Infrastructure as Code (Terrafrom and Google Cloud)

To setup the required GCP resources, please follow the [IaC README](./iac/README.md)
At the end of successfully completing the steps, you will be able to see the GCP resources in GCP console including: GSC bucket,BigQuery dataset, CloudComposer, IAM access rights, etc.


## Data Ingestion with Airflow

To initiate ETL pipeline that is responsible with:
    - Ingesting Raw Data to GCS Data Lake
    - Transforming Data with Spark
    - Ingesting Transformed Data to Google Cloud Storage
    - Ingesting Data from GCS to Google BigQuery
please follow the steps in [Airflow README](./airflow/README.md).

## Visualization and Analysis

To create dashboard and visualizations please follow the [Visualization README](./visualization/README.md)


## Further Information and Readmes
- [Good Practices and Good-2-Knows](./docs/good-2-knows.md)
- [Self-Assessment and Future Improvements](./docs/project-self-assesment.md)
