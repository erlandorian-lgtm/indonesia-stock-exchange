from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.smtp.notifications.smtp import SmtpNotifier

default_args = {
    "owner" : "erlandobrian",
    "retries" : 2,
}

@dag(
    dag_id="ihsg_pipeline",
    default_args = default_args,
    start_date=datetime(2026,11,23),
    schedule="@daily",
    catchup=False,
    tags=["ihsg","data-engineering"],
    on_failure_callback=SmtpNotifier(
        to="erlando.rian@gmail.com",
        from_email="erlando.rian@gmail.com",
        subject="[ALERT] IHSG Pipeline Failed",
        html_content="""
        <h3>IHSG Pipeline Failure</h3>
        <p>DAG: {{ dag.dag_id }}</p>
        <p>Run ID: {{ run_id }}</p>
        <p>Failed task: {{ ti.task_id }}</p>
        <p><a href="{{ ti.log_url }}">View task logs</a></p>
        """,
        smtp_conn_id="smtp_default",
    ),
)

def ihsg_pipeline():

    @task
    def extract_data():
        from src.ingestion.download_ihsg import main as extract_ihsg
        from src.ingestion.bi_extract import main as extract_bi
        from src.ingestion.cnn_extract import main as extract_cnn

        extract_ihsg()
        extract_bi()
        extract_cnn()

    @task
    def process_data():
        from src.processing.ihsg_transform import main as process_ihsg
        from src.processing.bi_transform import main as process_bi
        from src.processing.cnn_transform import main as process_cnn

        process_ihsg()
        process_bi("bi")
        process_cnn("cnn")

    @task 
    def load_data():
        from src.processing.load_to_postgres import main as load_postgres

        load_postgres()

    @task
    def load_bigquery():
        from src.processing.load_to_bigquery import main as load_bigquery_data
        load_bigquery_data()

    extract_data() >> process_data() >> load_data() >> load_bigquery()

ihsg_pipeline()