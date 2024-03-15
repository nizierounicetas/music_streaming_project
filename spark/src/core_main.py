from pyspark.sql import SparkSession
import sys
import logging

from services import CoreLoader
from services import constants

def main():
    logging.basicConfig(level=constants.LOGGER_LEVEL, format=constants.LOGGER_FORMAT)
    logger = logging.getLogger(constants.CORE_APP_NAME)

    args = sys.argv
    logger.info(f'ARGS: {args}')

    if len(args) < 3:
        logger.error('No proper args: arg1 - topic, arg2 - date in dd.mm.yyyy format')
        return

    _, topic, loading_date = args

    spark = SparkSession \
        .builder \
        .master('yarn') \
        .appName(constants.CORE_APP_NAME) \
        .getOrCreate()

    try:
        CoreLoader(spark).process(topic, loading_date)
    finally:
        if spark is not None:
            spark.stop()

if __name__=='__main__':
    main()