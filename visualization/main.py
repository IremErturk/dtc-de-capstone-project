import sys

from config import (
    EXTERNAL_TABLE_USERS,
    EXTERNAL_TABLE_USERS_IDENTITY,
    KEY_PATH,
    TABLE_REACTIONS,
    TABLE_ROOT_MESSAGES,
    TABLE_THREAD_REPLIES,
    run_query,
)
from core import create_messages_bar_chart, reaction_hotness, users_timezones
from google.cloud import bigquery
from google.oauth2 import service_account
from network_graph import populate_network
from word_cloud import populate_wordcloud


def read_data_from_BQ(client, query):
    df = run_query(client, query)
    return df


if __name__ == "__main__":
    env_info = sys.argv[1]

    if env_info == "github-actions":
        client = bigquery.Client()
    elif env_info == "local":
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
    else:
        print("Useage python main.py <local|github-actions")
        exit(1)

    # core message counts over time analysis
    query_ = """
        SELECT
            FORMAT_TIMESTAMP('%Y-%m-%d', DATETIME(ts)) date,
            COUNT(*) events,
        FROM `{table_name}`
        GROUP BY date
    """
    df_root_messages = read_data_from_BQ(
        client=client, query=query_.format(table_name=TABLE_ROOT_MESSAGES)
    )
    df_thread_replies = read_data_from_BQ(
        client=client, query=query_.format(table_name=TABLE_THREAD_REPLIES)
    )
    create_messages_bar_chart(df_root_messages, df_thread_replies)

    # core time zones that users associated
    query_ = """SELECT tz, tz_label, tz_offset FROM `{table_name}` """
    query = query_.format(table_name=EXTERNAL_TABLE_USERS)
    df_locations = run_query(client, query)  # tz, tz_label, tz_offset

    users_timezones(df_locations)

    # core most used reactions
    query = f"""SELECT * FROM `{TABLE_REACTIONS}`"""
    df_reactions = read_data_from_BQ(client=client, query=query)
    reaction_hotness(df_reactions)

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
