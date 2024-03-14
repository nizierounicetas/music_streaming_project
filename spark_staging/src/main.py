from pyspark.sql import SparkSession

from services import StageLoader, constants


def main():

    spark = SparkSession.builder.appName().master(master="yarn").getOrCreate()

    try:
        stageLoader = StageLoader(spark)
        stageLoader.process_stream()
    finally:
        if spark is not None:
            spark.stop()


if __name__ == '__main__':
    main()


