# create_auth_lambda_token Usage

This script generates a JWT token for use with the Entrix API Gateway Lambda authorizer.

## Install dependencies

```sh
pip install -r requirements.txt
```

## Generate a JWT token

```sh
python3 token.py
```

The script will print a valid JWT token to the console. Use this token in your API requests:

```
Authorization: Bearer <your-jwt-token>
```
