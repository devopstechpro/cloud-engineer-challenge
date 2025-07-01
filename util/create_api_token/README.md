# create_api_token Directory - JWT Token Management

This directory contains scripts for managing JWT secrets and generating tokens for the Entrix API Gateway Lambda authorizer.

## Install dependencies

```sh
pip3 install -r requirements.txt
```

## Scripts Overview

### 1. `create_secret.py` - Create JWT Secret in AWS Secrets Manager
Creates a JWT secret in AWS Secrets Manager from the `SECRET_TOKEN` environment variable.

**Usage:**
```sh
export SECRET_TOKEN='your-jwt-secret-value-here'
python3 create_secret.py
```

**Features:**
- Validates AWS credentials
- Creates secret named `entrix-jwt-secret`
- Stores secret as JSON: `{"secret": "your-token-value"}`
- Handles existing secrets (asks if you want to update)
- Outputs the secret ARN for use in CDK/Lambda

### 2. `get_secret_arn.py` - Get Secret ARN with Random Suffix
Retrieves the actual ARN of the JWT secret from AWS Secrets Manager (including the random suffix that AWS adds).

**Usage:**
```sh
python3 get_secret_arn.py
```

**Features:**
- Gets the complete secret ARN with random suffix
- Validates secret accessibility
- Shows account information
- Provides next steps for token generation

### 3. `generate_bearer_token_ssm.py` - Generate JWT Token from Secrets Manager
Generates a JWT token by retrieving the secret from AWS Secrets Manager.

**Prerequisites:**
```sh
export JWT_SECRET_ARN='arn:aws:secretsmanager:eu-west-1:ACCOUNT:secret:entrix-jwt-secret-ABC123'
```

**Usage:**
```sh
python3 generate_bearer_token_ssm.py
```

**Features:**
- Retrieves secret from AWS Secrets Manager
- Generates JWT token with 12-hour expiration
- Uses timezone-aware datetime (no deprecation warnings)
- Outputs the token for use in API requests

### 4. `generate_bearer_token_local.py` - Generate JWT Token Locally
Generates a JWT token using a locally defined secret (for testing/development).

**Prerequisites:**
```sh
export SECRET_TOKEN='your-jwt-secret-value-here'
```

**Usage:**
```sh
python3 generate_bearer_token_local.py
```

**Features:**
- Uses local environment variable for secret
- Generates JWT token with 12-hour expiration
- Uses timezone-aware datetime (no deprecation warnings)
- No AWS dependencies required

### 5. `test_api.py` - Test API Gateway Authorization
Comprehensive testing script for API Gateway authorization with different header formats.

**Usage:**
```sh
python3 test_api.py
```

**Features:**
- Tests API without authorization header
- Tests API with Bearer token format
- Tests API with Authorization header (no Bearer)
- Interactive prompts for API URL and token
- Detailed error reporting and status codes

## Complete Workflow Examples

### Workflow 1: Create Secret and Generate Token (Production)
```bash
# 1. Create the secret
export SECRET_TOKEN='ExtrixApiLambdaSecret#1230001'
python3 create_secret.py

# 2. Get the correct ARN
python3 get_secret_arn.py

# 3. Set the ARN environment variable (use output from step 2)
export JWT_SECRET_ARN='arn:aws:secretsmanager:eu-west-1:123456789012:secret:entrix-jwt-secret-ABC123'

# 4. Generate the token
python3 generate_bearer_token_ssm.py

# 5. Test the API
python3 test_api.py
```

### Workflow 2: Local Development (No AWS)
```bash
# 1. Set local secret
export SECRET_TOKEN='ExtrixApiLambdaSecret#1230001'

# 2. Generate token locally
python3 generate_bearer_token_local.py

# 3. Test the API
python3 test_api.py
```

### Workflow 3: Update Existing Secret
```bash
# 1. Update the secret
export SECRET_TOKEN='new-secret-value'
python3 create_secret.py
# (Script will ask if you want to update - answer 'y')

# 2. Get the ARN and generate new token
python3 get_secret_arn.py
export JWT_SECRET_ARN='arn:aws:secretsmanager:eu-west-1:123456789012:secret:entrix-jwt-secret-ABC123'
python3 generate_bearer_token_ssm.py
```

## Troubleshooting

### IAM Permissions Error
If you get IAM permission errors, make sure to use the correct secret ARN:

1. **Get the actual ARN:**
   ```bash
   python3 get_secret_arn.py
   ```

2. **Set the environment variable with the correct ARN:**
   ```bash
   export JWT_SECRET_ARN='arn:aws:secretsmanager:eu-west-1:123456789012:secret:entrix-jwt-secret-ABC123'
   ```

3. **Generate the token:**
   ```bash
   python3 generate_bearer_token_ssm.py
   ```

### AWS Credentials Error
If you get AWS credentials errors:

1. **Configure AWS CLI:**
   ```bash
   aws configure
   ```

2. **Or set environment variables:**
   ```bash
   export AWS_ACCESS_KEY_ID='your-access-key'
   export AWS_SECRET_ACCESS_KEY='your-secret-key'
   export AWS_REGION='eu-west-1'
   ```

### Token Generation Error
If token generation fails:

1. **Check if secret exists:**
   ```bash
   aws secretsmanager describe-secret --secret-id entrix-jwt-secret --region eu-west-1
   ```

2. **Verify secret format:**
   ```bash
   aws secretsmanager get-secret-value --secret-id entrix-jwt-secret --region eu-west-1
   ```

## API Usage

Once you have a JWT token, use it in your API requests:

```bash
curl -X POST \
  https://YOUR_API_ID.execute-api.eu-west-1.amazonaws.com/prod/orders \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"record_id": "test_1", "parameter_1": "abc", "parameter_2": 4}]'
```

## File Structure
```
create_api_token/
├── README.md                      # This documentation
├── requirements.txt               # Python dependencies
├── create_secret.py              # Create secret in AWS Secrets Manager
├── get_secret_arn.py             # Get secret ARN with suffix
├── generate_bearer_token_ssm.py  # Generate token from Secrets Manager
├── generate_bearer_token_local.py # Generate token locally
└── test_api.py                   # Test API Gateway authorization
```
