#!/usr/bin/env python3
"""
Script to get the actual ARN of the JWT secret in AWS Secrets Manager
"""
import boto3
import json
import sys
from botocore.exceptions import ClientError

def get_secret_arn():
    """Get the actual ARN of the JWT secret in AWS Secrets Manager"""
    
    # Initialize the Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='eu-west-1'
    )
    
    # Secret name
    secret_name = 'entrix-jwt-secret'
    
    try:
        # Get the secret details
        response = client.describe_secret(SecretId=secret_name)
        secret_arn = response['ARN']
        
        print(f"✅ Secret found: {secret_name}")
        print(f"📋 Secret ARN: {secret_arn}")
        
        # Also get the secret value to verify it's accessible
        try:
            secret_response = client.get_secret_value(SecretId=secret_name)
            secret_data = json.loads(secret_response['SecretString'])
            print(f"✅ Secret value accessible: {list(secret_data.keys())}")
        except Exception as e:
            print(f"⚠️  Warning: Could not access secret value: {e}")
        
        return secret_arn
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            print(f"❌ Error: Secret '{secret_name}' not found")
            print("Please create the secret first using:")
            print("export SECRET_TOKEN='your-jwt-secret-value'")
            print("python3 create_secret.py")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🔍 Getting JWT Secret ARN from AWS Secrets Manager...")
    print("-" * 50)
    
    # Validate AWS credentials
    try:
        session = boto3.session.Session()
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        print("✅ AWS credentials validated")
        print(f"   Account: {identity['Account']}")
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        print("Please configure your AWS credentials")
        sys.exit(1)
    
    # Get the secret ARN
    secret_arn = get_secret_arn()
    
    print("-" * 50)
    print("📝 Next steps:")
    print(f"1. Set the environment variable:")
    print(f"   export JWT_SECRET_ARN='{secret_arn}'")
    print("\n2. Generate a JWT token:")
    print("   python3 generate_bearer_token_ssm.py")
    print("\n3. Test the API with the token")

if __name__ == "__main__":
    main() 