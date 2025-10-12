# Configuration constants for the Smart Notification App

# Streamlit theme configuration
STREAMLIT_THEME = {
    "primaryColor": "#FF6B6B",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F0F2F6",
    "textColor": "#262730"
}

# AI Configuration
SENTIMENT_ANALYSIS_MODEL = "sentiment-analysis"
MAX_NOTIFICATION_LENGTH = 512
DEFAULT_NOTIFICATION_SCHEDULE = "09:00,13:00,17:00"

# Admin Configuration
ADMIN_SESSION_TIMEOUT_HOURS = 24
MAX_ADMIN_SESSIONS = 10
MIN_PASSWORD_LENGTH = 8

# Database Configuration
DATABASE_PATH = "smart_notification_app.db"
DATABASE_CLEANUP_DAYS = 30
MAX_NOTIFICATION_HISTORY = 1000

# Face Recognition Configuration
FACE_ENCODINGS_PATH = "face_encodings.pkl"
FACE_RECOGNITION_TOLERANCE = 0.6
FACE_RECOGNITION_MODEL = "hog"

# Notification Configuration
NOTIFICATION_API_KEY = "your_notification_api_key_here"
NOTIFICATION_ENABLED = True
EMAIL_ENABLED = True
PUSH_ENABLED = True
WEBHOOK_ENABLED = True