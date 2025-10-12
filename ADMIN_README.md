# Smart Notification App with Admin Login

## Admin Login System

This application now includes a comprehensive admin authentication system with the following features:

### Default Admin Credentials
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change the default password after first login!

### Features

#### 🔐 Authentication
- Secure password hashing with salt
- Session management with expiration
- Role-based access control
- Automatic session cleanup

#### 👥 User Management
- Create new admin users
- Manage user roles (admin, super_admin, viewer)
- Permission-based access control
- User activity tracking

#### 🛡️ Admin Panel
- **Dashboard:** System overview and statistics
- **User Management:** Add/edit admin users and permissions
- **System Settings:** Security, notifications, and database settings
- **System Logs:** View and manage system logs

#### 🔒 Security Features
- Password hashing with SHA-256 and salt
- Session-based authentication
- Permission-based feature access
- Automatic session expiration
- Secure logout functionality

### User Roles

1. **Super Admin:** Full access to all features
2. **Admin:** Access to most administrative features
3. **Viewer:** Read-only access to system information

### Permissions

- **read:** View system information
- **write:** Modify system settings
- **admin:** Administrative functions
- **all:** Full access to everything

### Getting Started

1. Run the application: `streamlit run app.py`
2. Use the default credentials to log in
3. Navigate to "🛡️ Admin Panel" to manage the system
4. Change the default password in User Management
5. Create additional admin users as needed

### File Structure

- `app.py` - Main application with admin integration
- `admin_auth.py` - Admin authentication system
- `config.py` - Configuration constants
- `admin_users.json` - Admin user database (auto-created)
- `admin_sessions.json` - Active sessions (auto-created)

### Security Notes

- Admin credentials are stored securely with hashed passwords
- Sessions expire after 24 hours by default
- All admin actions are logged
- Database operations require appropriate permissions
- Sensitive features are protected by authentication

### Admin Functions

#### Dashboard
- System statistics overview
- Active session monitoring
- Quick action buttons
- User role information

#### User Management
- View all admin users
- Add new admin users
- Manage user permissions
- Track user activity

#### System Settings
- Security configuration
- Notification settings
- Database management
- Password policies

#### System Logs
- View system activity
- Filter by log level
- Export and download logs
- Monitor system health
