#!/bin/bash

# Setup script for GCP Service Account for GitHub Actions
# This script creates a service account with necessary permissions for deploying to GKE

set -e

PROJECT_ID="infs3208-magpie"
SA_NAME="github-actions-msms"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="github-actions-key.json"

echo "🚀 Setting up GCP Service Account for GitHub Actions..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ Error: Not authenticated with gcloud. Run 'gcloud auth login' first"
    exit 1
fi

# Set project
echo "📝 Setting project to ${PROJECT_ID}..."
gcloud config set project "${PROJECT_ID}"

# Create service account
echo "👤 Creating service account ${SA_NAME}..."
if gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" &> /dev/null; then
    echo "⚠️  Service account already exists, skipping creation..."
else
    gcloud iam service-accounts create "${SA_NAME}" \
        --display-name="GitHub Actions MSMS Deployer" \
        --project="${PROJECT_ID}"
    echo "✅ Service account created"
fi

# Grant roles
echo "🔐 Granting IAM roles..."

roles=(
    "roles/container.developer"
    "roles/artifactregistry.writer"
    "roles/iam.serviceAccountUser"
)

for role in "${roles[@]}"; do
    echo "   - Granting ${role}..."
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="${role}" \
        --quiet > /dev/null
done

echo "✅ IAM roles granted"

# Create key
echo "🔑 Creating service account key..."
if [ -f "${KEY_FILE}" ]; then
    echo "⚠️  Key file ${KEY_FILE} already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Using existing key file."
        exit 0
    fi
    rm "${KEY_FILE}"
fi

gcloud iam service-accounts keys create "${KEY_FILE}" \
    --iam-account="${SA_EMAIL}" \
    --project="${PROJECT_ID}"

echo "✅ Service account key created: ${KEY_FILE}"
echo ""
echo "📋 Next steps:"
echo "1. Add the contents of ${KEY_FILE} to GitHub Secrets as 'GCP_SA_KEY'"
echo "   - Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "   - Click 'New repository secret'"
echo "   - Name: GCP_SA_KEY"
echo "   - Value: (paste entire contents of ${KEY_FILE})"
echo ""
echo "2. Generate and add DJANGO_SECRET_KEY:"
echo "   python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
echo ""
echo "3. Generate and add DB_PASSWORD:"
echo "   openssl rand -base64 32"
echo ""
echo "⚠️  IMPORTANT: Keep ${KEY_FILE} secure and never commit it to git!"
echo "⚠️  Delete it after adding to GitHub Secrets: rm ${KEY_FILE}"
