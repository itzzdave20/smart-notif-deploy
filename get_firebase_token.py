#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to generate Firebase OAuth2 access token
Run this script to get your FIREBASE_ACCESS_TOKEN and FIREBASE_PROJECT_ID
"""

from google.oauth2 import service_account
import google.auth.transport.requests
import sys
import os

def main():
    print("="*60)
    print("Firebase OAuth2 Access Token Generator")
    print("="*60)
    print()
    
    # Get service account file path
    if len(sys.argv) > 1:
        service_account_path = sys.argv[1]
    else:
        # Look for common file names
        possible_files = [
            "service-account-key.json",
            "firebase-service-account.json",
            "fcm-service-account.json",
            "service_account_key.json"
        ]
        
        service_account_path = None
        for filename in possible_files:
            if os.path.exists(filename):
                service_account_path = filename
                break
        
        if not service_account_path:
            print("❌ Service account JSON file not found!")
            print()
            print("Usage:")
            print("  python get_firebase_token.py <path-to-service-account.json>")
            print()
            print("Or place your service account JSON file in the current directory")
            print("with one of these names:")
            for f in possible_files:
                print(f"  - {f}")
            print()
            print("To get a service account JSON file:")
            print("  1. Go to https://console.cloud.google.com/")
            print("  2. Select your Firebase project")
            print("  3. Go to IAM & Admin → Service Accounts")
            print("  4. Create service account or select existing")
            print("  5. Go to Keys tab → Add Key → Create new key (JSON)")
            print("  6. Download the JSON file")
            sys.exit(1)
    
    print(f"📁 Using service account file: {service_account_path}")
    print()
    
    try:
        # Load service account credentials
        print("🔐 Loading credentials...")
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=['https://www.googleapis.com/auth/firebase.messaging']
        )
        
        # Request access token
        print("🔄 Requesting access token...")
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        
        access_token = credentials.token
        project_id = credentials.project_id
        
        print("✅ Success!")
        print()
        print("="*60)
        print("Add these to your .streamlit/secrets.toml file:")
        print("="*60)
        print()
        print(f'FIREBASE_ACCESS_TOKEN = "{access_token}"')
        print(f'FIREBASE_PROJECT_ID = "{project_id}"')
        print()
        print("="*60)
        print()
        print("⚠️  Important Notes:")
        print("   - Access tokens expire after 1 hour")
        print("   - You'll need to regenerate periodically")
        print("   - Or implement automatic token refresh in your app")
        print()
        print("💡 Tip: Use the generate_firebase_token.py script for")
        print("   automatic token refresh capabilities")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {service_account_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure you have installed the required libraries:")
        print("  pip install google-auth google-auth-oauthlib google-auth-httplib2")
        sys.exit(1)

if __name__ == "__main__":
    main()

