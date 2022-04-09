terraform {
  required_version = ">= 1.0"
  backend "gcs" {
    bucket = "tf-state-dtc-capstone"
  }
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable Required API services for the project
resource "google_project_service" "iamcredentials" {
  project                    = var.project_id
  service                    = "iamcredentials.googleapis.com"
  disable_dependent_services = true
}


# Data Lake Bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name     = local.data_lake_bucket
  location = var.region

  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 // days
    }
  }

  force_destroy = true
}

# Data ware house : DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = local.bigquery_dataset
  project                    = var.project_id
  location                   = var.region
  delete_contents_on_destroy = true
}

resource "google_project_service" "cloud-composer" {
  count                      = local.cloud_composer_enabled
  project                    = var.project_id
  service                    = "composer.googleapis.com"
  disable_dependent_services = true
}

# Cloud Composer Environment
module "cloud-composer" {
  source     = "./cloud-composer"
  count      = local.cloud_composer_enabled
  project_id = var.project_id
  region     = var.region
  depends_on = [google_project_service.iamcredentials, google_project_service.cloud-composer]
}
