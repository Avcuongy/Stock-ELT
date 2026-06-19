from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT_PATH = "/path/to/your/stock-elt"
PYTHON_EXEC = f"{PROJECT_PATH}/.venv/Scripts/python"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="elt",
    default_args=default_args,
    description="ELT",
    schedule="*/30 * * * *",
    start_date=datetime(2026, 6, 14),
    catchup=False,
    tags=["warehouse", "elt"],
) as dag:

    task_extract = BashOperator(
        task_id="elt_extract",
        bash_command=f"cd {PROJECT_PATH} && {PYTHON_EXEC} scripts/elt/extract.py",
    )

    task_load = BashOperator(
        task_id="elt_load",
        bash_command=f"cd {PROJECT_PATH} && {PYTHON_EXEC} scripts/elt/load.py",
    )

    task_transform = BashOperator(
        task_id="elt_transform",
        bash_command=f"cd {PROJECT_PATH} && {PYTHON_EXEC} scripts/elt/transform.py",
    )

    task_extract >> task_load >> task_transform
