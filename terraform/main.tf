terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

# Enable required GCP services (Cloud Run, Artifact Registry, Cloud Build)
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

# Artifact Registry repository for Docker images
resource "google_artifact_registry_repository" "repo" {
  depends_on   = [google_project_service.enable_artifact_registry]
  project       = var.project
  location      = var.region
  repository_id = var.artifact_repository_name
  format        = "DOCKER"
  description   = "Docker repository for container images"
}

# Service account for Cloud Run to run the container
resource "google_service_account" "cloud_run_sa" {
  project      = var.project
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run runtime service account"
}

# Grant Artifact Registry Reader to Cloud Run service account (to pull images)
resource "google_artifact_registry_repository_iam_member" "artifact_reader" {
  project    = var.project
  location   = var.region
  repository = google_artifact_registry_repository.repo.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run service for the Streamlit app
resource "google_cloud_run_service" "app" {
  depends_on = [
    google_project_service.enable_cloud_run,
    google_artifact_registry_repository.repo
  ]
  name     = var.cloud_run_service_name
  location = var.region
  project  = var.project

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:latest"
        resources {
          limits = {
            memory = var.memory
          }
        }
      }
      service_account_name = google_service_account.cloud_run_sa.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM roles for Cloud Build service account
data "google_project" "current" {
  project_id = var.project
}
# Construct Cloud Build service account email (PROJECT_NUMBER@cloudbuild.gserviceaccount.com)
locals {
  cloudbuild_sa = "${data.google_project.current.number}@cloudbuild.gserviceaccount.com"
}

# Allow Cloud Build to push images to Artifact Registry (Writer role on the repo)
resource "google_artifact_registry_repository_iam_member" "artifact_writer" {
  project    = var.project
  location   = var.region
  repository = google_artifact_registry_repository.repo.repository_id
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${local.cloudbuild_sa}"
}

# Allow Cloud Build to deploy to Cloud Run (Cloud Run Admin role)
resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project
  role    = "roles/run.admin"
  member  = "serviceAccount:${local.cloudbuild_sa}"
}

# Allow Cloud Build to impersonate the Cloud Run service account (for deployment)
resource "google_service_account_iam_member" "cloudbuild_run_sa_user" {
  service_account_id = google_service_account.cloud_run_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${local.cloudbuild_sa}"
}

# Cloud Build trigger (GitHub) for automatic build and deploy on push to main
resource "google_cloudbuild_trigger" "github_trigger" {
  depends_on = [
    google_project_service.enable_cloud_build,
    google_artifact_registry_repository.repo
  ]
  name  = var.trigger_name

  github {
    owner = var.github_repo_owner
    name  = var.github_repo_name
    push {
      branch = "main"
    }
  }

  build {
    # Step 1: Build the Docker image and push to Artifact Registry
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build", "-t",
        "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:$SHORT_SHA",
        "."
      ]
    }
    # Step 2: Deploy the image to Cloud Run (using gcloud CLI)
    step {
      name       = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", var.cloud_run_service_name,
        "--image", "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:$SHORT_SHA",
        "--region", var.region,
        "--platform", "managed",
        "--quiet"
      ]
    }
    # Image name to push (tags image with the commit SHA)
    images = [
      "${var.region}-docker.pkg.dev/${var.project}/${var.artifact_repository_name}/${var.image_name}:$SHORT_SHA"
    ]
  }
}

# Allow unauthenticated access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "allow_unauth" {
  location = var.region
  service  = var.cloud_run_service_name
  role     = "roles/run.invoker"
  member   = "allUsers"

  depends_on = [google_cloud_run_service.app]
}