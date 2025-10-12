# Smart Notification App - User Login System

## Overview

The application now supports both **Admin** and **User** authentication systems, providing different levels of access and functionality based on user roles.

## Authentication Types

### 🛡️ Admin Login
- **Full administrative access** to all features
- **User management** capabilities
- **System settings** and configuration
- **Database management** tools
- **System logs** and monitoring

### 👤 User Login
- **Limited access** based on permissions
- **Personal attendance** tracking
- **Profile management**
- **View notifications** and reports
- **Department-specific** features

## Default Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`

### User Account
- **Username:** `user`
- **Password:** `user123`

⚠️ **Important:** Change default passwords after first login!

## User Registration

New users can register by:
1. Clicking "User Login" on the main page
2. Going to the "Register" tab
3. Filling out the registration form:
   - First Name
   - Last Name
   - Username (must be unique)
   - Email (must be unique)
   - Department selection
   - Password (minimum 6 characters)
   - Password confirmation

## User Features

### Dashboard
- **Personal welcome** message
- **Role and department** information
- **Permission overview**
- **Quick action** buttons
- **Recent activity** display

### My Profile
- **View profile** information
- **Update personal** details
- **Change department**
- **Manage notification** preferences
- **Update contact** information

### Attendance (if permission granted)
- **Mark attendance** with photo upload
- **View personal** attendance records
- **Track attendance** history
- **Confidence scores** for face recognition

### Notifications (if permission granted)
- **View recent** notifications
- **Priority-based** display
- **Notification types** and categories
- **Creation timestamps**

### Reports (if permission granted)
- **Personal attendance** summary
- **Attendance trends** and charts
- **Monthly statistics**
- **Visual data** representation

## User Permissions

### Available Permissions
- **read:** View system information and reports
- **attendance:** Mark and view attendance records
- **notifications:** Access notification features
- **profile:** Manage personal profile

### Permission Levels
- **Basic User:** read, attendance
- **Standard User:** read, attendance, notifications
- **Advanced User:** read, attendance, notifications, profile

## Session Management

### User Sessions
- **8-hour timeout** (shorter than admin)
- **Automatic cleanup** of expired sessions
- **Secure session** tokens
- **Session persistence** across browser refreshes

### Security Features
- **Password hashing** with salt
- **Session-based** authentication
- **Permission-based** access control
- **Automatic logout** on session expiry

## File Structure

### User Authentication Files
- `user_auth.py` - User authentication system
- `users.json` - User database (auto-created)
- `user_sessions.json` - Active user sessions (auto-created)

### Integration Files
- `app.py` - Main application with dual authentication
- `config.py` - Configuration constants
- `admin_auth.py` - Admin authentication system

## Getting Started

### For New Users
1. **Run the application:** `streamlit run app.py`
2. **Choose "User Login"** on the main page
3. **Register a new account** or use default credentials
4. **Explore user features** based on your permissions

### For Administrators
1. **Choose "Admin Login"** on the main page
2. **Use admin credentials** to access full features
3. **Manage users** and system settings
4. **Monitor system** activity and logs

## User Interface Differences

### Admin Interface
- **Full navigation** menu with all features
- **Admin Panel** with system management
- **User management** capabilities
- **System settings** and configuration

### User Interface
- **Limited navigation** based on permissions
- **Personal dashboard** and profile
- **Attendance tracking** (if permitted)
- **Notifications and reports** (if permitted)

## Security Considerations

- **Separate authentication** systems for admin and users
- **Different session timeouts** (24h admin, 8h user)
- **Permission-based** feature access
- **Secure password** storage with hashing
- **Session management** with automatic cleanup

## User Management

### Admin Capabilities
- **View all users** and their information
- **Create new users** with specific permissions
- **Manage user roles** and departments
- **Monitor user activity** and sessions

### Self-Service Features
- **Profile updates** by users themselves
- **Password changes** (to be implemented)
- **Notification preferences** management
- **Department transfers** (if permitted)

## Troubleshooting

### Common Issues
1. **Session expired:** Re-login required
2. **Permission denied:** Contact admin for access
3. **Registration failed:** Username/email already exists
4. **Login failed:** Check credentials or contact admin

### Support
- **Admin users** can manage all user accounts
- **System logs** track authentication events
- **Session cleanup** runs automatically
- **Error messages** provide helpful guidance

## Future Enhancements

- **Password reset** functionality
- **Email verification** for registration
- **Two-factor authentication**
- **Role-based** department management
- **Advanced reporting** features
- **Mobile app** integration

