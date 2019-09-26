"""
Code that goes along with the Airflow tutorial located at:
https://github.com/apache/incubator-airflow/blob/master/airflow/example_dags/tutorial.py
"""
import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

crawler_path = "/home/haohsiang/spider591/"

default_args = {
    'owner': 'haohsiang',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'email': ['haohsiang51@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('crawler_591', default_args=default_args)

t1 = BashOperator(
    task_id='scrapy',
    bash_command='cd {} && scrapy crawl rent_591_crawler'.format(crawler_path),
    dag=dag)

t2 = BashOperator(
    task_id='report_status',
    bash_command='echo "I am Finished ,Please checkout ~"',
    dag=dag)

t2.set_upstream(t1)