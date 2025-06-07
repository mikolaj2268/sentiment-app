variable "project" {
  description = "Google Cloud project ID"
  type        = string
  default     = "sentiment-analysis-app-455917"
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "europe-west1"
}

variable "artifact_repository_name" {
  description = "Name of the Artifact Registry repository"
  type        = string
  default     = "docker-repo"
}

variable "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "sentiment-analysis-app"
}

variable "image_name" {
  description = "Name of the Docker image"
  type        = string
  default     = "sentiment-analysis-app"
}

variable "memory" {
  description = "Memory allocation for Cloud Run service"
  type        = string
  default     = "2Gi"
}

variable "trigger_name" {
  description = "Name of the Cloud Build trigger"
  type        = string
  default     = "github-trigger"
}

variable "github_repo_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "mikolaj2268-sentiment-app"
}

variable "github_repo_name" {
  description = "GitHub repository name"
  type        = string
}

variable "github_token" {
  description = "GitHub token for authentication"
  type        = string
  sensitive   = true
}

variable "github_app_installation_id" {
  description = "GitHub App installation ID"
  type        = string
  sensitive   = true
}

variable "create_service_account" {
  description = "Whether to create the service account"
  type        = bool
  default     = false
}

variable "csv_bucket_name" {
  description = "Bucket do zapisu przesłanych plików CSV"
  type        = string
}
variable "google_client_id" {
  description = "OAuth Google Client ID"
  type        = string
}

variable "google_client_secret" {
  description = "OAuth Google Client Secret"
  type        = string
  sensitive   = true
}

variable "redirect_uri" {
  description = "Redirect URI for OAuth"
  type        = string
}

variable "service_account_email" {
  description = "Email of the service account to deploy Cloud Run service"
  type        = string
}
