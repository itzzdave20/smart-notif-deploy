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

# AI Chatbot API Configuration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)  # Set via environment variable OPENAI_API_KEY
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')  # or "gpt-4", "gpt-4-turbo-preview"
AI_API_ENABLED = os.getenv('AI_API_ENABLED', 'True').lower() == 'true'  # Set to False to use rule-based only
AI_API_URL = os.getenv('AI_API_URL', 'http://localhost:5000/api/chat')  # Local API endpoint
AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))
AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '1000'))
AI_USE_API = os.getenv('AI_USE_API', 'True').lower() == 'true'  # Use external API if available, fallback to rule-based

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