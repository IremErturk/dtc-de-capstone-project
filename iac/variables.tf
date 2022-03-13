locals {
  project_name     = replace(var.project_name, "-", "_")
  data_lake_bucket = "${local.project_name}_${var.env}_data_lake"
  bigquery_dataset = "${local.project_name}_${var.env}_all_data"
}

variable "project_name" {
  description = "Your GCP Project Name"
  default     = "dtc-capstone"
  type        = string
}

variable "project_id" {
  description = "Your GCP Project ID"
  default     = "dtc-capstone-344019"
  type        = string
}

variable "state_bucket" {
  description = "Bucket name for storing terrafrom state and lock files"
  default     = "dtc_capstone_terraform_state"
  type        = string
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default     = "europe-west6"
  type        = string
}

variable "env" {
  description = "Environment for GCP resources."
  default     = "dev"
  type        = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default     = "STANDARD"
  type        = string
}
