FROM marketplace.gcr.io/google/airflow2

USER root

RUN apt-get update && \
    ACCEPT_EULA=Y apt-get upgrade -y && \
    apt-get install -y git
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PROJECT_ID=${PROJECT_ID}
ENV DATAPROC_CLUSTER_NAME=${DATAPROC_CLUSTER_NAME}
ENV REGION=${REGION}

USER ${AIRFLOW_UID}