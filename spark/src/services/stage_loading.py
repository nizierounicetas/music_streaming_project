from pyspark.sql import SparkSession, DataFrame
import logging

from pyspark.sql.functions import from_json, col, year, month, dayofmonth, hour
from pyspark.sql.streaming import DataStreamWriter
from pyspark.sql.types import StructType

import constants
import schemas

class StageLoader:

    def __init__(self, spark: SparkSession):
        self._spark = spark
        self._logger = logging.getLogger(constants.APP_NAME)

    def _read_stream_from_kafka(self, boostrap_server: str, topic: str, offset: str = "earliest") -> DataFrame:
        """
        Private method to read stream as DataFrame from Apache Kafka
        :param boostrap_server: kafka.boostrap.servers option
        :param topic: kafka topic for the particular Dataframe
        :param offset: offset which is used for starting getting data from kafka topic
        :returns: stream as Dataframe
        """
        df = self._spark.readStream \
                   .format("kafka") \
                   .option("kafka.bootstrap.servers", boostrap_server) \
                   .option("failOnDataLoss", False) \
                   .option("startingOffsets", offset) \
                   .option("subscribe", topic) \
                   .load()

        return df

    def _parse_df(self, df: DataFrame, schema: StructType) -> DataFrame:
        """
        Private method to parse data from raw kafka Dataframe's value field and
        build struct Dataframe with schema usage, cast ts field to timestamp,
        add year, month, day, hour fields on ts field for further usage in partitioning
        :param df: raw Dataframe stream from Kafka
        :param schema: expected schema of the Dataframe
        :returns: struct processed Dataframe
        """
        df = df \
            .selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("temp")) \
            .select("temp.*")

        df = df \
            .withColumn("ts", (col("ts") / 1000).cast("timestamp")) \

        df = df.withColumn("year", year(col("ts"))) \
            .withColumn("month", month(col("ts"))) \
            .withColumn("day", dayofmonth(col("ts"))) \
            .withColumn("hour", hour(col("ts")))

        return df

    def _get_stream_writer_to_parquet(self, df: DataFrame, storage_path: str, checkpoint_path: str,
                                      trigger: str, output_mode: str) -> DataStreamWriter:
        """
        Private method to get parquet format stream writer of the particular stream Dataframe
        :param df: processed Dataframe stream from Kafka
        :param storage_path: path for data storing in parquet files
        :param checkpoint_path: path for storing execution progress, useful to recover from errors
        :param trigger: processingTime property for trigger
        :param output_mode: outputmode: append, update, complete
        :returns: DataStreamWriter
        """
        stream_writer = df.writeStream \
            .format("parquet") \
            .partitionBy("year", "month", "day", "hour") \
            .option("path", storage_path) \
            .option("checkpointLocation", checkpoint_path) \
            .trigger(processingTime=trigger) \
            .outputMode(output_mode)

        return stream_writer

    def process_stream(self):
        """
        Public method for processing data streams for listen events, page view events, auth events:
        reading from Kafka and writing to Google Cloud Storage
        """
        df_meta = [(constants.AUTH_EVENTS_TOPIC, schemas.auth_events_schema),
                   (constants.PAGE_VIEW_EVENTS_TOPIC, schemas.page_view_events_schema),
                   (constants.LISTEN_EVENTS_TOPIC, schemas.listen_events_schema)]

        dfs = [self._read_stream_from_kafka(f'{constants.KAFKA_HOST}:{constants.KAFKA_PORT}', topic, "earliest")
               for topic, _ in df_meta]

        dfs = [self._parse_df(dfs[i], df_meta[i][1]) for i in range(len(dfs))]

        df_writers = [self._get_stream_writer_to_parquet(dfs[i], f'{constants.GCS_PATH}/{df_meta[i][0]}/data/',
                                                         f'{constants.GCS_PATH}/{df_meta[i][0]}/checkpoints/',
                                                         "120 seconds", "append") for i in range(len(dfs))]

        for writer in df_writers:
            writer.start()

        self._spark.streams.awaitAnyTermination()











