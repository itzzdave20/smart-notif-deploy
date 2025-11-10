# AI Chatbot Setup Guide

## Quick Start

### Option 1: Use OpenAI API Directly (Recommended)

1. **Get OpenAI API Key**
   - Sign up at https://platform.openai.com
   - Get your API key from https://platform.openai.com/api-keys

2. **Set Environment Variable**
   
   **Windows:**
   ```cmd
   set OPENAI_API_KEY=sk-your-api-key-here
   ```
   
   **Linux/Mac:**
   ```bash
   export OPENAI_API_KEY=sk-your-api-key-here
   ```

3. **Or Create .env file:**
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

4. **Run Streamlit App**
   ```bash
   streamlit run smart-notification-app.py
   ```

The chatbot will automatically use OpenAI API if the key is configured!

### Option 2: Use Flask API Server

1. **Start the API Server**
   ```bash
   python ai_chatbot_api.py
   ```
   
   Or use the startup script:
   - Windows: `start_api_server.bat`
   - Linux/Mac: `chmod +x start_api_server.sh && ./start_api_server.sh`

2. **Configure API URL** (if different from default)
   
   In `config.py` or `.env`:
   ```
   AI_API_URL=http://localhost:5000/api/chat
   ```

3. **Run Streamlit App**
   ```bash
   streamlit run smart-notification-app.py
   ```

## Features

### ✅ Multi-tier AI System

1. **OpenAI API** (Best Quality)
   - Uses GPT-3.5 or GPT-4
   - Natural conversations
   - Context-aware responses
   - Best for production

2. **Local API Endpoint** (Customizable)
   - Use your own AI service
   - Custom implementations
   - Self-hosted solutions

3. **Rule-based Fallback** (Always Available)
   - Works without API keys
   - Pre-defined responses
   - Good for basic queries

### ✅ Automatic Fallback

The system automatically falls back if:
- OpenAI API is unavailable
- API key is invalid
- Network issues occur
- Rate limits are hit

### ✅ Conversation History

- Maintains context across messages
- Remembers previous interactions
- Up to 10 messages of history

## Configuration

### Environment Variables

Create a `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# API Server Configuration
API_PORT=5000
API_HOST=0.0.0.0

# AI Settings
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000
AI_USE_API=True
```

### Config.py Settings

```python
OPENAI_MODEL = "gpt-3.5-turbo"  # or "gpt-4"
AI_TEMPERATURE = 0.7  # 0.0-2.0, higher = more creative
AI_MAX_TOKENS = 1000  # Max response length
AI_USE_API = True  # Enable API usage
```

## Testing

### Test the API Server

```bash
python test_api.py
```

### Manual API Test

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "conversation_history": []}'
```

### Test in Python

```python
import requests

response = requests.post(
    'http://localhost:5000/api/chat',
    json={'message': 'What is Python?', 'conversation_history': []}
)

print(response.json())
```

## Troubleshooting

### OpenAI API Not Working

1. **Check API Key:**
   ```python
   import os
   print(os.getenv('OPENAI_API_KEY'))
   ```

2. **Verify Key is Valid:**
   - Check at https://platform.openai.com/api-keys
   - Ensure you have credits

3. **Check Network:**
   - Ensure internet connection
   - Check firewall settings

### API Server Not Starting

1. **Check Port:**
   - Default is 5000
   - Change in `.env`: `API_PORT=5000`

2. **Check Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check Logs:**
   - Look for error messages in console
   - Check if port is already in use

### Rule-based Mode Only

If you see "Rule-based Mode" in the UI:

1. **Check API Key:**
   - Ensure `OPENAI_API_KEY` is set
   - Restart the app after setting

2. **Check Config:**
   - `AI_USE_API` should be `True`
   - `AI_API_ENABLED` should be `True`

3. **Check API Server:**
   - If using local API, ensure server is running
   - Check `AI_API_URL` is correct

## Cost Considerations

### OpenAI API Pricing

- **GPT-3.5-turbo**: ~$0.0015 per 1K tokens (input) + $0.002 per 1K tokens (output)
- **GPT-4**: Higher cost, better quality

### Cost Optimization

1. **Use GPT-3.5-turbo** for most queries
2. **Limit conversation history** (already limited to 10 messages)
3. **Set lower max_tokens** if responses are too long
4. **Use rule-based** for common questions

## Security

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Add authentication** for production API server
4. **Enable rate limiting** to prevent abuse

## Support

For issues:
1. Check console logs
2. Test API endpoints
3. Verify configuration
4. Check OpenAI status page

## Next Steps

- Add authentication to API server
- Implement rate limiting
- Add conversation persistence
- Create custom AI models
- Add streaming responses

