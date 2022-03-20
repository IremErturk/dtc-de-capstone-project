locals {
  composer_name = "${var.project_id}-composer-test"
}

variable "project_id" {
  description = "Your GCP Project ID"
  default     = "dtc-capstone-344019"
  type        = string
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default     = "europe-west6"
  type        = string
}

