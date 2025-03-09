# Quantify-X Cloud Deployment

This directory contains scripts and configuration files for deploying the Quantify-X application to Google Cloud Run using Google Cloud Build.

## Files Overview

- **gcloud_init.sh**: Initializes Google Cloud project with required APIs and permissions
- **deploy.sh**: Manually triggers a Cloud Build deployment
- **cloudbuild.yaml**: Defines the build and deployment process for Cloud Build
- **cleanup-policy.json**: Configures Artifact Registry to retain only the latest 3 versions

## Initial Setup

1. Ensure you have the Google Cloud SDK installed:
   ```
   https://cloud.google.com/sdk/docs/install
   ```

2. Run the initialization script to set up your Google Cloud project:
   ```bash
   chmod +x cloud/gcloud_init.sh
   ./cloud/gcloud_init.sh
   ```

3. Connect your GitHub repository to Cloud Build:
   - Go to: https://console.cloud.google.com/cloud-build/triggers/connect
   - Follow the prompts to connect your GitHub repository
   - Grant the necessary permissions

4. Create a Cloud Build trigger:
   - Go to: https://console.cloud.google.com/cloud-build/triggers/add
   - Name: `quantify-x-deploy`
   - Event: Push to a branch
   - Source: `^main$` (to trigger on pushes to the main branch)
   - Configuration: Cloud Build configuration file (cloudbuild.yaml)
   - Location: Repository
   - Configuration file location: `cloud/cloudbuild.yaml`

## Deployment Methods

### Automatic Deployment (Recommended)

After setting up the trigger, every push to the main branch will automatically:
1. Build a new Docker image with the git commit hash as tag
2. Push it to Artifact Registry
3. Deploy it to Cloud Run
4. Configure the custom domain

### Manual Deployment

To manually trigger a deployment:

```bash
chmod +x cloud/deploy.sh
./cloud/deploy.sh
```

This script will:
1. Check for uncommitted changes
2. Submit your code to Cloud Build
3. Monitor the deployment progress

## Versioning Strategy

This setup uses git-based versioning:
- Each image is tagged with the git commit short hash (`$SHORT_SHA`)
- The latest successful build is also tagged as `latest`
- Only the last 3 tagged versions are retained in Artifact Registry
- Untagged images older than 30 days are automatically deleted

## Accessing the Deployed Application

After deployment, your application will be available at:
- https://quantifyx.zowo.io (custom domain)
- The Cloud Run URL (displayed after deployment)

DNS propagation for the custom domain may take up to 48 hours.

## Monitoring and Logs

- **Build Logs**: https://console.cloud.google.com/cloud-build/builds
- **Cloud Run Logs**: https://console.cloud.google.com/run/detail/europe-west1/quantify-x/logs
- **Revisions**: https://console.cloud.google.com/run/detail/europe-west1/quantify-x/revisions

## Rollback Process

To roll back to a previous version:

1. Find the image tag (commit hash) of the version you want to roll back to:
   ```bash
   gcloud artifacts docker tags list europe-west1-docker.pkg.dev/quantify-x/quantify-x/streamlit-app
   ```

2. Deploy that specific version:
   ```bash
   gcloud run deploy quantify-x \
     --image=europe-west1-docker.pkg.dev/quantify-x/quantify-x/streamlit-app:COMMIT_HASH \
     --region=europe-west1
   ```

## Troubleshooting

- **Domain Mapping Issues**: Check that your DNS is properly configured in Google Cloud DNS
- **Build Failures**: Examine the build logs in Cloud Build
- **Deployment Failures**: Check Cloud Run service logs 