#!/usr/bin/env python3
"""
Chat Ping - Smart Notification App
Quick Start Script for Mobile Deployment
"""

import subprocess
import sys
import os
import socket

def get_local_ip():
    """Get the local IP address for mobile access"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def main():
    print("🔔 Chat Ping - Smart Notification App")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists("smart-notification-app.py"):
        print("❌ Error: smart-notification-app.py not found!")
        print("Please run this script from the app directory.")
        return
    
    # Get local IP
    local_ip = get_local_ip()
    
    print(f"📱 Mobile Access URL: http://{local_ip}:8501")
    print("🔧 Starting Streamlit server...")
    print("=" * 50)
    
    try:
        # Start Streamlit with mobile-friendly settings
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "smart-notification-app.py",
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--server.headless", "false"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Chat Ping...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\n🔧 Try running manually:")
        print("streamlit run smart-notification-app.py --server.address 0.0.0.0")

if __name__ == "__main__":
    main()
