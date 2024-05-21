terraform {
  required_version = ">=1.0"
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  project = "music-streaming-project"
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_compute_instance" "eventsim_vm" {
  name                      = "music-streaming-eventism-vm"
  machine_type              = "e2-standard-4"
  tags                      = ["kafka"]
  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 15
    }
  }

  network_interface {
    network = "default"
    access_config {
    }
  }
}

resource "google_compute_instance" "airflow_vm" {
  name                      = "airflow-vm"
  machine_type              = "e2-standard-4"
  zone                      = "us-west1-b"
  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 15
    }
  }

  network_interface {
    network = "default"
    access_config {
    }
  }
}

resource "google_storage_bucket" "music_stage_bucket" {
  name          = "music_stage_bucket"
  location      = "us-central1"
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 # in days
    }
  }
}

resource "google_compute_firewall" "kafka_firewall" {
  name    = "kafka-"
  network = "default"
  project = "music-streaming-project"

  allow {
    protocol = "tcp"
    ports    = ["9092"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["kafka"]
}


resource "google_dataproc_cluster" "music_dataproc_cluster" {
  name   = "stage-streaming"
  region = "us-central1"
  project = "music-streaming-project"

  cluster_config {
    gce_cluster_config {
      zone = "us-central1-c"
    }

    master_config {
      num_instances = 1
      machine_type  = "n2-standard-4"

      disk_config {
        boot_disk_type    = "pd-balanced"
        boot_disk_size_gb = 30
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "n2-standard-4"

      disk_config {
        boot_disk_type    = "pd-balanced"
        boot_disk_size_gb = 30
      }
    }

    software_config {
      image_version = "2.1-debian11"
    }
  }
}

resource "google_bigquery_dataset" "core_dataset" {
  dataset_id                 = "music_core"
  project                    = "music-streaming-project"
  location                   = "us-central1"
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "dm_dataset" {
  dataset_id                 = "music_dm"
  project                    = "music-streaming-project"
  location                   = "us-central1"
  delete_contents_on_destroy = true
}