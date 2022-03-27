import time

from google.cloud import bigquery
from google.cloud.bigquery.client import Client

KEY_PATH = "../.google/credentials/terraform-admin.json"

# Google Cloud Parameter
PROJECT_NAME = "dtc-capstone-344019"
GCS_BUCKET = "dtc_capstone_344019_data-lake"
DATASET_NAME = "dtc_capstone_344019_all_data"

# BigQuery Tables for users
EXTERNAL_TABLE_USERS = f"{PROJECT_NAME}.{DATASET_NAME}.ext_users"
EXTERNAL_TABLE_USERS_IDENTITY = f"{PROJECT_NAME}.{DATASET_NAME}.ext_users_identity"
EXTERNAL_TABLE_USERS_LOCATION = f"{PROJECT_NAME}.{DATASET_NAME}.ext_users_location"
EXTERNAL_TABLE_USERS_STATUS = f"{PROJECT_NAME}.{DATASET_NAME}.ext_users_status"

# BigQuery Tables for messages
TABLE_REACTIONS = f"{PROJECT_NAME}.{DATASET_NAME}.reactions_course-data-engineering"
TABLE_ROOT_MESSAGES = (
    f"{PROJECT_NAME}.{DATASET_NAME}.root_messages_course-data-engineering"
)
TABLE_THREAD_REPLIES = (
    f"{PROJECT_NAME}.{DATASET_NAME}.thread_replies_course-data-engineering"
)


def get_query_estimates(client: Client, query: str):
    job_config = bigquery.QueryJobConfig()
    job_config.dry_run = True
    job_config.use_query_cache = False

    query_job = client.query(
        (query),
        job_config=job_config,
    )
    print(
        "Estimated: This query will process {} bytes".format(
            query_job.total_bytes_processed
        )
    )


def run_query(client: Client, query: str):
    get_query_estimates(client, query)
    query_job = client.query(query)
    while not query_job.done():
        time.sleep(1)
    print(
        "Actual: This query processed {} bytes".format(query_job.total_bytes_processed)
    )
    df = query_job.to_dataframe()
    return df
