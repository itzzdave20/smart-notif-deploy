#!/usr/bin/env python3
"""
Installation script for QR code library
Run this script to install the required QR code library
"""

import subprocess
import sys

def install_qr_library():
    """Install the qrcode library with PIL support"""
    try:
        print("Installing qrcode library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]"])
        print("✅ QR code library installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install QR code library: {e}")
        return False

if __name__ == "__main__":
    print("QR Code Library Installer")
    print("=" * 30)
    
    success = install_qr_library()
    
    if success:
        print("\n🎉 Installation complete!")
        print("You can now use the QR code attendance features.")
    else:
        print("\n❌ Installation failed!")
        print("Please try installing manually:")
        print("pip install qrcode[pil]")
