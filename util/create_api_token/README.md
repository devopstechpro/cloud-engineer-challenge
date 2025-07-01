# create_auth_lambda_token Usage

This script generates a JWT token for use with the Entrix API Gateway Lambda authorizer.

## Install dependencies

```sh
pip3 install -r requirements.txt
```

## Create Secret in AWS Secrets Manager

**Create secret from environment variable**

Set environment var `SECRET_TOKEN` before running the script.

```sh
export SECRET_TOKEN='your-jwt-secret-value-here'
python3 create_secret.py
```

The script will output the ARN of the Secrets Manager resource which you can use to reference in your CDK stack or Lambda environment variables.

## Generate a JWT token

**Fetch token from SSM**

Set environment var `JWT_SECRET_ARN` before running the script.

```sh
python3 generate_bearer_token_ssm.py
```

**Use token locally**

Set environment var `SECRET_TOKEN` before running the script.

```sh
python3 generate_bearer_token_local.py
```

**The script will print a valid JWT token to the console. Use this token in your API requests:**

```
Authorization: Bearer <your-jwt-token>
```

## Usage Examples

### 1. Create Secret in AWS Secrets Manager
```bash
# Set your secret token
export SECRET_TOKEN='ExtrixApiLambdaSecret#1230001'

# Create the secret and get the ARN
python3 create_secret_from_env.py
```

### 2. Generate JWT Token from Secrets Manager
```bash
# Set the secret ARN (output from step 1)
export JWT_SECRET_ARN='arn:aws:secretsmanager:eu-west-1:123456789012:secret:entrix-jwt-secret'

# Generate the token
python3 generate_bearer_token_ssm.py
```

### 3. Generate JWT Token Locally
```bash
# Set your secret token
export SECRET_TOKEN='ExtrixApiLambdaSecret#1230001'

# Generate the token
python3 generate_bearer_token_local.py
```
