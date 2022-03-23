import ast
import logging
import os
import re
import time
from datetime import datetime
from glob import glob

from google.cloud import storage
from pyspark.sql import SparkSession, types
from pyspark.sql.functions import col, explode, to_timestamp, udf
from pyspark.sql.types import StringType

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

PATH_TO_LOCAL_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
DATA_SOURCE_ROOT = "assets/slack-data"
CHANNEL_NAME = "course-data-engineering"

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "dtc-capstone-344019")
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc_capstone_344019_data-lake")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "dtc_capstone_344019_all_data")


interest_columns = [
    "client_msg_id",
    "parent_user_id",
    "reply_count",
    "subtype",
    "text",
    "thread_ts",
    "ts",
    "user",
]

drop_columns = [
    "attachments",
    "blocks",
    "display_as_bot",
    "edited",
    "files",
    "hidden",
    "inviter",
    "is_locked",
    "last_read",
    "latest_reply",
    "reactions",
    "replies",
    "reply_count",
    "reply_users",
    "reply_users_count",
    "root" "source_team",
    "subscribed",
    "team",
    "topic",
    "type",
    "upload",
    "user_profile",
    "user_team",
    "x_files",
]


def find_files(logical_date: str, **kwargs):
    prefix_yy_mm = "-".join(logical_date.split("-")[:-1])
    files = glob(
        f"{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix_yy_mm}-*.json"
    )

    task_instance = kwargs["ti"]
    task_instance.xcom_push(key="files", value=files)
    task_instance.xcom_push(key="prefix", value=prefix_yy_mm)
    logging.info("XCOM variable files is successfully pushed..")


def upload_file_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


def upload_files_to_gcs(bucket, object_prefix, files):
    files = ast.literal_eval(files)
    for file in files:
        filename = file.split("/")[-1]
        upload_file_to_gcs(bucket, f"{object_prefix}/{filename}", file)


def upload_local_directory_to_gcs(bucket_name, gcs_path, local_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    assert os.path.isdir(local_path)  # Works only with local_paths that are directory
    for local_file in glob(local_path + "/**", recursive=True):
        if os.path.isfile(local_file):
            remote_path = os.path.join(gcs_path, local_file[1 + len(local_path) :])
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)


def upload_df_to_gcs(bucket_obj, object_name, df):
    blob = bucket_obj.blob(object_name)
    blob.upload_from_string(df, "text/csv")


def initialize_gcp(bucket_name):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    return bucket


def initialize_spark():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName(f"{PROJECT_ID}-spark")
        .getOrCreate()
    )
    return spark


def stop_spark(spark: SparkSession):
    spark.stop()


# Group 2:
def epoch_2_datetime(epoch):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))


def clean_message_text(text):
    user_pattern = re.compile(r"<@(.+?)>")
    link_pattern_text = re.compile(r"<(http.+?)\|(.+?)>")
    link_pattern = re.compile(r"<(http.+?)>")

    text = (
        text.replace("\xa0", " ")
        .replace("•", "-")
        .replace("\n\n", "\n")
        .replace("'", "")
        .replace("`", "")
    )
    text = re.sub("\n", " ", text)
    text = user_pattern.sub("", text)
    text = link_pattern_text.sub("", text)
    text = link_pattern.sub("", text)
    return text.strip()


udf_epoch_2_datetime = udf(lambda x: epoch_2_datetime(x), StringType())
udf_clean_message_text = udf(lambda x: clean_message_text(x), types.StringType())


def extract_reactions_data(df):
    reactions_df = df.where((col("reactions").isNotNull()))
    reactions_df = reactions_df.select(["client_msg_id", "reactions"])
    reactions_df = reactions_df.withColumn("reaction", explode("reactions")).drop(
        "reactions"
    )
    reactions_df = reactions_df.select(
        ["client_msg_id", "reaction.name", "reaction.count", "reaction.users"]
    )
    return reactions_df


def transform_epoch_2_datetime(df, column_name):
    df = df.withColumn(column_name, df[column_name].cast(types.IntegerType()))
    df = df.withColumn(column_name, udf_epoch_2_datetime(col(column_name)))
    df = df.withColumn(column_name, to_timestamp(col(column_name)))
    return df


def split_root_and_thread_messages(df):
    root_level_messages = df.where((col("parent_user_id").isNull()))
    thread_level_messages = df.where((col("parent_user_id").isNotNull()))

    root_level_messages = root_level_messages.select(*interest_columns)
    # root_level_messages = root_level_messages.drop([col for col in drop_columns] + ["parent_user_id"])

    thread_level_messages = thread_level_messages.select(*interest_columns)
    return (root_level_messages, thread_level_messages)


def save_spark_df_2_local_file(spark_df, tempfile):
    spark_df.toPandas().to_csv(tempfile, header=True, index=False)


def transform_message_data(bucket_name, prefix):

    print(f"PREFIX: {prefix}")

    # file-names
    source_data_path = f"{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix}-*.json"
    target_reactions = f"clean/messages/{prefix}_reactions.csv"
    # target_messages         = f'clean/messages/{prefix}_messages.csv'
    target_messages = f"{PATH_TO_LOCAL_HOME}/{prefix}_messages.parquet"
    target_root_messages = f"clean/messages/{prefix}_root_level_messages.csv"
    target_thread_replies = f"clean/messages/{prefix}_thread_level_messages.csv"

    spark_session = initialize_spark()
    bucket = initialize_gcp(bucket_name)

    # transform 1: all_message_data for given year-month
    message_data = spark_session.read.json(source_data_path, multiLine=True)

    # transform 2: clean unwanted subtype (thread_broadcast, channel_join)
    # this step cause, all values for 'inviter' and 'root' become null
    message_data = message_data.where(
        (col("subtype").isNull())
        | ((col("subtype") != "thread_broadcast") & (col("subtype") != "channel_join"))
    )

    # # transform 3: cleanup the text column in messages.
    message_data = message_data.withColumn("text", udf_clean_message_text(col("text")))

    # transform 5: epoch to datetime.. for ts and thread_ts columns
    message_data = transform_epoch_2_datetime(message_data, "ts")
    message_data = transform_epoch_2_datetime(message_data, "thread_ts")

    # transform 6: Extract reactions data from ythje
    reactions_data = extract_reactions_data(message_data)
    upload_df_to_gcs(
        bucket,
        target_reactions,
        reactions_data.toPandas().to_csv(header=True, index=False),
    )

    # transform 7: drop unrelevant columns in messages
    # print(f"message_data (undropped):{(message_data.count(), len(message_data.columns))}")
    message_data = message_data.select(*interest_columns)
    # print(f"message_data (dropped)  :{(message_data.count(), len(message_data.columns))}")
    # print(f"remaining columns : {message_data.columns}")
    # print(f"schema : {message_data.printSchema()}")

    # print(message_data.toPandas())

    # print(message_data.show())

    message_data.write.mode("overwrite").parquet(target_messages)

    # upload_df_to_gcs(BUCKET,target_messages, message_data.toPandas().to_csv(header=True, index=False))

    # transform 7: split messages in : root_level and thread_level messages
    # root_messages, theared_replies = split_root_and_thread_messages(message_data)
    # upload_df_to_gcs(bucket,target_root_messages, root_messages.toPandas().to_csv(header=True, index=False))
    # upload_df_to_gcs(bucket,target_thread_replies, theared_replies.toPandas().to_csv(header=True, index=False))

    stop_spark(spark_session)


default_args = {
    "owner": "airflow",
    "start_date": datetime(2020, 11, 22),
    "end_date": datetime(2022, 4, 22),
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="course-data-engineering-V6",
    schedule_interval="@monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=1,
    tags=["dtc-capstone"],
) as dag:

    with TaskGroup("upload-raw-data") as upload_raw_data:

        files_for_month = PythonOperator(
            task_id="files_for_month",
            python_callable=find_files,
            provide_context=True,
            op_kwargs={"logical_date": "{{ ds }}"},
        )
        upload_raw_files = PythonOperator(
            task_id="upload_files",
            python_callable=upload_files_to_gcs,
            provide_context=True,
            op_kwargs={
                "bucket": BUCKET,
                "object_prefix": "raw/messages/data-engineering",
                "files": f'{{{{ ti.xcom_pull(key="files") }}}}',
            },
        )
        files_for_month >> upload_raw_files

    with TaskGroup("transform-message-data") as transform_data_and_save_locally:

        transform_data = PythonOperator(
            task_id="transform_data_and_save",
            python_callable=transform_message_data,
            provide_context=True,
            op_kwargs={
                "bucket_name": BUCKET,
                "prefix": f'{{{{ ti.xcom_pull(key="prefix") }}}}',
            },
        )

        transform_data

    with TaskGroup("upload-message-data-to-gcs") as upload_data_to_gcs:

        upload_messages = PythonOperator(
            task_id="messages",
            python_callable=upload_local_directory_to_gcs,
            provide_context=True,
            op_kwargs={
                "local_path": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="prefix") }}}}_messages.parquet',
                "bucket_name": BUCKET,
                "gcs_path": f"clean/messages/",
            },
        )

        # upload_root_messages = PythonOperator(
        #     task_id="root_messages",
        #     python_callable=upload_file_to_gcs,
        #     provide_context=True,
        #     op_kwargs={
        #         "bucket": BUCKET,
        #         "object_name": f'clean/messages/{{{{ ti.xcom_pull(key="prefix") }}}}_root_messages.parquet',
        #         "local_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="prefix") }}}}_root_messages2.parquet',
        #     },
        # )

        # upload_thread_replies = PythonOperator(
        #     task_id="thread_replies",
        #     python_callable=upload_file_to_gcs,
        #     provide_context=True,
        #     op_kwargs={
        #         "bucket": BUCKET,
        #         "object_name": f'clean/messages/{{{{ ti.xcom_pull(key="prefix") }}}}_thread_replies.parquet',
        #         "local_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="prefix") }}}}_thread_replies2.parquet',
        #     },
        # )

        # upload_reactions = PythonOperator(
        #     task_id="reactions",
        #     python_callable=upload_file_to_gcs,
        #     provide_context=True,
        #     op_kwargs={
        #         "bucket": BUCKET,
        #         "object_name": f'clean/messages/{{{{ ti.xcom_pull(key="prefix") }}}}_reactions.parquet',
        #         "local_file": f'{PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="prefix") }}}}_reactions.parquet',
        #     },
        # )

    # cleanup = BashOperator(
    #     task_id="cleanup",
    #     bash_command=f'rm {PATH_TO_LOCAL_HOME}/{{{{ ti.xcom_pull(key="prefix") }}}}*.parquet',
    # )

    upload_raw_data >> transform_data_and_save_locally >> upload_data_to_gcs
