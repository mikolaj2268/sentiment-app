#!/usr/bin/env bash
#
# Wipe the “sentiment-analysis-app-455917” project so we can run Terraform fresh.
# Requires: gcloud CLI already authenticated (gcloud auth login && gcloud config set project …).

set -euo pipefail

PROJECT_ID="sentiment-analysis-app-455917"
REGION="europe-west1"

echo "=== Cloud Run service ==="
gcloud run services delete sentiment-analysis-app \
  --region="$REGION" --platform=managed --quiet || true

echo "=== Artifact Registry repo ==="
gcloud artifacts repositories delete docker-repo \
  --location="$REGION" --quiet || true

echo "=== Secret Manager secret ==="
gcloud secrets delete gcp_token --quiet || true

echo "=== Runtime service account ==="
gcloud iam service-accounts delete \
  cloud-run-sa@"$PROJECT_ID".iam.gserviceaccount.com --quiet || true

echo "=== Cloud Build trigger ==="
gcloud builds triggers delete sentiment-app-trigger --quiet || true

echo "=== Cloud Build GitHub repository ==="
gcloud builds repositories delete sentiment-app \
  --connection=github-connection --region="$REGION" --quiet || true

echo "=== Cloud Build GitHub connection ==="
gcloud builds connections delete github-connection \
  --region="$REGION" --quiet || true

echo "=== (Optional) disable the APIs Terraform enabled ==="
gcloud services disable run.googleapis.com \
  secretmanager.googleapis.com artifactregistry.googleapis.com \
  cloudbuild.googleapis.com --quiet || true

echo "Cleanup finished."