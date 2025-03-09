#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Google Cloud Initial Setup for quantify-x ===${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Google Cloud SDK not found. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Login to Google Cloud
echo -e "${GREEN}=== Authenticating with Google Cloud ===${NC}"
gcloud auth login

# Set project configuration
echo -e "${GREEN}=== Setting up project configuration ===${NC}"
gcloud config set project quantify-x

# Enable required APIs
echo -e "${GREEN}=== Enabling required Google Cloud APIs ===${NC}"
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable certificatemanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create Artifact Registry repository
echo -e "${GREEN}=== Creating Artifact Registry repository in europe-west1 ===${NC}"
gcloud artifacts repositories create quantify-x \
    --repository-format=docker \
    --location=europe-west1 \
    --description="Docker repository for Quantify-X application" || \
    echo -e "${YELLOW}Repository may already exist, continuing...${NC}"

# Set up cleanup policy for Artifact Registry
echo -e "${GREEN}=== Setting up cleanup policy for Artifact Registry ===${NC}"
gcloud artifacts repositories set-cleanup-policies quantify-x \
    --location=europe-west1 \
    --policy=cloud/cleanup-policy.json || \
    echo -e "${YELLOW}Failed to set cleanup policy. You may need to manually apply it later.${NC}"

# Check if Cloud DNS zone exists
echo -e "${GREEN}=== Checking Cloud DNS configuration for zowo.io ===${NC}"
if ! gcloud dns managed-zones describe zowo-zone &> /dev/null; then
    echo -e "${YELLOW}Creating DNS zone for zowo.io${NC}"
    gcloud dns managed-zones create zowo-zone \
        --dns-name=zowo.io \
        --description="DNS zone for zowo.io domain"
else
    echo -e "${GREEN}DNS zone for zowo.io already exists${NC}"
fi

# Create DNS A record for subdomain
echo -e "${GREEN}=== Creating DNS A record for quantifyx.zowo.io ===${NC}"
echo "This will be configured after Cloud Run deployment to get the right IP"

# Create service account for deployment
echo -e "${GREEN}=== Creating service account for deployment ===${NC}"
gcloud iam service-accounts create quantify-x-deployer \
    --display-name="Quantify-X Deployment Service Account" || \
    echo -e "${YELLOW}Service account may already exist, continuing...${NC}"

# Grant necessary permissions
echo -e "${GREEN}=== Granting permissions to service account ===${NC}"
gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:quantify-x-deployer@quantify-x.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:quantify-x-deployer@quantify-x.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:quantify-x-deployer@quantify-x.iam.gserviceaccount.com" \
    --role="roles/dns.admin"

gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:quantify-x-deployer@quantify-x.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

# Give Cloud Build service account permissions to deploy to Cloud Run and update DNS
echo -e "${GREEN}=== Granting permissions to Cloud Build service account ===${NC}"
PROJECT_NUMBER=$(gcloud projects describe quantify-x --format='value(projectNumber)')
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Give Cloud Build permissions to Artifact Registry
gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/dns.admin"

gcloud projects add-iam-policy-binding quantify-x \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="roles/iam.serviceAccountUser"

# Also grant Cloud Run service account permission to pull from Artifact Registry
CLOUDRUN_SA="service-${PROJECT_NUMBER}@serverless-robot-prod.iam.gserviceaccount.com"
gcloud artifacts repositories add-iam-policy-binding quantify-x \
    --location=europe-west1 \
    --member="serviceAccount:${CLOUDRUN_SA}" \
    --role="roles/artifactregistry.reader" || \
    echo -e "${YELLOW}Failed to set Artifact Registry permissions for Cloud Run, may need manual setup${NC}"

echo -e "${GREEN}=== Initial setup complete! ===${NC}"
echo -e "${YELLOW}=== Important: Run these permissions commands manually if needed: ===${NC}"
echo "PROJECT_NUMBER=\$(gcloud projects describe quantify-x --format='value(projectNumber)')"
echo "CLOUDRUN_SA=\"service-\${PROJECT_NUMBER}@serverless-robot-prod.iam.gserviceaccount.com\""
echo "gcloud artifacts repositories add-iam-policy-binding quantify-x --location=europe-west1 --member=\"serviceAccount:\${CLOUDRUN_SA}\" --role=\"roles/artifactregistry.reader\""

echo "Next steps:"
echo "1. Connect your GitHub repository to Cloud Build in Google Cloud Console"
echo "   Go to: https://console.cloud.google.com/cloud-build/triggers/connect"
echo "2. Create a Cloud Build trigger for your repository"
echo "   - Trigger type: Push to a branch"
echo "   - Branch: ^main$"
echo "   - Configuration: cloud/cloudbuild.yaml"
echo "3. Or run manually: ./cloud/deploy.sh" 