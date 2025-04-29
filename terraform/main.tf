###############################################################################
# Provider and required APIs
###############################################################################
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = "sentiment-analysis-app-455917"
  region  = "europe-west1"
}

provider "google-beta" {
  project = "sentiment-analysis-app-455917"
  region  = "europe-west1"
}

###############################################################################
# Enable required services
###############################################################################
resource "google_project_service" "enable_cloud_run" {
  project            = var.project
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "enable_artifact_registry" {
  project            = var.project
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "enable_cloud_build" {
  project            = var.project
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "enable_secret_manager" {
  project            = var.project
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

###############################################################################
# Artifact Registry
###############################################################################
resource "google_artifact_registry_repository" "repo" {
  depends_on = [google_project_service.enable_artifact_registry]

  project       = var.project
  location      = var.region
  repository_id = var.artifact_repository_name
  format        = "DOCKER"
  description   = "Docker repository for Streamlit image"
}

###############################################################################
# Service Account for Cloud Run
###############################################################################
data "google_service_account" "existing_cloud_run_sa" {
  count      = var.create_service_account ? 0 : 1
  account_id = "cloud-run-sa"
  project    = var.project
}

resource "google_service_account" "cloud_run_sa" {
  count        = var.create_service_account ? 1 : 0
  project      = var.project
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run runtime service account"
}

locals {
  cloud_run_sa_email = var.create_service_account ? google_service_account.cloud_run_sa[0].email : data.google_service_account.existing_cloud_run_sa[0].email
  cloud_run_sa_name  = "projects/${var.project}/serviceAccounts/${local.cloud_run_sa_email}"
}

resource "google_artifact_registry_repository_iam_member" "artifact_reader" {
  project    = var.project
  location   = var.region
  repository = google_artifact_registry_repository.repo.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${local.cloud_run_sa_email}"
}

###############################################################################
# Cloud Run Service
###############################################################################
resource "google_cloud_run_service" "app" {
  provider = google-beta
  depends_on = [
    google_project_service.enable_cloud_run,
    google_artifact_registry_repository.repo
  ]

  name     = var.cloud_run_service_name
  location = var.region
  project  = var.project

  template {
    spec {
      timeout_seconds = 300
      service_account_name = local.cloud_run_sa_email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:latest"

        resources {
          limits = { memory = var.memory }
        }
      }
    }
  }

  traffic {
    latest_revision = true
    percent         = 100
  }
}

resource "google_cloud_run_service_iam_member" "allow_unauth" {
  location = var.region
  project  = var.project
  service  = google_cloud_run_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

###############################################################################
# IAM for Cloud Build SA
###############################################################################
data "google_project" "current" {}

locals {
  cloudbuild_sa = "${data.google_project.current.number}@cloudbuild.gserviceaccount.com"
}

resource "google_artifact_registry_repository_iam_member" "artifact_writer" {
  project    = var.project
  location   = var.region
  repository = google_artifact_registry_repository.repo.repository_id
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${local.cloudbuild_sa}"
}

resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project
  role    = "roles/run.admin"
  member  = "serviceAccount:${local.cloudbuild_sa}"
}

resource "google_service_account_iam_member" "cloudbuild_run_sa_user" {
  service_account_id = local.cloud_run_sa_name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${local.cloudbuild_sa}"
}

###############################################################################
# GitHub Secrets for Cloud Build
###############################################################################
resource "google_secret_manager_secret" "gh_token" {
  depends_on = [google_project_service.enable_secret_manager]
  
  project   = var.project
  secret_id = "github-token"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gh_token_version" {
  secret      = google_secret_manager_secret.gh_token.id
  secret_data = var.github_token
}

resource "google_secret_manager_secret_iam_member" "allow_build_sa" {
  project   = var.project
  secret_id = google_secret_manager_secret.gh_token.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.cloudbuild_sa}"
}

/*
###############################################################################
# GitHub Connection for Cloud Build
###############################################################################
resource "google_cloudbuildv2_connection" "github_connection" {
  provider = google-beta
  project  = var.project
  location = "europe-west1"
  name     = "github-connection"

  github_config {
    app_installation_id = var.github_app_installation_id  # You need to provide this
    authorizer_credential {
      oauth_token_secret_version = google_secret_manager_secret_version.gh_token_version.name
    }
  }
}

resource "google_cloudbuildv2_repository" "github_repo" {
  provider = google-beta
  project  = var.project
  location = "europe-west1"
  name     = "mikolaj2268-sentiment-app"  # Your GitHub repo name
  parent_connection = google_cloudbuildv2_connection.github_connection.name
  remote_uri = "https://github.com/mikolaj2268/sentiment-app.git"  # Your GitHub repo URL
}


# Cloud Build trigger configuration
resource "google_cloudbuild_trigger" "github_trigger" {
  provider   = google-beta
  depends_on = [google_cloudbuildv2_repository.github_repo]
  
  name       = var.trigger_name
  project    = var.project
  description = "Build and deploy on push to main branch"
  location   = var.region

  # Update the repository event config to use the full repository path
  repository_event_config {
    repository = google_cloudbuildv2_repository.github_repo.id
    push {
      branch = "^main$"
    }
  }

  # The rest of the build configuration
  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build",
        "-t",
        "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:$SHORT_SHA",
        "."
      ]
    }

    step {
      name       = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", var.cloud_run_service_name,
        "--image", "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:$SHORT_SHA",
        "--region", var.region,
        "--platform", "managed",
        "--service-account", local.cloud_run_sa_email,
        "--quiet"
      ]
    }

    images = [
      "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:$SHORT_SHA"
    ]
    timeout = "600s"
  }
}

*/


