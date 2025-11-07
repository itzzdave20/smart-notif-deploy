# Email Configuration Setup Instructions

## Quick Setup

I've set up the email configuration system for you! Here's how to complete the setup:

### Option 1: Use the Setup Script (Recommended)

1. **Install python-dotenv** (if not already installed):
   ```bash
   pip install python-dotenv
   ```

2. **Run the setup script**:
   ```bash
   python setup_email_config.py
   ```

3. Follow the prompts to enter your Gmail credentials.

### Option 2: Manual Setup

1. **Copy the example file**:
   ```bash
   copy env_example.txt .env
   ```
   (On Windows PowerShell: `Copy-Item env_example.txt .env`)

2. **Edit the `.env` file** and replace these values:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_USERNAME=your_actual_email@gmail.com
   EMAIL_PASSWORD=your_16_character_app_password
   ```

## Getting Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" as the app and "Other" as the device
5. Generate the password and copy the 16-character code
6. Use this password as `EMAIL_PASSWORD` in your `.env` file

## Verify Setup

After setting up:

1. **Restart your application** (if running)
2. **Test the email sending**:
   - Log in as an instructor
   - Go to "Notifications" page
   - Send a test notification to a class
   - Check the student's email inbox

## Files Created/Modified

✅ `requirements.txt` - Added python-dotenv
✅ `notification_engine.py` - Added .env file loading
✅ `setup_email_config.py` - Interactive setup script
✅ `env_example.txt` - Updated with instructions

## Security Note

⚠️ **Important**: The `.env` file contains sensitive credentials. Make sure:
- `.env` is in your `.gitignore` file (never commit it!)
- Keep your App Password secure
- Don't share your `.env` file with anyone

## Troubleshooting

### Email not sending?
- Check that `.env` file exists and has correct values
- Verify Gmail App Password is correct (16 characters)
- Check console logs for SMTP errors
- Ensure 2-Step Verification is enabled on Gmail

### Can't find .env file?
- Make sure you created it in the project root directory
- Check that it's not hidden (show hidden files in file explorer)

## Need Help?

If you encounter issues:
1. Check the console/terminal output for error messages
2. Verify your Gmail credentials are correct
3. Ensure python-dotenv is installed: `pip install python-dotenv`
4. Try sending a test notification and check the logs

