# data "google_service_account" "terraform-admin" {
#   account_id = "terraform-admin@dtc-capstone-344019.iam.gserviceaccount.com"
# }

resource "google_service_account" "composer_admin" {
  account_id   = "composer-admin"
  display_name = "Composer Admin"
  project      = var.project_id
}

resource "google_project_iam_member" "account_user_binding" {
  project    = var.project_id
  role       = "roles/iam.serviceAccountUser"
  member     = "serviceAccount:${google_service_account.composer_admin.email}"
  depends_on = [google_service_account.composer_admin]
}

resource "google_project_iam_member" "composer_binding" {
  project    = var.project_id
  role       = "composer.admin"
  member     = "serviceAccount:${google_service_account.composer_admin.email}"
  depends_on = [google_service_account.composer_admin]
}


resource "google_composer_environment" "composer_environment" {
  name    = local.composer_name
  region  = var.region
  project = var.project_id

  config {

    software_config {
      image_version = "composer-2.0.0-preview.3-airflow-2.1.2"
      airflow_config_overrides = {
        core-dags_are_paused_at_creation = "True"
      }
      #   pypi_packages = {
      #     numpy = ""
      #     scipy = "==1.1.0"
      #   }
      #   env_variables = {
      #     FOO = "bar"
      #   }
    }
    environment_size = "ENVIRONMENT_SIZE_SMALL"

    node_config {
      service_account = google_service_account.composer_admin.name
    }
  }
}
