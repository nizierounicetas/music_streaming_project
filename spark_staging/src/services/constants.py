# Kafka Topics
import os

APP_NAME = "music_streaming_process"

# kafka topics variables
LISTEN_EVENTS_TOPIC = "listen_events"
PAGE_VIEW_EVENTS_TOPIC = "page_view_events"
AUTH_EVENTS_TOPIC = "auth_events"

# kafka bootstrap server address
KAFKA_PORT = "9092"
KAFKA_HOST = os.getenv("BROKER_IP", 'localhost')

# google cloud storage bucket name and path
GCS_BUCKET_NAME = os.getenv("STAGE_BUCKET_NAME", 'music_stage_bucket')
GCS_PATH = f'gs://{GCS_BUCKET_NAME}'
