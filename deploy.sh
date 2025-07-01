#!/bin/bash

# Entrix Deployment Script
# This script creates the JWT secret and deploys the CDK stack using default AWS credentials

set -e  # Exit on any error

echo "🚀 Entrix Deployment Script"
echo "=========================="

# Check if SECRET_TOKEN is set
if [ -z "$SECRET_TOKEN" ]; then
    echo "❌ Error: SECRET_TOKEN environment variable is not set"
    echo "Please set it before running this script:"
    echo "export SECRET_TOKEN='your-jwt-secret-value-here'"
    exit 1
fi

# Check if AWS credentials are configured (using default profile)
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS credentials not configured"
    echo "Please run 'aws configure' or set up your default AWS credentials"
    exit 1
fi

echo "✅ AWS credentials validated"

# Step 1: Create the secret
echo ""
echo "📦 Step 1: Creating JWT secret in AWS Secrets Manager..."
cd util/create_api_token

# Run the secret creation script
python3 create_secret.py

echo "✅ Secret created/updated successfully"

# Step 2: Deploy CDK stack
echo ""
echo "🏗️  Step 2: Deploying CDK stack..."
cd ../../entrix

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Build the CDK app
echo "🔨 Building CDK app..."
npm run build

# Install PyJWT layer if needed
if [ ! -d "../src/auth_lambda_layer/python" ]; then
    echo "📦 Installing PyJWT Lambda layer..."
    mkdir -p ../src/auth_lambda_layer/python
    pip3 install pyjwt -t ../src/auth_lambda_layer/python
fi

# Deploy the stack
echo "🚀 Deploying CDK stack..."
npx cdk deploy --all --require-approval never

echo ""
echo "✅ Deployment completed successfully!"
echo "📋 Your API Gateway endpoint will be available in the CDK output"
echo "🔑 Use the JWT token generation scripts to test the API:"
echo "   * Set environment var JWT_SECRET_ARN before running the script *"
echo "   cd util/create_api_token"
echo "   python3 generate_bearer_token_ssm.py" 