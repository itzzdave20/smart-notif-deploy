# Email Secrets Setup Guide

This guide will help you configure email notifications for the Smart Notification App.

## Quick Setup

### Option 1: Run the Setup Script
```bash
python setup_secrets.py
```

This will:
- Check if your secrets file exists
- Verify your configuration
- Provide setup instructions

### Option 2: Manual Setup

## Local Development Setup

1. **Edit the secrets file** (`.streamlit/secrets.toml`):
   ```toml
   EMAIL_USERNAME = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_app_password"
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = "587"
   SMTP_USE_SSL = "false"
   EMAIL_FROM_NAME = "Smart Notification App"
   EMAIL_REPLY_TO = ""
   SMTP_TIMEOUT = "20"
   ```

2. **Restart your Streamlit app** after editing secrets

## Streamlit Cloud Setup

1. Go to your app dashboard: https://share.streamlit.io
2. Select your app
3. Click **Settings** → **Secrets**
4. Paste your secrets in TOML format:
   ```toml
   EMAIL_USERNAME = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_app_password"
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = "587"
   SMTP_USE_SSL = "false"
   EMAIL_FROM_NAME = "Smart Notification App"
   EMAIL_REPLY_TO = ""
   SMTP_TIMEOUT = "20"
   ```
5. Click **Save**
6. Your app will automatically redeploy

## Gmail App Password Setup

**Important**: Gmail requires an App Password (not your regular password) for SMTP.

### Steps:

1. **Enable 2-Step Verification**:
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification" if not already enabled

2. **Create App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Other (Custom name)" as the device
   - Enter "Smart Notification App" as the name
   - Click "Generate"
   - Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)

3. **Use the App Password**:
   - In your secrets file, use the 16-character App Password (remove spaces)
   - Example: `EMAIL_PASSWORD = "abcdefghijklmnop"`

## Email Provider Settings

### Gmail
```toml
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USE_SSL = "false"
```

### Gmail (SSL - Port 465)
```toml
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "465"
SMTP_USE_SSL = "true"
```

### Outlook/Office365
```toml
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = "587"
SMTP_USE_SSL = "false"
```

### Yahoo Mail
```toml
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = "587"
SMTP_USE_SSL = "false"
```

## Testing Your Configuration

1. Start your Streamlit app
2. Log in as an Instructor
3. Go to **Notifications** tab
4. Click **"Send Test Email to Me"**
5. Check your email inbox (and spam folder)

## Troubleshooting

### Error: "SMTP not configured"
- Check that `.streamlit/secrets.toml` exists
- Verify all required fields are present
- Make sure values are not empty
- Restart the Streamlit app after editing secrets

### Error: "Authentication failed"
- For Gmail: Make sure you're using an App Password, not your regular password
- Verify 2-Step Verification is enabled
- Check that the password has no extra spaces

### Error: "Connection refused"
- Check your SMTP_SERVER and SMTP_PORT settings
- Verify your firewall/network allows SMTP connections
- Try using port 465 with SMTP_USE_SSL = "true"

### Emails going to spam
- Add your email to the sender's contacts
- Check spam folder
- Verify EMAIL_FROM_NAME is set appropriately

## Security Notes

- **Never commit secrets.toml to git** - it's already in `.gitignore`
- Use App Passwords instead of regular passwords
- Rotate passwords regularly
- For production, use environment variables or secure secret management

## Current Configuration Status

Your current secrets file is located at: `.streamlit/secrets.toml`

To verify your setup, run:
```bash
python setup_secrets.py
```

