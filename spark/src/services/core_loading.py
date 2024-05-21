import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, expr

import constants


class CoreLoader:
    def __init__(self, spark: SparkSession):
        self._spark = spark

    def process(self, topic: str, loading_date: str, date_column: str):

        day, month, year = [int(v) for v in loading_date.split('.')]

        max_existing_date_df = self._spark.read.format("bigquery").option("dataset", constants.CORE_DATASET) \
            .option("table", f"(SELECT MAX(CAST(t.{date_column} AS DATE)) AS max_date FROM {constants.CORE_DATASET}{topic} t)") \
            .load()

        if not max_existing_date_df.rdd.isEmpty():
            max_existing_date = max_existing_date_df.collect()[0]['max_date']
            if not (max_existing_date < datetime.date(year, month, day)):
                return

        df = self._spark.read.parquet(f"{constants.GCS_PATH}/{topic}/data/")

        df = df.filter(df["year"] == lit(year) & df["month"]
                       == lit(month) & df["day"] == lit(day))

        df = df.drop(col('year'), col('month'), col('day'))

        df = df.withColumnRenamed('ts', date_column)

        df = df.withColumn("sk", expr("uuid()"))

        df.show()
        df.printSchema()

        df.write.format("bigquery").option(
            'table', f'constants{constants.CORE_DATASET}.{topic}').mode('append').save()
