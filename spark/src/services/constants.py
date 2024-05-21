import os

# logger settings
LOGGER_FORMAT = 'log_format: str = "%(asctime)s.%(msecs)03d [%(levelname)s] - %(name)s - %(funcName)s - %(lineno)s - %(message)s"'
LOGGER_LEVEL = 'INFO'

# spark job names
STAGE_APP_NAME = "music_stage_job"
CORE_APP_NAME = "music_core_job"

# kafka topics
LISTEN_EVENTS_TOPIC = "listen_events"
PAGE_VIEW_EVENTS_TOPIC = "page_view_events"
AUTH_EVENTS_TOPIC = "auth_events"

# core date columns
DATE_COLUMNS = {
    LISTEN_EVENTS_TOPIC: "event_ts",
    PAGE_VIEW_EVENTS_TOPIC: "event_ts",
    AUTH_EVENTS_TOPIC: "tregistration_ts"
}

# kafka bootstrap server address
KAFKA_PORT = "9092"
KAFKA_HOST = os.getenv("BROKER_IP", 'localhost')

# google cloud storage bucket name and path
GCS_BUCKET_NAME = os.getenv("STAGE_BUCKET_NAME", 'music_stage_bucket')
GCS_PATH = f'gs://{GCS_BUCKET_NAME}'

CORE_DATASET = "music_core"

STRING_COLUMNS = []
