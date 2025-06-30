import json
import os
import jwt  # PyJWT

def lambda_handler(event, context):
    """
    Request-based Lambda authorizer for API Gateway.
    Authorizes requests with a valid JWT in the Authorization header.
    """
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization') or headers.get('authorization', '')
    method_arn = event.get('methodArn', '*')
    secret = os.environ.get('JWT_SECRET', 'ExtrixApiLambdaSecret#1230001')

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