from google.oauth2 import service_account
import google.auth.transport.requests

# Path to your downloaded JSON key file
# Update this path to match your actual file location
credentials = service_account.Credentials.from_service_account_file(
    r'C:\Users\itzzzdave\Downloads\smart-notification-app-24a23-20412e315a82.json',
    scopes=['https://www.googleapis.com/auth/firebase.messaging']
)

# Request access token
request = google.auth.transport.requests.Request()
credentials.refresh(request)

print(f"Access Token: {credentials.token}")
print(f"Project ID: {credentials.project_id}")
