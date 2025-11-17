#!/bin/bash

# Azure Setup Script for PlayLister Deployment
# This script configures Azure resources for the PlayLister application

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration variables
RESOURCE_GROUP="BCSAI2025-DEVOPS-STUDENTS-B"
ACR_NAME="playlisteracr"
APP_SERVICE="playlister-webapp"
APP_PLAN="playlister-plan"

echo -e "${GREEN}=== PlayLister Azure Setup ===${NC}\n"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed${NC}"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo -e "${YELLOW}Logging in to Azure...${NC}"
az login

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
echo -e "${GREEN}✓ Using subscription: $SUBSCRIPTION_ID${NC}\n"

# Step 1: Get ACR credentials
echo -e "${YELLOW}Step 1: Retrieving ACR credentials...${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

echo -e "${GREEN}✓ ACR Username: $ACR_USERNAME${NC}"
echo -e "${GREEN}✓ ACR Password: ${ACR_PASSWORD:0:10}...${NC}\n"

# Step 2: Configure App Service to use ACR
echo -e "${YELLOW}Step 2: Configuring App Service to use ACR...${NC}"
az webapp config container set \
  --name $APP_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --docker-custom-image-name $ACR_NAME.azurecr.io/playlister:latest \
  --docker-registry-server-url https://$ACR_NAME.azurecr.io \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

echo -e "${GREEN}✓ App Service configured to use ACR${NC}\n"

# Step 3: Configure App Settings
echo -e "${YELLOW}Step 3: Setting application environment variables...${NC}"
az webapp config appsettings set \
  --name $APP_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --settings \
    APP_ENV=production \
    DATABASE_URL=sqlite:///playlist.db \
    APP_VERSION=1.0.0 \
    WEBSITES_PORT=8000 \
  --output none

echo -e "${GREEN}✓ Environment variables configured${NC}\n"

# Step 4: Enable Continuous Deployment
echo -e "${YELLOW}Step 4: Enabling continuous deployment...${NC}"
az webapp deployment container config \
  --name $APP_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --enable-cd true \
  --output none

echo -e "${GREEN}✓ Continuous deployment enabled${NC}\n"

# Step 5: Create Service Principal for GitHub Actions
echo -e "${YELLOW}Step 5: Creating service principal for GitHub Actions...${NC}"
SP_NAME="playlister-github-actions"

# Check if service principal already exists
SP_EXISTS=$(az ad sp list --display-name $SP_NAME --query "[].appId" --output tsv)

if [ -n "$SP_EXISTS" ]; then
    echo -e "${YELLOW}⚠ Service principal '$SP_NAME' already exists${NC}"
    echo -e "${YELLOW}Using existing service principal: $SP_EXISTS${NC}"
    APP_ID=$SP_EXISTS
    echo -e "${YELLOW}Note: You'll need to manually reset credentials if needed${NC}\n"
else
    # Create new service principal
    AZURE_CREDENTIALS=$(az ad sp create-for-rbac \
      --name $SP_NAME \
      --role contributor \
      --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
      --sdk-auth)
    
    APP_ID=$(echo $AZURE_CREDENTIALS | jq -r '.clientId')
    echo -e "${GREEN}✓ Service principal created: $APP_ID${NC}\n"
fi

# Display summary
echo -e "${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Add the following secrets to your GitHub repository:"
echo -e "   Settings → Secrets and variables → Actions → New repository secret\n"

echo -e "${GREEN}   ACR_USERNAME:${NC}"
echo -e "   $ACR_USERNAME\n"

echo -e "${GREEN}   ACR_PASSWORD:${NC}"
echo -e "   $ACR_PASSWORD\n"

if [ -z "$SP_EXISTS" ]; then
    echo -e "${GREEN}   AZURE_CREDENTIALS:${NC}"
    echo -e "   $AZURE_CREDENTIALS\n"
else
    echo -e "${YELLOW}   AZURE_CREDENTIALS:${NC}"
    echo -e "   Service principal already exists. To get new credentials, run:"
    echo -e "   ${YELLOW}az ad sp credential reset --name $SP_NAME --sdk-auth${NC}\n"
fi

echo -e "2. Push your code to the 'main' branch to trigger deployment\n"

echo -e "3. Monitor deployment at:"
echo -e "   GitHub Actions: https://github.com/YOUR_USERNAME/playLister/actions"
echo -e "   Azure Portal: https://portal.azure.com\n"

echo -e "4. Once deployed, access your app at:"
echo -e "   ${GREEN}https://$APP_SERVICE.azurewebsites.net${NC}\n"

echo -e "${YELLOW}For detailed instructions, see AZURE_DEPLOYMENT.md${NC}\n"

# Save credentials to a local file (gitignored)
echo -e "${YELLOW}Saving credentials to .azure-credentials.txt (this file is gitignored)${NC}"
cat > .azure-credentials.txt << EOF
# Azure Credentials for GitHub Secrets
# Add these to: GitHub → Settings → Secrets → Actions

ACR_USERNAME=$ACR_USERNAME

ACR_PASSWORD=$ACR_PASSWORD

AZURE_CREDENTIALS (App ID: $APP_ID)
Run this command to get credentials if needed:
az ad sp credential reset --name $SP_NAME --sdk-auth

EOF

echo -e "${GREEN}✓ Credentials saved to .azure-credentials.txt${NC}"
echo -e "${RED}⚠ Do NOT commit this file to Git!${NC}\n"
