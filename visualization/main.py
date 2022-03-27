from google.cloud import bigquery
from google.oauth2 import service_account

from config import run_query
from config import TABLE_ROOT_MESSAGES
from word_cloud import populate_wordcloud

from config import KEY_PATH

def read_data_from_bigQuery(client, table_name):
    # read data from google cloud
    query_     = """SELECT text FROM `{table_name}`"""
    query      = query_.format(table_name=table_name)
    df         = run_query(client, query)
    return df


if __name__ == "__main__":
    
    # Setup BigQuery Client by Service Account key
    # Reference: https://cloud.google.com/bigquery/docs/authentication/service-account-file
    credentials = service_account.Credentials.from_service_account_file(
        KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

    # create wordcloud figure
    df_root_messages = read_data_from_bigQuery(client=client,table_name=TABLE_ROOT_MESSAGES)
    populate_wordcloud(df_root_messages)

    # create network_graph



