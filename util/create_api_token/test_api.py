#!/usr/bin/env python3
"""
Test script to debug API Gateway authorization issues
"""
import requests
import json
import os
import sys

def test_api_without_auth(api_url):
    """Test API without authorization header"""
    print("🔍 Testing API without authorization...")
    try:
        response = requests.post(
            api_url,
            json=[{"record_id": "test_1", "parameter_1": "abc", "parameter_2": 4}],
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_api_with_bearer_token(api_url, token):
    """Test API with Bearer token"""
    print("🔍 Testing API with Bearer token...")
    try:
        response = requests.post(
            api_url,
            json=[{"record_id": "test_1", "parameter_1": "abc", "parameter_2": 4}],
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_api_with_auth_header(api_url, token):
    """Test API with Authorization header (without Bearer)"""
    print("🔍 Testing API with Authorization header (no Bearer)...")
    try:
        response = requests.post(
            api_url,
            json=[{"record_id": "test_1", "parameter_1": "abc", "parameter_2": 4}],
            headers={
                'Content-Type': 'application/json',
                'Authorization': token
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main function"""
    print("🧪 API Gateway Authorization Test")
    print("=" * 40)
    
    # Get API URL from user
    api_url = input("Enter your API Gateway URL (e.g., https://abc123.execute-api.eu-west-1.amazonaws.com/prod/orders): ").strip()
    
    if not api_url:
        print("❌ No API URL provided")
        sys.exit(1)
    
    # Get JWT token
    token = input("Enter your JWT token: ").strip()
    
    if not token:
        print("❌ No JWT token provided")
        sys.exit(1)
    
    print(f"\n📋 Testing API: {api_url}")
    print(f"🔑 Token: {token[:20]}...")
    print("-" * 40)
    
    # Test 1: Without authorization
    test_api_without_auth(api_url)
    print()
    
    # Test 2: With Bearer token
    test_api_with_bearer_token(api_url, token)
    print()
    
    # Test 3: With Authorization header (no Bearer)
    test_api_with_auth_header(api_url, token)
    print()
    
    print("✅ Testing completed!")
    print("\n📝 Next steps:")
    print("1. Check the status codes and responses above")
    print("2. If you get 401/403 errors, check your Lambda authorizer logs")
    print("3. If you get 500 errors, check your API Lambda logs")
    print("4. Verify the JWT token is valid and not expired")

if __name__ == "__main__":
    main() 