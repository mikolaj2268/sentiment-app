########################
# Zmienne konfiguracyjne
########################
variable "project" {
  description = "ID projektu GCP"
  type        = string
  default     = "sentiment-analysis-app-455917"
}

variable "region" {
  description = "Region dla Cloud Run i Artifact Registry"
  type        = string
  default     = "europe-west1"
}

variable "artifact_repository_name" {
  description = "Nazwa repozytorium Docker w Artifact Registry"
  type        = string
  default     = "docker-repo"
}

variable "image_name" {
  description = "Nazwa obrazu (bez tagu)"
  type        = string
  default     = "sentiment-analysis-app"
}

variable "cloud_run_service_name" {
  description = "Nazwa usługi Cloud Run"
  type        = string
  default     = "sentiment-analysis-app"
}

variable "memory" {
  description = "Limit pamięci dla kontenera w Cloud Run"
  type        = string
  default     = "2Gi"
}

variable "trigger_name" {
  description = "Nazwa Cloud Build triggera"
  type        = string
  default     = "sentiment-app-cloudbuild-trigger"
}

variable "github_repo_owner" {
  description = "Owner (organisation / user) repozytorium GitHub"
  type        = string
  default     = "mikolaj2268"
}

variable "github_repo_name" {
  description = "Nazwa repozytorium GitHub"
  type        = string
  default     = "sentiment-app"
}