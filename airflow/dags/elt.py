from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.sensors.external_task import ExternalTaskSensor

PROJECT_PATH = "/path/to/your/stock-elt"
PYTHON_EXEC = f"{PROJECT_PATH}/.venv/Scripts/python"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="2_data_warehouse_elt",
    default_args=default_args,
    description="Phase 2: Extract from Source, Load and Transform in DuckDB",
    schedule_interval="0 1 * * *",
    start_date=datetime(2026, 6, 11),
    catchup=False,
    tags=["warehouse", "elt"],
) as dag:

    wait_for_backend = ExternalTaskSensor(
        task_id="wait_for_backend_source",
        external_dag_id="1_backend_source_pipeline",
        external_task_id="backend_load",
        allowed_states=["success"],
        execution_delta=timedelta(seconds=0),
        timeout=3600,
        poke_interval=60,
    )

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

    # Thiết lập luồng chạy tuần tự
    wait_for_backend >> task_extract >> task_load >> task_transform
