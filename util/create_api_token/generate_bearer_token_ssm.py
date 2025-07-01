import jwt
import datetime
import boto3
import json
import os
from botocore.exceptions import ClientError

def get_secret():
    """Retrieve JWT secret from AWS Secrets Manager"""
    # Try to get secret name from environment variable
    secret_name = os.environ.get('JWT_SECRET_ARN')
    
    if not secret_name:
        raise ValueError("JWT_SECRET_ARN environment variable is not set")
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=os.environ.get('AWS_REGION', 'eu-west-1')
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret_data = json.loads(get_secret_value_response['SecretString'])
            return secret_data.get('secret', secret_data.get('JWT_SECRET'))
        else:
            raise ValueError("Secret value is not a string")

# Get the secret from AWS Secrets Manager
secret = get_secret()

# Create the payload
payload = {
    "sub": "test-user",  # Subject (user id or username)
    "iat": int(datetime.datetime.now(datetime.UTC).timestamp()),  # Issued at (as int)
    "exp": int((datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=12)).timestamp())  # Expires in 12 hour (as int)
}

# Generate the token
token = jwt.encode(payload, secret, algorithm="HS256")

print(token if isinstance(token, str) else token.decode())