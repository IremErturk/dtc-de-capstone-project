data "google_project" "dtc-capstone" {
  project_id = var.project_id
}

# Enable API Services
resource "google_project_service" "cloud-composer" {
  project                    = var.project_id
  service                    = "composer.googleapis.com"
  disable_dependent_services = true
}

resource "google_project_service" "iam" {
  project                    = var.project_id
  service                    = "iam.googleapis.com"
  disable_dependent_services = true
}

# Reference: default Compute Engine Service Account
data "google_compute_default_service_account" "default" {
  project    = var.project_id
  depends_on = [google_project_service.iam]
}
resource "google_project_iam_member" "default_editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

## TODO: replace with defauly service account
## https://cloud.google.com/composer/docs/composer-2/create-environments
## Access Control: https://cloud.google.com/composer/docs/composer-2/access-control
# resource "google_service_account" "composer_admin" {
#   account_id   = "composer-admin"
#   display_name = "Composer Admin"
#   project      = var.project_id
# }

# resource "google_project_iam_member" "composer-editor" {
#   project = var.project_id
#   role    = "roles/editor"
#   member  = "serviceAccount:${google_service_account.composer_admin.email}"
# }

# resource "google_project_iam_member" "composer_worker" {
#   project = var.project_id
#   role    = "roles/composer.worker"
#   member  = "serviceAccount:${google_service_account.composer_admin.email}"
# }

# resource "google_project_iam_member" "account_user" {
#   project = var.project_id
#   role    = "roles/iam.serviceAccountUser"
#   member  = "serviceAccount:${google_service_account.composer_admin.email}"
# }

# resource "google_project_iam_member" "composer_admin" {
#   project = var.project_id
#   role    = "roles/composer.environmentAndStorageObjectAdmin"
#   member  = "serviceAccount:${google_service_account.composer_admin.email}"
# }

## resource "google_project_iam_member" "account_token" {
##   project = var.project_id
##   role    = "roles/iam.serviceAccountTokenCreator"
##   member  = "serviceAccount:${google_service_account.composer_admin.email}"
## }


# Cloud Composer Service Agent account
# Reference: https://cloud.google.com/composer/docs/composer-2/create-environments#grant-permissions 

resource "google_project_iam_member" "service_agent_v2ext" {
  project = var.project_id
  role    = "roles/composer.ServiceAgentV2Ext" # iam.serviceAccounts.setIamPolicy , iam.serviceAccounts.getIamPolicy
  member  = "serviceAccount:service-${data.google_project.dtc-capstone.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "service_agent" {
  project = var.project_id
  role    = "roles/composer.serviceAgent"
  member  = "serviceAccount:service-${data.google_project.dtc-capstone.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:service-${data.google_project.dtc-capstone.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}


# TODO: Workload Identity and Cluster Creation 
# https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#gcloud
# https://stackoverflow.com/questions/69677805/workload-identity-service-accounts-for-composer-2-gke-autopilot-cluster-podo


# Cloud Composer Environmet
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/composer_environment
# TODO: google_compute_network, google_compute_subnetwork 
resource "google_composer_environment" "composer_environment" {
  name    = local.composer_name
  region  = var.region
  project = var.project_id

  config {

    software_config {
      image_version = "composer-2.0.7-airflow-2.2.3"
      airflow_config_overrides = {
        core-dags_are_paused_at_creation = "True"
      }
    }
    environment_size = "ENVIRONMENT_SIZE_SMALL"
  }
}
