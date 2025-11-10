"""
Flask API Server for AI Chatbot
Provides REST API endpoints for the AI chatbot functionality
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Import AI features
try:
    from ai_features import AIFeatures
    AI_FEATURES_AVAILABLE = True
except ImportError:
    print("Warning: ai_features module not found. Some features may be limited.")
    AI_FEATURES_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize AI features
ai_features = None
if AI_FEATURES_AVAILABLE:
    try:
        ai_features = AIFeatures()
        print("✅ AI Features initialized successfully")
    except Exception as e:
        print(f"⚠️ Failed to initialize AI Features: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_available': AI_FEATURES_AVAILABLE and ai_features is not None
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint - Main API for chatbot interactions
    
    Request body:
    {
        "message": "user message here",
        "conversation_history": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ],
        "user_id": "optional_user_id",
        "role": "student|instructor|admin"
    }
    
    Response:
    {
        "response": "AI response text",
        "timestamp": "ISO timestamp",
        "confidence": 0.95,
        "source": "openai|api|rule-based",
        "model": "gpt-3.5-turbo" (if using OpenAI)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'error': 'Message is required',
                'status': 'error'
            }), 400
        
        conversation_history = data.get('conversation_history', [])
        user_id = data.get('user_id', 'anonymous')
        role = data.get('role', 'student')
        
        # Get AI response
        if not ai_features:
            return jsonify({
                'error': 'AI features not available',
                'status': 'error'
            }), 503
        
        # Call AI chat method
        result = ai_features.chat_with_ai(message, conversation_history)
        
        # Add metadata
        result['user_id'] = user_id
        result['role'] = role
        result['status'] = 'success'
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """
    Streaming chat endpoint (for future implementation)
    Currently returns regular response, can be upgraded to SSE or WebSocket
    """
    # For now, just call regular chat endpoint
    return chat()

@app.route('/api/status', methods=['GET'])
def status():
    """Get API status and configuration"""
    return jsonify({
        'status': 'operational',
        'ai_available': AI_FEATURES_AVAILABLE and ai_features is not None,
        'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'chat': '/api/chat',
            'health': '/health',
            'status': '/api/status'
        }
    }), 200

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current AI configuration (without sensitive data)"""
    try:
        from config import (
            OPENAI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS,
            AI_USE_API, AI_API_ENABLED
        )
        
        return jsonify({
            'model': OPENAI_MODEL,
            'temperature': AI_TEMPERATURE,
            'max_tokens': AI_MAX_TOKENS,
            'api_enabled': AI_USE_API,
            'local_api_enabled': AI_API_ENABLED,
            'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    🤖 AI Chatbot API Server
    ========================
    Starting server on {host}:{port}
    Debug mode: {debug}
    AI Features: {'✅ Available' if AI_FEATURES_AVAILABLE and ai_features else '❌ Not Available'}
    OpenAI API: {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Not Configured'}
    
    Endpoints:
    - POST /api/chat - Main chat endpoint
    - GET  /health - Health check
    - GET  /api/status - API status
    - GET  /api/config - Configuration info
    
    Example request:
    curl -X POST http://localhost:{port}/api/chat \\
         -H "Content-Type: application/json" \\
         -d '{{"message": "Hello!", "conversation_history": []}}'
    """)
    
    app.run(host=host, port=port, debug=debug)

