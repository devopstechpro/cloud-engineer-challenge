#!/usr/bin/env python3
"""
Script to create JWT secret in AWS Secrets Manager from environment variable SECRET_TOKEN
"""
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError

def create_secret_from_env():
    """Create JWT secret in AWS Secrets Manager from SECRET_TOKEN environment variable"""
    
    # Get the secret token from environment variable
    secret_token = os.environ.get('SECRET_TOKEN')
    
    if not secret_token:
        print("Error: SECRET_TOKEN environment variable is not set")
        print("Please set the environment variable before running this script:")
        print("export SECRET_TOKEN='your-jwt-secret-value-here'")
        sys.exit(1)
    
    # Initialize the Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=os.environ.get('AWS_REGION', 'eu-west-1')
    )
    
    # Secret configuration
    secret_name = 'entrix-jwt-secret'
    secret_value = {
        'secret': secret_token
    }
    
    try:
        # Check if secret already exists
        try:
            response = client.describe_secret(SecretId=secret_name)
            print(f"Secret '{secret_name}' already exists!")
            print(f"Secret ARN: {response['ARN']}")
            
            # Ask if user wants to update the secret
            update_choice = input("Do you want to update the existing secret? (y/N): ").strip().lower()
            if update_choice in ['y', 'yes']:
                # Update the existing secret
                update_response = client.update_secret(
                    SecretId=secret_name,
                    SecretString=json.dumps(secret_value),
                    Description='JWT secret for Entrix API Gateway Lambda authorizer'
                )
                print(f"Successfully updated secret: {secret_name}")
                print(f"Secret ARN: {update_response['ARN']}")
            else:
                print("Secret was not updated.")
            
            return response['ARN']
            
        except client.exceptions.ResourceNotFoundException:
            pass
        
        # Create the secret
        response = client.create_secret(
            Name=secret_name,
            Description='JWT secret for Entrix API Gateway Lambda authorizer',
            SecretString=json.dumps(secret_value)
        )
        
        print(f"Successfully created secret: {secret_name}")
        print(f"Secret ARN: {response['ARN']}")
        
        return response['ARN']
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceExistsException':
            print(f"Error: Secret '{secret_name}' already exists with a different value")
            print("Use the update option or delete the existing secret first")
        else:
            print(f"Error creating secret: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("Creating JWT secret in AWS Secrets Manager from SECRET_TOKEN environment variable...")
    print("-" * 70)
    
    # Validate AWS credentials
    try:
        session = boto3.session.Session()
        sts_client = session.client('sts')
        sts_client.get_caller_identity()
        print("✅ AWS credentials validated")
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        print("Please configure your AWS credentials using:")
        print("  - AWS CLI: aws configure")
        print("  - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("  - IAM roles (if running on EC2)")
        sys.exit(1)
    
    # Create the secret
    secret_arn = create_secret_from_env()
    
    print("-" * 70)
    print("✅ Secret creation completed successfully!")
    print(f"📋 Secret ARN: {secret_arn}")
    print("\n📝 Next steps:")
    print("1. Use this ARN in your CDK stack or Lambda environment variables")
    print("2. The secret is stored as JSON: {\"secret\": \"your-token-value\"}")
    print("3. Your Lambda functions can now retrieve this secret using the ARN")

if __name__ == "__main__":
    main() 