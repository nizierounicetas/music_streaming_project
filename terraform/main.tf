provider "google" {
  project = "music-streaming-project"
  region  = "us-central1"
  zone    = "us-central1-c"
}

resource "google_compute_instance" "eventism_vm" {
  name                      = "music-streaming-eventism-vm"
  machine_type              = "e2-standard-2"
  tags                      = ["eventsim"]
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

