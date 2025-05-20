# dags/my_dbt_dag.py

import datetime
import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# --- Configuration ---
DBT_PROJECT_DIR = "/home/airflow/gcs/dags/my_dbt_project"
DBT_PROFILE_DIR = "/home/airflow/gcs/dags/my_dbt_project"
DBT_TARGET = "dev"
GCP_PROJECT_ID = os.getenv("GCP_PROJECT", "my-gcp-project")
DBT_BIGQUERY_DATASET = "dbt_transformed_data"

current_path = os.environ.get("PATH", "")
DBT_ENV_VARS = {
    "PATH": current_path,
    "DBT_BIGQUERY_PROJECT": GCP_PROJECT_ID,
    "DBT_BIGQUERY_DATASET": DBT_BIGQUERY_DATASET,
    "DBT_PROFILES_DIR": DBT_PROFILE_DIR
}


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=5),
    "start_date": days_ago(1),
    "cwd": DBT_PROJECT_DIR,
    "env": DBT_ENV_VARS,
}

with DAG(
    dag_id="dbt_bigquery_transformations",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["dbt", "bigquery"],
    doc_md="DAG to run dbt transformations for BigQuery",
) as dag:

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"dbt deps --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILE_DIR}",
        # cwd=DBT_PROJECT_DIR,
        # env=DBT_ENV_VARS,
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"dbt seed --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILE_DIR} --target {DBT_TARGET} --full-refresh",
        # cwd=DBT_PROJECT_DIR,
        # env=DBT_ENV_VARS,
        # Add --full-refresh if you want to overwrite existing seed tables
    )

    dbt_compile = BashOperator(
        task_id="dbt_compile",
        bash_command=f"dbt compile --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILE_DIR} --target {DBT_TARGET}",
        # cwd=DBT_PROJECT_DIR,
        # env=DBT_ENV_VARS,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILE_DIR} --target {DBT_TARGET}",
        # cwd=DBT_PROJECT_DIR,
        # env=DBT_ENV_VARS,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"dbt test --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILE_DIR} --target {DBT_TARGET}",
        # cwd=DBT_PROJECT_DIR,
        # env=DBT_ENV_VARS,
    )

    # Define task dependencies
    dbt_deps >> dbt_seed >> dbt_compile >> dbt_run >> dbt_test
