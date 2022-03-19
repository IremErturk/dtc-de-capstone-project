from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from pyspark.sql import SparkSession, functions
from datetime import datetime, timedelta

###############################################
# Parameters
###############################################
spark_master = "spark://spark:7077"
spark_app_name = "Spark Hello World"
file_path = "/home/spark/resources/data/airflow.cfg"

###############################################
# DAG Definition
###############################################
now = datetime.now()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG(
        dag_id="spark-test4", 
        description="This DAG runs a simple Pyspark app.",
        default_args=default_args, 
        schedule_interval=timedelta(1)
    )

start = DummyOperator(task_id="start", dag=dag)

spark_job = PythonOperator(
    task_id="spark_job",
    python_callable="/home/spark/app/hello-world.py", # Spark application path created in airflow and spark cluster
    dag=dag)

end = DummyOperator(task_id="end", dag=dag)

start >> spark_job >> end