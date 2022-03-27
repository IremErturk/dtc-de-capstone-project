from config import (
    EXTERNAL_TABLE_USERS_IDENTITY,
    KEY_PATH,
    TABLE_REACTIONS,
    TABLE_ROOT_MESSAGES,
    TABLE_THREAD_REPLIES,
    run_query,
)
from google.cloud import bigquery
from google.oauth2 import service_account
from network_graph_pyvis import populate_network
from word_cloud import populate_wordcloud


def read_data_from_BQ(client, query):
    df = run_query(client, query)
    return df


if __name__ == "__main__":

    # Setup BigQuery Client by Service Account key
    # Reference: https://cloud.google.com/bigquery/docs/authentication/service-account-file
    credentials = service_account.Credentials.from_service_account_file(
        KEY_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )

    # create wordcloud figure
    query = f"""SELECT text FROM `{TABLE_ROOT_MESSAGES}`"""
    df_root_messages = read_data_from_BQ(client=client, query=query)
    populate_wordcloud(df_root_messages)  # skip for now

    # create network_graph
    query = f"""SELECT * FROM `{EXTERNAL_TABLE_USERS_IDENTITY}`"""
    df_users = read_data_from_BQ(client=client, query=query)
    df_users = df_users.drop(df_users[df_users.id == "id"].index)
    df_users = df_users[df_users["id"].notna()]

    query = f"""SELECT user, parent_user_id FROM `{TABLE_THREAD_REPLIES}`"""
    df_thread_replies = read_data_from_BQ(client=client, query=query)
    populate_network(
        "thread_replies", df_users, df_thread_replies, ["parent_user_id", "user"]
    )

    query = f"""SELECT msg_owner, msg_reactor FROM `{TABLE_REACTIONS}`"""
    df_reactions = read_data_from_BQ(client=client, query=query)
    populate_network("reactions", df_users, df_reactions, ["msg_owner", "msg_reactor"])
