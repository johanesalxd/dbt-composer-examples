# dags/check_installed_packages_dag.py

import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "start_date": days_ago(1),
}

with DAG(
    dag_id="check_installed_python_packages",
    default_args=default_args,
    description="A simple DAG to list installed Python packages using 'pip freeze'",
    schedule_interval=None,
    catchup=False,
    tags=["utility", "debug"],
) as dag:

    list_all_packages_task = BashOperator(
        task_id="list_all_python_packages_via_pip_freeze",
        bash_command="pip freeze",
        doc_md="""\
#### Task Documentation
This task executes `pip freeze` to list all Python packages and their versions
installed in the Airflow worker environment. The output will be available in the task logs.
        """,
    )
