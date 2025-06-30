import jwt
import datetime

# Use the same secret as your Lambda authorizer
secret = "ExtrixApiLambdaSecret#1230001"

# Create the payload
payload = {
    "sub": "test-user",  # Subject (user id or username)
    "iat": int(datetime.datetime.utcnow().timestamp()),  # Issued at (as int)
    "exp": int((datetime.datetime.utcnow() + datetime.timedelta(hours=12)).timestamp())  # Expires in 12 hour (as int)
}

# Generate the token
token = jwt.encode(payload, secret, algorithm="HS256")

print(token if isinstance(token, str) else token.decode())