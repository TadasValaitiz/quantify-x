#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Deploying Quantify-X to Google Cloud Run using Cloud Build ===${NC}"

# Configuration
PROJECT_ID="quantify-x"
REGION="europe-west1"
SERVICE_NAME="quantify-x"
DOMAIN="quantifyx.zowo.io"

# Check if gcloud is properly configured
if [[ $(gcloud config get-value project) != "${PROJECT_ID}" ]]; then
    echo -e "${RED}Project is not set to ${PROJECT_ID}. Please run ./cloud/gcloud_init.sh first.${NC}"
    exit 1
fi

# Get the current git commit hash for versioning
GIT_SHA=$(git rev-parse --short HEAD)
echo -e "${GREEN}=== Building version based on commit: ${GIT_SHA} ===${NC}"

# Check if we're on a clean git state
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}WARNING: You have uncommitted changes. These will be included in the build.${NC}"
    echo -e "${YELLOW}Consider committing your changes first for proper versioning.${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment cancelled.${NC}"
        exit 1
    fi
fi

# Submit the build to Cloud Build with the commit hash as a substitution
echo -e "${GREEN}=== Submitting build to Google Cloud Build ===${NC}"
gcloud builds submit --config=cloud/cloudbuild.yaml --substitutions=_COMMIT_SHA=${GIT_SHA} .

echo -e "${GREEN}=== Build and deployment submitted to Cloud Build ===${NC}"
echo -e "${BLUE}You can monitor the build progress at:${NC}"
echo -e "${BLUE}https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}${NC}"

# Wait for build to complete
echo -e "${GREEN}=== Waiting for build and deployment to complete... ===${NC}"
echo -e "${YELLOW}This may take several minutes. You can press Ctrl+C to stop waiting without cancelling the build.${NC}"

# Try to get the Cloud Run URL (this will work if the service has been deployed before)
if gcloud run services describe ${SERVICE_NAME} --region=${REGION} &>/dev/null; then
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')
    echo -e "${GREEN}=== Service will be available at: ${SERVICE_URL} ===${NC}"
    echo -e "${GREEN}=== and at: https://${DOMAIN} after DNS propagation ===${NC}"
fi

echo -e "${GREEN}=== Deployment process initiated! ===${NC}"
echo -e "${GREEN}=== The service may take a few minutes to become fully available. ===${NC}" 