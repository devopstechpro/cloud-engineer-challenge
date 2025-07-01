import jwt
import datetime
import os

# Use the same secret as your Lambda authorizer
secret = os.environ.get('SECRET_TOKEN')

if not secret:
    raise ValueError("SECRET_TOKEN environment variable is not set")

# Create the payload
payload = {
    "sub": "test-user",  # Subject (user id or username)
    "iat": int(datetime.datetime.now(datetime.UTC).timestamp()),  # Issued at (as int)
    "exp": int((datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=12)).timestamp())  # Expires in 12 hour (as int)
}

# Generate the token
token = jwt.encode(payload, secret, algorithm="HS256")

print(token if isinstance(token, str) else token.decode())