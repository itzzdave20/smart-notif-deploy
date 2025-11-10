# Quick Start Guide - AI Chatbot Setup

## ✅ Installation Complete!

All required packages have been installed:
- ✅ openai (version 2.7.1)
- ✅ flask (version 3.1.2)
- ✅ flask-cors
- ✅ requests (version 2.32.5)
- ✅ python-dotenv

## 🔑 Next Step: Configure Your OpenAI API Key

### Option 1: Edit .env file directly

1. Open the `.env` file in your project
2. Find this line:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Replace `your_openai_api_key_here` with your actual API key
4. Save the file

### Option 2: Use the setup script

Run:
```bash
python setup_openai.py
```

Then enter your API key when prompted.

### Option 3: Set environment variable (Windows)

```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Option 4: Set environment variable (Linux/Mac)

```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 🚀 How to Use

### Method 1: Direct OpenAI Integration (Recommended)

1. **Set your API key** (see above)
2. **Run your Streamlit app:**
   ```bash
   streamlit run smart-notification-app.py
   ```
3. **The chatbot will automatically use OpenAI!**

The app will:
- Try OpenAI API first (if key is set)
- Fall back to rule-based if API is unavailable
- Show which mode is active in the UI

### Method 2: Use Flask API Server

1. **Start the API server:**
   ```bash
   python ai_chatbot_api.py
   ```
   
   Or use:
   - Windows: `start_api_server.bat`
   - Linux/Mac: `./start_api_server.sh`

2. **Run your Streamlit app:**
   ```bash
   streamlit run smart-notification-app.py
   ```

3. The app will connect to the local API server

## 📝 Get Your OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Add it to your `.env` file

## 🧪 Test the Setup

### Test API Server

```bash
python test_api.py
```

### Test in Python

```python
import requests

response = requests.post(
    'http://localhost:5000/api/chat',
    json={'message': 'Hello!', 'conversation_history': []}
)

print(response.json())
```

## ✅ Verification

Run the setup script to verify everything:

```bash
python setup_openai.py
```

This will check:
- ✅ .env file exists
- ✅ All packages are installed
- ✅ API key is configured (if set)

## 🎯 What You'll See

When you run the Streamlit app and use the AI Chatbot:

- **If OpenAI is configured:** You'll see "OpenAI API Active" in the sidebar
- **If using rule-based:** You'll see "Using Rule-based Mode" in the sidebar
- **Response source** is shown for each message

## 📚 More Information

- Full API documentation: `README_API.md`
- Detailed setup guide: `AI_CHATBOT_SETUP.md`
- API server code: `ai_chatbot_api.py`

## 🆘 Troubleshooting

### API key not working?

1. Check the `.env` file has the correct key
2. Restart the Streamlit app after setting the key
3. Verify the key at https://platform.openai.com/api-keys
4. Check you have credits in your OpenAI account

### Still using rule-based mode?

1. Make sure `.env` file exists
2. Check `OPENAI_API_KEY` is set correctly
3. Restart the app
4. Check console for error messages

### API server not starting?

1. Check port 5000 is available
2. Install all packages: `pip install -r requirements.txt`
3. Check for error messages in console

## 🎉 You're All Set!

Once you add your OpenAI API key, the chatbot will automatically use it for better, more natural responses!

