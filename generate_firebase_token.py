#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper script to generate Firebase OAuth2 access token from service account JSON
This is needed for Firebase Cloud Messaging HTTP v1 API
"""

import json
import sys
from pathlib import Path

def generate_access_token(service_account_path):
    """Generate OAuth2 access token from service account JSON file"""
    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
    except ImportError:
        print("❌ Error: Required libraries not installed")
        print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2")
        return None, None
    
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/firebase.messaging']
        )
        
        # Request access token
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        
        # Get project ID from credentials
        project_id = credentials.project_id
        
        return credentials.token, project_id
        
    except FileNotFoundError:
        print(f"❌ Error: Service account file not found: {service_account_path}")
        return None, None
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON file: {service_account_path}")
        return None, None
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        return None, None

def main():
    print("="*60)
    print("Firebase OAuth2 Access Token Generator")
    print("="*60)
    print()
    
    if len(sys.argv) > 1:
        service_account_path = sys.argv[1]
    else:
        # Look for service account JSON in common locations
        possible_paths = [
            "service-account-key.json",
            "firebase-service-account.json",
            "fcm-service-account.json",
            ".streamlit/service-account-key.json"
        ]
        
        print("Looking for service account JSON file...")
        service_account_path = None
        for path in possible_paths:
            if Path(path).exists():
                service_account_path = path
                print(f"✅ Found: {path}")
                break
        
        if not service_account_path:
            print("❌ Service account JSON file not found")
            print()
            print("Usage:")
            print("  python generate_firebase_token.py <path-to-service-account.json>")
            print()
            print("Or place your service account JSON file in one of these locations:")
            for path in possible_paths:
                print(f"  - {path}")
            print()
            print("To get a service account JSON file:")
            print("  1. Go to Google Cloud Console")
            print("  2. IAM & Admin → Service Accounts")
            print("  3. Create service account or select existing")
            print("  4. Keys → Add Key → Create new key (JSON)")
            sys.exit(1)
    
    print(f"Generating access token from: {service_account_path}")
    print()
    
    access_token, project_id = generate_access_token(service_account_path)
    
    if access_token and project_id:
        print("✅ Success! Copy these values to your secrets.toml:")
        print()
        print("="*60)
        print("Add to .streamlit/secrets.toml:")
        print("="*60)
        print()
        print(f'FIREBASE_ACCESS_TOKEN = "{access_token}"')
        print(f'FIREBASE_PROJECT_ID = "{project_id}"')
        print()
        print("="*60)
        print()
        print("⚠️  Note: Access tokens expire after 1 hour")
        print("   You may need to regenerate periodically")
        print("   Or implement automatic token refresh in your app")
    else:
        print("❌ Failed to generate access token")
        sys.exit(1)

if __name__ == "__main__":
    main()

