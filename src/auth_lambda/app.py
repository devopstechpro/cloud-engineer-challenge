import json
import os
import jwt  # PyJWT
import boto3
from botocore.exceptions import ClientError

def get_secret():
    """Retrieve JWT secret from AWS Secrets Manager"""
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
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret_data = json.loads(get_secret_value_response['SecretString'])
            return secret_data.get('secret', secret_data.get('JWT_SECRET'))
        else:
            raise ValueError("Secret value is not a string")

def lambda_handler(event, context):
    """
    Request-based Lambda authorizer for API Gateway.
    Authorizes requests with a valid JWT in the Authorization header.
    """
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization') or headers.get('authorization', '')
    method_arn = event.get('methodArn', '*')
    secret = get_secret()

    if not auth_header:
        return generate_policy('anonymous', 'Deny', method_arn, {'error': 'Missing Authorization header'})

    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = auth_header

    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        principal_id = payload.get('sub', 'user')
        context = {k: str(v) for k, v in payload.items()}
        return generate_policy(principal_id, 'Allow', method_arn, context)
    except jwt.ExpiredSignatureError:
        return generate_policy('anonymous', 'Deny', method_arn, {'error': 'Token expired'})
    except jwt.InvalidTokenError as e:
        return generate_policy('anonymous', 'Deny', method_arn, {'error': f'Invalid token: {str(e)}'})
    except Exception as e:
        return generate_policy('anonymous', 'Deny', method_arn, {'error': f'Unexpected error: {str(e)}'})

def generate_policy(principal_id, effect, resource, context=None):
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }
    if context:
        policy['context'] = context
    return policy 