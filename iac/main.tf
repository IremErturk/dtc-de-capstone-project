terraform {
  required_version = ">= 1.0"
  backend "gcs" {
    bucket = var.state_bucket_name
    prefix = var.env
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
  // credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
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

# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = local.bigquery_dataset
  project    = var.project_id
  location   = var.region
}