variable "project" {
  description = "GCP project ID where resources will be created"
  type        = string
  default     = "sentiment-analysis-app-455917"
}

variable "region" {
  description = "GCP region for Cloud Run and Artifact Registry"
  type        = string
  default     = "europe-west1"
}

variable "artifact_repository_name" {
  description = "Name of the Artifact Registry repository for container images"
  type        = string
  default     = "docker-repo"
}

variable "image_name" {
  description = "Name of the container image (Streamlit app) in the repository"
  type        = string
  default     = "sentiment-analysis-app"
}

variable "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "sentiment-analysis-app"
}

variable "memory" {
  description = "Memory allocation for the Cloud Run container"
  type        = string
  default     = "2Gi"
}

variable "github_repo_name" {
  description = "GitHub repository name for the app"
  type        = string
  default     = "sentiment-app"
}

variable "github_repo_owner" {
  description = "GitHub user or organization that owns the repository"
  type        = string
  default     = "mikolaj2268"
}

variable "trigger_name" {
  description = "Name of the Cloud Build trigger"
  type        = string
  default     = "sentiment-app-cloudbuild-trigger"
}