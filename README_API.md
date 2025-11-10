# AI Chatbot API Documentation

## Overview

The AI Chatbot API provides REST endpoints for interacting with the AI chatbot. It supports multiple AI backends:
- **OpenAI API** (GPT-3.5, GPT-4) - Recommended for best results
- **Local API endpoint** - For custom implementations
- **Rule-based fallback** - When APIs are unavailable

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Start the API Server

```bash
python ai_chatbot_api.py
```

The server will start on `http://localhost:5000` by default.

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "ai_available": true
}
```

### 2. Chat Endpoint

**POST** `/api/chat`

Main endpoint for chatbot interactions.

**Request Body:**
```json
{
  "message": "What is Python?",
  "conversation_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help you?"}
  ],
  "user_id": "user123",
  "role": "student"
}
```

**Response:**
```json
{
  "response": "Python is a high-level programming language...",
  "timestamp": "2024-01-15T10:30:00",
  "confidence": 0.95,
  "source": "openai",
  "model": "gpt-3.5-turbo",
  "user_id": "user123",
  "role": "student",
  "status": "success"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain recursion",
    "conversation_history": []
  }'
```

### 3. API Status

**GET** `/api/status`

Get API status and configuration.

**Response:**
```json
{
  "status": "operational",
  "ai_available": true,
  "openai_configured": true,
  "timestamp": "2024-01-15T10:30:00",
  "endpoints": {
    "chat": "/api/chat",
    "health": "/health",
    "status": "/api/status"
  }
}
```

### 4. Configuration

**GET** `/api/config`

Get current AI configuration (without sensitive data).

**Response:**
```json
{
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 1000,
  "api_enabled": true,
  "local_api_enabled": true,
  "openai_configured": true
}
```

## Integration with Streamlit App

The Streamlit app automatically uses the API if available. Configure in `config.py`:

```python
AI_API_URL = "http://localhost:5000/api/chat"
AI_USE_API = True
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (missing/invalid parameters)
- `500` - Internal Server Error
- `503` - Service Unavailable (AI features not available)

Error responses include:
```json
{
  "error": "Error message",
  "status": "error",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Using OpenAI API Directly

If you prefer to use OpenAI API directly without the Flask server, set the environment variable:

```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

The Streamlit app will automatically use OpenAI if the key is configured.

## Rate Limiting

For production use, consider adding rate limiting:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## Security

- Never commit `.env` file with API keys
- Use environment variables for sensitive data
- Consider adding authentication for production
- Enable HTTPS in production
- Implement rate limiting to prevent abuse

## Testing

Test the API with Python:

```python
import requests

response = requests.post(
    'http://localhost:5000/api/chat',
    json={
        'message': 'Hello!',
        'conversation_history': []
    }
)

print(response.json())
```

## Troubleshooting

1. **API not responding**: Check if server is running on correct port
2. **OpenAI errors**: Verify API key is correct and has credits
3. **Import errors**: Ensure all dependencies are installed
4. **CORS errors**: Flask-CORS is enabled, but check browser console

## Support

For issues or questions, check:
- API logs in console
- Streamlit app logs
- OpenAI API status page

