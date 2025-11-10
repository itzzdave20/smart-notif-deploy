"""
Quick setup script for OpenAI API integration
This script helps you configure your OpenAI API key
"""

import os
from pathlib import Path

def setup_openai_key():
    """Interactive setup for OpenAI API key"""
    print("=" * 60)
    print("OpenAI API Setup")
    print("=" * 60)
    print()
    print("To use the AI Chatbot with OpenAI, you need an API key.")
    print("Get your key from: https://platform.openai.com/api-keys")
    print()
    
    # Check if .env exists
    env_file = Path(".env")
    if env_file.exists():
        print("[OK] .env file found")
        
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if key is already set
        if 'OPENAI_API_KEY=your_openai_api_key_here' in content or 'OPENAI_API_KEY=' in content:
            print("[!] API key not configured yet")
            
            api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
            
            if api_key:
                # Update .env file
                if 'OPENAI_API_KEY=your_openai_api_key_here' in content:
                    content = content.replace('OPENAI_API_KEY=your_openai_api_key_here', f'OPENAI_API_KEY={api_key}')
                elif 'OPENAI_API_KEY=' in content:
                    # Find and replace the line
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('OPENAI_API_KEY='):
                            lines[i] = f'OPENAI_API_KEY={api_key}'
                            break
                    content = '\n'.join(lines)
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print("[OK] API key saved to .env file")
            else:
                print("[!] Skipped. You can set it later in the .env file")
        else:
            print("[OK] API key appears to be configured")
            print("   (Key is hidden for security)")
    else:
        print("[!] .env file not found. Creating one...")
        
        # Create .env file
        env_template = """# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Flask API Server Configuration
API_PORT=5000
API_HOST=0.0.0.0
FLASK_DEBUG=False

# AI Chatbot Configuration
OPENAI_MODEL=gpt-3.5-turbo
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000
AI_USE_API=True
AI_API_ENABLED=True
AI_API_URL=http://localhost:5000/api/chat
"""
        
        with open(env_file, 'w') as f:
            f.write(env_template)
        
        print("[OK] .env file created")
        
        api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
        
        if api_key:
            with open(env_file, 'r') as f:
                content = f.read()
            content = content.replace('OPENAI_API_KEY=your_openai_api_key_here', f'OPENAI_API_KEY={api_key}')
            with open(env_file, 'w') as f:
                f.write(content)
            print("[OK] API key saved to .env file")
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. If you haven't set your API key, edit the .env file")
    print("2. Run your Streamlit app: streamlit run smart-notification-app.py")
    print("3. The chatbot will automatically use OpenAI if the key is set")
    print()
    print("To start the API server separately:")
    print("   python ai_chatbot_api.py")
    print()

def verify_setup():
    """Verify the setup is correct"""
    print("\nVerifying setup...")
    print("-" * 60)
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("[OK] .env file exists")
        
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            print("[OK] OPENAI_API_KEY is set")
        else:
            print("[!] OPENAI_API_KEY not configured")
    else:
        print("[!] .env file not found")
    
    # Check packages
    print("\nChecking packages...")
    try:
        import openai
        print(f"[OK] openai installed (version {openai.__version__})")
    except ImportError:
        print("[X] openai not installed")
    
    try:
        import flask
        print(f"[OK] flask installed (version {flask.__version__})")
    except ImportError:
        print("[X] flask not installed")
    
    try:
        import flask_cors
        print("[OK] flask-cors installed")
    except ImportError:
        print("[X] flask-cors not installed")
    
    try:
        import requests
        print(f"[OK] requests installed (version {requests.__version__})")
    except ImportError:
        print("[X] requests not installed")
    
    try:
        from dotenv import load_dotenv
        print("[OK] python-dotenv installed")
    except ImportError:
        print("[X] python-dotenv not installed")
    
    print("-" * 60)

if __name__ == "__main__":
    setup_openai_key()
    verify_setup()

