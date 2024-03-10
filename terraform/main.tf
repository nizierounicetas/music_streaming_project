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

resource "google_compute_instance" "eventism_vm" {
  name                      = "music-streaming-eventism-vm"
  machine_type              = "e2-standard-2"
  tags                      = ["eventsim", "kafka"]
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

resource "google_storage_bucket" "music_streaming_bucket" {
  name          = "music_streaming_stage"
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

resource "google_dataproc_cluster" "stage_streaming" {
  name   = "stage-streaming"
  region = "us-central1"
  project = "music-streaming-project"

  cluster_config {
    gce_cluster_config {
      zone = "us-central1-c"
    }

    master_config {
      num_instances = 1
      machine_type  = "n2-standard-2"

      disk_config {
        boot_disk_type    = "pd-balanced"
        boot_disk_size_gb = 30
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "n2-standard-2"

      disk_config {
        boot_disk_type    = "pd-balanced"
        boot_disk_size_gb = 30
      }
    }

    software_config {
      image_version = "2.1-debian11"
      optional_components = ["JUPYTER"]
    }
  }
}
