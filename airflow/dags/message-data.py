import logging
import os
import re
import time
from datetime import datetime
from glob import glob

from config import (
    BUCKET,
    DATA_SOURCE_ROOT,
    PATH_TO_LOCAL_HOME,
    PROJECT_ID,
    message_schema,
)
from google.cloud import storage
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, lit

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.task_group import TaskGroup

TEMP_FILE_PATH = f"{PATH_TO_LOCAL_HOME}/assets/temp"

# Configure parameters:

CHANNEL_NAME = "course-data-engineering"
START_DATE = datetime(2020, 10, 22)
END_DATE = datetime(2022, 4, 22)

# CHANNEL_NAME = "course-ml-zoomcamp"
# START_DATE = datetime(2021, 6, 22)
# END_DATE = datetime(2022, 3, 22)

# CHANNEL_NAME = "welcome"
# START_DATE = datetime(2020, 9, 22)
# END_DATE = datetime(2022, 4, 22)


def check_condition(logical_date: str, **kwargs):
    prefix_yy_mm = "-".join(logical_date.split("-")[:-1])
    # Push prefix to avoid re-calculation
    task_instance = kwargs["ti"]
    task_instance.xcom_push(key="prefix", value=prefix_yy_mm)
    logging.info("XCOM variable files is successfully pushed..")

    files = glob(
        f"{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix_yy_mm}-*.json"
    )

    if len(files) == 0 or files is None:
        return "skip"
    else:
        return "upload-raw-data.upload_files"


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


def upload_files_to_gcs(bucket, object_prefix, prefix, **kwargs):
    files = glob(
        f"{PATH_TO_LOCAL_HOME}/{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix}-*.json"
    )
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


def initialize_spark():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName(f"{PROJECT_ID}-spark")
        .getOrCreate()
    )
    return spark


def stop_spark(spark: SparkSession):
    spark.stop()


# Transformation  Functions
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


def tokenize_text(text):
    # todo
    pass


def extract_reactions_data(df):
    reactions_df = df.where((col("reactions").isNotNull()))
    reactions_df = reactions_df.select(
        ["client_msg_id", "user", "channel_name", "reactions"]
    )
    reactions_df = reactions_df.withColumnRenamed("user", "msg_owner")

    reactions_df = reactions_df.withColumn("reaction", explode("reactions")).drop(
        "reactions"
    )
    reactions_df = reactions_df.select(
        [
            "client_msg_id",
            "msg_owner",
            "reaction.name",
            "reaction.count",
            "reaction.users",
            "channel_name",
        ]
    )
    reactions_df = reactions_df.withColumn("msg_reactor", explode("users"))
    drop_cols = ["users", "count"]
    reactions_df = reactions_df.drop(*drop_cols)

    return reactions_df


def transform_message_data(prefix):
    # file-names
    source_data_path = f"{DATA_SOURCE_ROOT}/{CHANNEL_NAME}/{prefix}-*.json"

    # local-file-paths
    reactions_path = f"{TEMP_FILE_PATH}/{CHANNEL_NAME}/{prefix}/reactions_{prefix}_{CHANNEL_NAME}.parquet"
    messages_path = f"{TEMP_FILE_PATH}/{CHANNEL_NAME}/{prefix}/messages_{prefix}_{CHANNEL_NAME}.parquet"
    root_messages_path = f"{TEMP_FILE_PATH}/{CHANNEL_NAME}/{prefix}/rootmessages_{prefix}_{CHANNEL_NAME}.parquet"
    thread_replies_path = f"{TEMP_FILE_PATH}/{CHANNEL_NAME}/{prefix}/threadreplies_{prefix}_{CHANNEL_NAME}.parquet"

    spark_session = initialize_spark()

    # transform 1: all_message_data for given year-month
    message_data = spark_session.read.schema(message_schema).json(
        source_data_path, multiLine=True
    )

    # transform 2: clean unwanted subtype (thread_broadcast, channel_join)
    # this step cause, all values for 'inviter' and 'root' become null
    message_data = message_data.where(
        (col("subtype").isNull())
        | ((col("subtype") != "thread_broadcast") & (col("subtype") != "channel_join"))
    )

    # transform 3: add channel-name column
    message_data = message_data.withColumn("channel_name", lit(CHANNEL_NAME))

    # transform 3: Extract reactions data
    reactions_data = extract_reactions_data(message_data)
    reactions_data = reactions_data.toPandas()
    reactions_data.to_parquet(reactions_path, index=False)

    # transform 4: drop columns that are no-more needed
    columns_to_drop = ["type", "subtype", "reactions"]
    message_data = message_data.drop(*columns_to_drop)

    # --> convert message_data pyspark dataframe to pandas dataframe
    message_data = message_data.toPandas()

    # transform 5: cleanup the text column in messages.
    message_data["text"] = message_data["text"].apply(lambda x: clean_message_text(x))
    message_data.to_parquet(messages_path, index=False)

    # transform 6: split messages in : root_level and thread_replies messages
    thread_replies = message_data[message_data.parent_user_id.notnull()]
    root_messages = message_data[message_data.parent_user_id.isnull()]

    # transform 7: epoch to datetime.. for ts and thread_ts columns
    root_messages = root_messages.astype({"ts": float, "thread_ts": float})
    root_messages["ts"] = root_messages["ts"].apply(lambda x: epoch_2_datetime(x))

    thread_replies = thread_replies.astype({"ts": float, "thread_ts": float})
    thread_replies["ts"] = thread_replies["ts"].apply(lambda x: epoch_2_datetime(x))
    thread_replies["thread_ts"] = thread_replies["thread_ts"].apply(
        lambda x: epoch_2_datetime(x)
    )

    # transform 8: drop columns that are no-more needed
    root_messages = root_messages.drop(["parent_user_id", "thread_ts"], 1)

    # -> upload the root_messages and thread_replies files in local
    root_messages.to_parquet(root_messages_path, index=False)
    thread_replies.to_parquet(thread_replies_path, index=False)

    stop_spark(spark_session)


default_args = {
    "owner": "airflow",
    "start_date": START_DATE,
    "end_date": END_DATE,
    "depends_on_past": False,
    "retries": 3,
}


with DAG(
    dag_id="channels-data-pipeline",
    schedule_interval="@monthly",
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=["dtc-capstone"],
) as dag:

    prep_tasks = BranchPythonOperator(
        task_id="check-data-availability",
        python_callable=check_condition,
        provide_context=True,
        op_kwargs={"logical_date": "{{ ds }}"},
    )

    to_skip = DummyOperator(dag=dag, task_id="skip")

    with TaskGroup("upload-raw-data") as upload_raw_data:
        upload_raw_files = PythonOperator(
            task_id="upload_files",
            python_callable=upload_files_to_gcs,
            provide_context=True,
            op_kwargs={
                "bucket": BUCKET,
                "object_prefix": f"raw/message-data/{CHANNEL_NAME}",
                "prefix": f'{{{{ ti.xcom_pull(key="prefix") }}}}',
            },
        )

    with TaskGroup(
        "data-cleanup-and-transformation"
    ) as data_cleanup_and_transformation:

        prep = BashOperator(
            task_id="prep",
            bash_command=f'mkdir -p {TEMP_FILE_PATH}/{CHANNEL_NAME}/{{{{ ti.xcom_pull(key="prefix") }}}}',
        )

        transform_data = PythonOperator(
            task_id="transform_data",
            python_callable=transform_message_data,
            provide_context=True,
            op_kwargs={
                "prefix": f'{{{{ ti.xcom_pull(key="prefix") }}}}',
            },
        )

        prep >> transform_data

    with TaskGroup("upload-transformed-data-to-gcs") as upload_transfered_data_to_gcs:
        upload_messages = PythonOperator(
            task_id="messages",
            python_callable=upload_local_directory_to_gcs,
            provide_context=True,
            op_kwargs={
                "bucket_name": BUCKET,
                "gcs_path": f"clean/message-data",
                "local_path": f'{TEMP_FILE_PATH}/{CHANNEL_NAME}/{{{{ ti.xcom_pull(key="prefix") }}}}',
            },
        )

    cleanup = BashOperator(
        task_id="cleanup-temporary-files",
        bash_command=f'rm -rf {TEMP_FILE_PATH}/{CHANNEL_NAME}/{{{{ ti.xcom_pull(key="prefix") }}}}/',
    )

    (
        prep_tasks
        >> upload_raw_data
        >> data_cleanup_and_transformation
        >> upload_transfered_data_to_gcs
        >> cleanup
    )
    prep_tasks >> to_skip
