# QR Code Attendance Setup

## Installation Requirements

To use the QR code attendance feature, you need to install the `qrcode` library:

```bash
pip install qrcode[pil]
```

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
