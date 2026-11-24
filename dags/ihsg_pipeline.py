from airflow.decorators import dag, task
from datetime import datetime

default_args = {
    "owner" : "erlandobrian",
    "retries" : 2,
    "email" : ["erlando.rian@gmail.com"],
    "email_on_failure" : True,
    "email_on_retry" : False,
}

@dag(
    dag_id="ihsg_pipeline",
    default_args = default_args,
    start_date=datetime(2026,11,23),
    schedule="@daily",
    catchup=False,
    tags=["ihsg","data-engineering"]
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

    extract_data() >> process_data() >> load_data()

ihsg_pipeline()