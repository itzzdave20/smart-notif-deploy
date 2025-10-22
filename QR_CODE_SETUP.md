# QR Code Attendance Setup

## Installation Requirements

To use the QR code attendance feature, you need to install the `qrcode` library.

### Quick Installation Options:

**Option 1: Using the installation script**
```bash
python install_qr.py
```

**Option 2: Manual installation**
```bash
pip install qrcode[pil]
```

**Option 3: Using requirements.txt**
```bash
pip install -r requirements.txt
```

### What gets installed?
- `qrcode`: Main library for generating QR codes
- `Pillow`: Image processing library (required by qrcode)
- `[pil]`: Ensures Pillow is installed with correct dependencies

### Verification
After installation, verify it works:
```bash
python -c "import qrcode; print('✅ QR code library installed successfully!')"
```

### Troubleshooting
- If you get "ModuleNotFoundError": Try `pip3 install qrcode[pil]` or `python -m pip install qrcode[pil]`
- If you get PIL errors: Try `pip install Pillow` first, then `pip install qrcode[pil]`

## How It Works

### For Instructors:
1. Go to **Class Management** → Select a class → **Attendance**
2. Click on **QR Code Attendance** tab
3. Set the validity period (5-60 minutes)
4. Click **Generate QR Code**
5. Display the QR code to students
6. Students scan the QR code to mark attendance

### For Students:
1. Go to **My Attendance**
2. Scan the QR code displayed by your instructor using your phone's camera
3. Copy the text that appears
4. Paste it in the "QR Code Data" field
5. Click **Mark Attendance**

## Features

- **Secure**: QR codes expire after a set time (default 30 minutes)
- **Mobile-friendly**: Works with any phone camera
- **Real-time**: Instant attendance marking
- **Notifications**: Instructors get notified when students mark attendance
- **Validation**: Only enrolled students can mark attendance
- **Session tracking**: Each QR code has a unique session ID

## Security Features

- QR codes contain encrypted data with expiry timestamps
- Only enrolled students can mark attendance
- Each QR code session is unique and tracked
- Automatic expiry prevents reuse of old QR codes

## Mobile Compatibility

- Works on iPhone, Android, and other mobile devices
- Uses native camera apps for QR code scanning
- No additional apps required
- Optimized for mobile browsers
