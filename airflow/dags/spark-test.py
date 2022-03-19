from airflow import DAG
import sys
import os
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator

import pyspark
from pyspark.sql import SparkSession, functions
from datetime import datetime, timedelta
from operator import add
from random import random

dataset_file = "yellow_tripdata_2021-01.csv"
dataset_url = f"https://s3.amazonaws.com/nyc-tlc/trip+data/{dataset_file}"
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")


def f(_):
    x = random() * 2 - 1
    y = random() * 2 - 1
    return 1 if x ** 2 + y ** 2 <= 1 else 0

def simple_test():
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName('test') \
        .getOrCreate()

    print(spark)

    partitions = 3
    n = 100000 * partitions

    count = spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
    print("Pi is roughly %f" % (4.0 * count / n))

def read_file():
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName('test') \
        .getOrCreate()

    df = spark.read \
    .option("header", "true") \
    .csv(f'{path_to_local_home}/{dataset_file}')

    df.show()

   

###############################################
# DAG Definition
###############################################
now = datetime.now()

default_args = {
    "owner": "airflow",
    "start_date": datetime(2020, 11, 18),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 10,
    "retry_delay": timedelta(minutes=1)
}


dag = DAG(
        dag_id="spark-test", 
        description="This DAG runs a simple Pyspark app.",
        default_args=default_args, 
        schedule_interval=timedelta(1),
        max_active_runs=2,

    )

download_dataset_task = BashOperator(
    task_id="download_dataset_task",
    bash_command=f"curl -sS {dataset_url} > {path_to_local_home}/{dataset_file}",
    dag=dag
)

start_job = DummyOperator(task_id="start-job", dag=dag)

first_job = PythonOperator(
    task_id="first_job",
    python_callable=read_file, # Spark application path created in airflow and spark cluster
    dag=dag)

end_job = DummyOperator(task_id="end", dag=dag)

download_dataset_task >> start_job >> first_job >> end_job
