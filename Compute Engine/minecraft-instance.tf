locals {
  instance_name = "instance-minecraft-${formatdate("YYYY-MM-DD", timestamp())}"
  disk_name = "disk-minecraft-${formatdate("YYYY-MM-DD", timestamp())}"
}

provider "google" {
  project = "minecraft-host-465119" 
  region  = "southamerica-east1"
  zone = "southamerica-east1-b"
}

resource "google_compute_disk" "default" {
  name  = local.disk_name
  type  = "pd-standard"
  size  = 10
}

resource "google_compute_instance" "default" {
  name = local.instance_name 

  attached_disk {
    source      = google_compute_disk.default.self_link 
    device_name = local.disk_name 
    mode        = "READ_WRITE"
  }

  boot_disk {
    auto_delete = true
    device_name = local.instance_name 

    initialize_params {
      image = "projects/ubuntu-os-cloud/global/images/ubuntu-minimal-2504-plucky-amd64-v20250708"
      size  = 10
      type  = "pd-balanced"
    }

    mode = "READ_WRITE"
  }

  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false

  labels = {
    goog-ec-src = "vm_add-tf"
  }

  machine_type = "e2-medium"

  metadata = {
    startup-script = file("${path.module}/startup_script.sh") 
  }

  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }

    queue_count = 0
    stack_type  = "IPV4_ONLY"
    subnetwork  = "projects/minecraft-host-465119/regions/southamerica-east1/subnetworks/default"
  }

  tags = ["minecraft-server"] 
  

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = "834580746470-compute@developer.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/devstorage.read_only", "https://www.googleapis.com/auth/logging.write", "https://www.googleapis.com/auth/monitoring.write", "https://www.googleapis.com/auth/service.management.readonly", "https://www.googleapis.com/auth/servicecontrol", "https://www.googleapis.com/auth/trace.append"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }

}

