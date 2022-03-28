import os

from pyspark.sql import types

# Google Cloud configuration parameters
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "dtc-capstone-344019")
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc_capstone_344019_data-lake")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "dtc_capstone_344019_all_data")

# Airflow parameters
PATH_TO_LOCAL_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
DATA_SOURCE_ROOT = "assets/slack-data"


# Data specific paramters
message_schema = types.StructType(
    [
        types.StructField("client_msg_id", types.StringType(), False),
        types.StructField("parent_user_id", types.StringType(), True),
        types.StructField("text", types.StringType(), True),
        types.StructField("type", types.StringType(), True),
        types.StructField("subtype", types.StringType(), True),
        types.StructField("user", types.StringType(), True),
        types.StructField("ts", types.StringType(), True),
        types.StructField("thread_ts", types.StringType(), True),
        types.StructField("reply_count", types.IntegerType(), True),
        types.StructField(
            "reactions",
            types.ArrayType(
                types.StructType(
                    [
                        types.StructField("count", types.LongType(), True),
                        types.StructField("name", types.StringType(), True),
                        types.StructField(
                            "users", types.ArrayType(types.StringType(), True), True
                        ),
                    ]
                )
            ),
            True,
        ),
    ]
)


user_schema = types.StructType(
    [
        types.StructField("deleted", types.BooleanType(), True),
        types.StructField("id", types.StringType(), True),
        types.StructField("is_admin", types.BooleanType(), True),
        types.StructField("is_app_user", types.BooleanType(), True),
        types.StructField("is_bot", types.BooleanType(), True),
        types.StructField("is_email_confirmed", types.BooleanType(), True),
        types.StructField("is_invited_user", types.BooleanType(), True),
        types.StructField("is_owner", types.BooleanType(), True),
        types.StructField("is_primary_owner", types.BooleanType(), True),
        types.StructField("is_restricted", types.BooleanType(), True),
        types.StructField("is_ultra_restricted", types.BooleanType(), True),
        types.StructField("name", types.StringType(), True),
        types.StructField("real_name", types.StringType(), True),
        types.StructField("tz", types.StringType(), True),
        types.StructField("tz_label", types.StringType(), True),
        types.StructField("tz_offset", types.IntegerType(), True),
        types.StructField("updated", types.LongType(), True),
    ]
)
