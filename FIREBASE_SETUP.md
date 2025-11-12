# Firebase Cloud Messaging (FCM) Setup Guide

This guide will help you set up Firebase Cloud Messaging for push notifications in the Smart Notification App.

## What is Firebase Cloud Messaging?

Firebase Cloud Messaging (FCM) is a free service that allows you to send push notifications to users' devices (web, iOS, Android).

## ⚠️ Important: Legacy API Deprecated

**The Legacy FCM API was deprecated on June 20, 2023, and shutdown began July 22, 2024.**

This app now supports:
- ✅ **HTTP v1 API** (Recommended) - Uses OAuth2 access tokens
- ⚠️ **Legacy API** (Deprecated) - Still works but will stop functioning soon

**You should migrate to HTTP v1 API as soon as possible.**

## Quick Setup

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or select an existing project
3. Enter a project name (e.g., "Smart Notification App")
4. Follow the setup wizard
5. Click **"Create project"**

### Step 2: Enable Cloud Messaging API (HTTP v1)

⚠️ **IMPORTANT**: The Legacy API is **DEPRECATED** as of July 2024. Use HTTP v1 API instead.

1. In Firebase Console, go to **Project Settings** → **Cloud Messaging**
2. **Enable Cloud Messaging API (not Legacy)**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select your Firebase project
   - Navigate to **APIs & Services** → **Library**
   - Search for "Firebase Cloud Messaging API"
   - Click **Enable** (make sure it's the HTTP v1 API, not Legacy)

### Step 3: Create Service Account and Get Access Token

1. In Google Cloud Console, go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name it (e.g., "fcm-service")
4. Grant role: **Firebase Cloud Messaging API Admin**
5. Click **Create and Continue** → **Done**
6. Click on the created service account
7. Go to **Keys** tab → **Add Key** → **Create new key**
8. Choose **JSON** format and download
9. **Generate OAuth2 Access Token**:
   
   First, install the required libraries:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2
   ```
   
   **Option 1: Use the ready-made script** (Easiest - Recommended):
   ```bash
   python get_firebase_token.py path/to/service-account-key.json
   ```
   
   This script will automatically output the values you need to add to your `secrets.toml` file.
   
   **Option 2: Create your own Python script**:
   
   Create a new file (e.g., `my_firebase_token.py`) and add this code:
   ```python
   from google.oauth2 import service_account
   import google.auth.transport.requests
   
   # Path to your downloaded JSON key file
   credentials = service_account.Credentials.from_service_account_file(
       'path/to/service-account-key.json',
       scopes=['https://www.googleapis.com/auth/firebase.messaging']
   )
   
   # Request access token
   request = google.auth.transport.requests.Request()
   credentials.refresh(request)
   
   print(f"Access Token: {credentials.token}")
   print(f"Project ID: {credentials.project_id}")
   ```
   
   Then run it:
   ```bash
   python my_firebase_token.py
   ```
   
   **Option 3: Run in Python interactive mode**:
   
   Open Python and paste the code:
   ```bash
   python
   ```
   Then paste the code from Option 2 above.

### Step 4: Add to Secrets

#### For Local Development:

Edit `.streamlit/secrets.toml`:

```toml
## Firebase Cloud Messaging (FCM) - HTTP v1 API (Recommended)
FIREBASE_ACCESS_TOKEN = "your_oauth2_access_token_here"
FIREBASE_PROJECT_ID = "your_project_id_here"

## Legacy API (Deprecated - only use if HTTP v1 not available)
FIREBASE_SERVER_KEY = ""  # Leave empty, use FIREBASE_ACCESS_TOKEN instead
```

#### For Streamlit Cloud:

1. Go to your app dashboard
2. Click **Settings** → **Secrets**
3. Add:

```toml
FIREBASE_ACCESS_TOKEN = "your_oauth2_access_token_here"
FIREBASE_PROJECT_ID = "your_project_id_here"
```

**Note**: Access tokens expire. You may need to refresh them periodically or use a service account key file directly.

### Step 4: Restart Your App

After adding the secrets, restart your Streamlit app.

## How It Works

### Current Implementation

The app uses Firebase Cloud Messaging API to send push notifications:

1. **Notification Created**: When an instructor/admin creates a notification
2. **Device Tokens**: The app can send to specific device tokens (when users register for push)
3. **FCM API**: Sends notification via Firebase API
4. **User Receives**: Push notification appears on user's device

### Device Token Registration

To send push notifications to users, you need their device tokens. This requires:

1. **Browser Permission**: Users must allow push notifications
2. **Service Worker**: The app already has a service worker (`sw.js`)
3. **Token Storage**: Device tokens should be stored in the database

### Future Enhancement

Currently, push notifications work when device tokens are provided. To enable full push notifications:

1. Add device token registration in the frontend
2. Store tokens in the database
3. Send notifications to all registered devices

## Testing

### Test Push Notification

1. Get a device token (from browser console after user allows notifications)
2. In your code, call:
   ```python
   notification_engine.send_push_notification(
       notification_dict,
       device_tokens=['device_token_here']
   )
   ```

### Check Logs

The app will log:
- ✅ Success messages when notifications are sent
- ❌ Error messages if something goes wrong
- ℹ️ Info messages if Firebase is not configured

## Troubleshooting

### Error: "FIREBASE_SERVER_KEY not set"

- Make sure you added `FIREBASE_SERVER_KEY` to `.streamlit/secrets.toml`
- Restart your Streamlit app after editing secrets
- Check that the key is not empty

### Error: "Firebase API error: 401"

**For HTTP v1 API:**
- Your OAuth2 access token is expired or invalid
- Regenerate the access token using the service account
- Make sure the token has the correct scopes: `https://www.googleapis.com/auth/firebase.messaging`

**For Legacy API:**
- Your Server Key is invalid or expired
- Note: Legacy API is deprecated - migrate to HTTP v1 API

### Error: "Firebase API error: 400"

- Invalid payload format
- Check that device tokens are valid
- Verify notification data structure

### Push Notifications Not Appearing

- User must allow browser notifications
- Device token must be valid and registered
- Check browser console for errors
- Verify Firebase Server Key is correct

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit secrets to git** - `.streamlit/secrets.toml` is in `.gitignore`
2. **Server Key is sensitive** - Keep it secret, don't share it
3. **Use environment variables** in production
4. **Rotate keys** if compromised

## Alternative: Firebase Admin SDK

For more advanced features, you can use the Firebase Admin SDK:

```python
from firebase_admin import credentials, messaging, initialize_app

# Initialize Firebase Admin
cred = credentials.Certificate("path/to/serviceAccountKey.json")
initialize_app(cred)

# Send notification
message = messaging.Message(
    notification=messaging.Notification(
        title="Hello",
        body="World"
    ),
    token="device_token"
)
messaging.send(message)
```

## Current Status

✅ **Implemented:**
- Firebase FCM API integration
- Server Key configuration via secrets
- Push notification sending with device tokens
- Error handling and logging

🚧 **Future Enhancements:**
- Automatic device token registration
- Topic-based notifications
- Notification preferences per user
- Rich notifications with images/actions

## Resources

- [Firebase Console](https://console.firebase.google.com/)
- [FCM Documentation](https://firebase.google.com/docs/cloud-messaging)
- [FCM HTTP API](https://firebase.google.com/docs/cloud-messaging/http-server-ref)

## Support

For issues or questions:
1. Check the logs in your Streamlit app
2. Verify your Firebase Server Key
3. Test with a single device token first
4. Review Firebase Console for delivery status

