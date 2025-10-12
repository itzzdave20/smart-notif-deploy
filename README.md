# Smart Notification App with AI Features and Attendance

A comprehensive application that combines attendance tracking with AI-powered smart notifications.

## Features

- **Face Recognition Attendance**: Automatic attendance tracking using face recognition
- **Smart Notifications**: AI-powered notification system with sentiment analysis
- **Streamlit Interface**: Modern web interface for easy management
- **Real-time Analytics**: Attendance reports and notification insights
- **AI Scheduling**: Intelligent notification scheduling based on user behavior

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to `http://localhost:8501`

## Project Structure

- `app.py` - Main Streamlit application
- `attendance_system.py` - Face recognition and attendance tracking
- `notification_engine.py` - AI-powered notification system
- `database.py` - Database management
- `ai_features.py` - AI utilities and sentiment analysis
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies

## Configuration

Create a `.env` file with your configuration:
```
DATABASE_PATH=attendance.db
FACE_ENCODINGS_PATH=face_encodings/
NOTIFICATION_API_KEY=your_api_key
```
