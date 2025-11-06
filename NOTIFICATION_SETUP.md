# Notification System Setup Guide

## Overview
The notification system has been updated to send emails to students and show pop-up notifications on their screens when instructors send notifications.

## Features Implemented

### 1. Email Notifications
- When an instructor sends a notification to students, emails are automatically sent to each student's email address
- Emails are fetched from `students.json` file
- Email sending uses SMTP (Gmail by default)

### 2. Pop-up Notifications
- Browser notifications appear when students receive new notifications
- Streamlit toast notifications show on the student interface
- Sound alerts play when new notifications arrive
- Dashboard shows notification badges and alerts

## Email Configuration

To enable email sending, set the following environment variables:

```bash
# SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### For Gmail:
1. Enable 2-Step Verification on your Google Account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password as `EMAIL_PASSWORD`

### Note:
If email is not configured, the system will still work but will only log the email content instead of sending it. This prevents blocking notification creation.

## How It Works

### Instructor Side:
1. Instructor goes to "Notifications" page
2. Selects a class and creates a notification
3. System automatically:
   - Creates notification in database
   - Sends email to all enrolled students
   - Marks notification as sent

### Student Side:
1. Student receives email notification
2. When student opens the app:
   - Browser notification pop-up appears
   - Sound alert plays
   - Toast notification shows
   - Dashboard shows notification badge
3. Student can view all notifications in "Notifications" page

## Testing

1. **Test Email Sending:**
   - Configure email settings
   - Instructor sends a test notification
   - Check student email inbox

2. **Test Pop-up Notifications:**
   - Instructor sends notification
   - Student opens dashboard or notifications page
   - Verify browser notification appears
   - Verify sound plays

## Troubleshooting

### Emails Not Sending:
- Check environment variables are set correctly
- Verify Gmail app password is correct
- Check console logs for SMTP errors
- Ensure student emails exist in `students.json`

### Pop-ups Not Showing:
- Ensure browser allows notifications (check permission in browser settings)
- Check browser console for JavaScript errors
- Verify notifications are created in database

## Files Modified

1. `notification_engine.py`:
   - Added `get_student_email()` method
   - Updated `send_email_notification()` to actually send emails via SMTP
   - Modified `create_targeted_notification()` to send emails automatically

2. `smart-notification-app.py`:
   - Updated `show_student_notifications()` to show pop-ups
   - Added notification tracking and alerts

3. `user_auth.py`:
   - Updated `show_student_dashboard()` to check for new notifications
   - Added notification alerts on dashboard

4. `instructor_features.py`:
   - Updated success message to indicate email sending

