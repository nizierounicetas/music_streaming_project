import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

from .constants import *

class CoreLoader:
    def __init__(self, spark: SparkSession):
        self._spark = spark

    def process(self, topic: str, loading_date: str):
        df = self._spark.read.parquet(f"{GCS_PATH}/{topic}/data/")
        day, month, year = [int(v) for v in loading_date.split('.')]

        df = df.filter(df["year"] == lit(year) & df["month"] == lit(month) & df["day"] == lit(day))

        df.show()
        df.printSchema()

        df.write.format("bigquery").option('table', f'{CORE_DATASET}.{topic}').mode('append').save()