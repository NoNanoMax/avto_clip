from airflow.decorators import dag, task

import logging

logging.basicConfig(filename="dags.log", level=logging.INFO)
_LOG = logging.getLogger()
_LOG.addHandler(logging.StreamHandler())

@dag(
    dag_id="test_pipe"
)
def test_pipe():

    @task
    def start():
        print("1")

    start()

test_pipe()
