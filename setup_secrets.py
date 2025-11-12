#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for configuring email secrets for Smart Notification App
This script helps verify and set up email configuration.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_secrets_file():
    """Check if secrets.toml exists and is properly configured"""
    secrets_path = Path(".streamlit/secrets.toml")
    
    if not secrets_path.exists():
        print("❌ Secrets file not found at .streamlit/secrets.toml")
        return False
    
    print("✅ Secrets file found at .streamlit/secrets.toml")
    
    # Read and check contents
    try:
        with open(secrets_path, 'r') as f:
            content = f.read()
            
        # Check for required fields
        required_fields = ['EMAIL_USERNAME', 'EMAIL_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
        missing_fields = []
        
        for field in required_fields:
            if f'{field} =' not in content and f'{field}=' not in content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️  Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print("✅ All required fields are present")
        
        # Check for placeholder values
        if 'your_email@example.com' in content or 'your_app_password' in content:
            print("⚠️  Warning: Placeholder values detected. Please update with real credentials.")
            return False
        
        print("✅ Secrets file appears to be configured")
        return True
        
    except Exception as e:
        print(f"❌ Error reading secrets file: {e}")
        return False

def create_secrets_template():
    """Create a template secrets.toml file"""
    secrets_dir = Path(".streamlit")
    secrets_dir.mkdir(exist_ok=True)
    
    secrets_path = secrets_dir / "secrets.toml"
    
    if secrets_path.exists():
        response = input(f"⚠️  {secrets_path} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return False
    
    template = '''## Streamlit secrets for SMTP email sending
## Replace the placeholder values with your real credentials.
##
## For Gmail: create an App Password and use it as EMAIL_PASSWORD.
##   SMTP_SERVER = "smtp.gmail.com"
##   SMTP_PORT = "587"        # or "465" with SMTP_USE_SSL = "true"
##
## For Office365/Outlook:
##   SMTP_SERVER = "smtp.office365.com"
##   SMTP_PORT = "587"
##
## After editing, restart the app.

EMAIL_USERNAME = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"

## Optional
SMTP_USE_SSL = "false"        # "true" if using port 465
EMAIL_FROM_NAME = "Smart Notification App"
EMAIL_REPLY_TO = ""
SMTP_TIMEOUT = "20"
'''
    
    try:
        with open(secrets_path, 'w') as f:
            f.write(template)
        print(f"✅ Created template at {secrets_path}")
        print("📝 Please edit the file and add your real credentials")
        return True
    except Exception as e:
        print(f"❌ Error creating secrets file: {e}")
        return False

def verify_secrets():
    """Verify secrets can be read by Streamlit"""
    try:
        import streamlit as st
        
        if not hasattr(st, 'secrets'):
            print("⚠️  Streamlit secrets not available (this is normal if not running in Streamlit)")
            return False
        
        secrets = st.secrets
        
        # Check required fields
        required = ['EMAIL_USERNAME', 'EMAIL_PASSWORD']
        missing = []
        
        for field in required:
            if field not in secrets or not secrets[field] or secrets[field].strip() == '':
                missing.append(field)
        
        if missing:
            print(f"❌ Missing or empty secrets: {', '.join(missing)}")
            return False
        
        print("✅ Secrets are properly configured and accessible")
        print(f"   EMAIL_USERNAME: {secrets.get('EMAIL_USERNAME', 'NOT SET')[:20]}...")
        print(f"   SMTP_SERVER: {secrets.get('SMTP_SERVER', 'NOT SET')}")
        print(f"   SMTP_PORT: {secrets.get('SMTP_PORT', 'NOT SET')}")
        return True
        
    except ImportError:
        print("⚠️  Streamlit not available (this is normal if not running in Streamlit)")
        return False
    except Exception as e:
        print(f"❌ Error verifying secrets: {e}")
        return False

def print_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("📧 EMAIL SECRETS SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. LOCAL DEVELOPMENT:")
    print("   - Edit .streamlit/secrets.toml with your email credentials")
    print("   - Restart your Streamlit app")
    print("\n2. STREAMLIT CLOUD:")
    print("   - Go to your app dashboard")
    print("   - Click 'Settings' → 'Secrets'")
    print("   - Paste your secrets in TOML format")
    print("\n3. GMAIL SETUP:")
    print("   - Enable 2-Step Verification in Google Account")
    print("   - Go to 'App passwords' → Generate new password")
    print("   - Use the 16-character password (not your regular password)")
    print("\n4. REQUIRED SECRETS:")
    print("   - EMAIL_USERNAME: Your email address")
    print("   - EMAIL_PASSWORD: Your app password or SMTP password")
    print("   - SMTP_SERVER: e.g., 'smtp.gmail.com'")
    print("   - SMTP_PORT: e.g., '587' or '465'")
    print("\n5. OPTIONAL SECRETS:")
    print("   - SMTP_USE_SSL: 'true' or 'false' (for port 465)")
    print("   - EMAIL_FROM_NAME: Display name for emails")
    print("   - EMAIL_REPLY_TO: Reply-to address")
    print("   - SMTP_TIMEOUT: Connection timeout in seconds")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("🔧 Smart Notification App - Secrets Setup")
    print("="*60)
    
    # Check if secrets file exists
    if not check_secrets_file():
        print("\n📝 Creating secrets template...")
        if create_secrets_template():
            print_instructions()
            return
        else:
            print("❌ Failed to create secrets template")
            sys.exit(1)
    
    # Try to verify secrets
    print("\n🔍 Verifying secrets...")
    verify_secrets()
    
    print("\n✅ Setup check complete!")
    print_instructions()

if __name__ == "__main__":
    main()

