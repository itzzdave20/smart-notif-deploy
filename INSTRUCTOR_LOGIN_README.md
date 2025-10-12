# Smart Notification App - Instructor Login System

## Overview

The application now supports **three authentication types**: Admin, User, and **Instructor**. The instructor system is specifically designed for educational institutions to manage classes, attendance, and notifications.

## Authentication Types

### 🛡️ Admin Login
- **Full administrative access** to all features
- **User and instructor management**
- **System settings** and configuration
- **Database management** tools

### 👤 User Login
- **Student access** with limited permissions
- **Personal attendance** tracking
- **Profile management**
- **View notifications** and reports

### 🎓 Instructor Login
- **Class management** capabilities
- **Attendance tracking** for classes
- **Student notification** system
- **Educational reports** and analytics

## Default Credentials

### Instructor Account
- **Username:** `instructor`
- **Password:** `instructor123`

⚠️ **Important:** Change default passwords after first login!

## Instructor Features

### Dashboard
- **Personal welcome** message with instructor details
- **Class statistics** overview
- **Quick action** buttons for common tasks
- **Recent class** information display
- **Department and specialization** information

### Class Management
- **Create new classes** with schedules and rooms
- **Manage enrolled students** for each class
- **View class details** and schedules
- **Class status** management
- **Student enrollment** tracking

### Attendance Management
- **Take class attendance** with photo upload
- **Manual attendance** entry
- **Attendance history** for each class
- **Attendance reports** and analytics
- **Student attendance** tracking

### Notification System
- **Send class notifications** to students
- **Schedule notifications** for future delivery
- **Quick announcement** templates
- **Notification history** tracking
- **Priority-based** notification system

### Reports & Analytics
- **Class overview** statistics
- **Attendance analytics** and trends
- **Student performance** tracking
- **Visual charts** and graphs
- **Export capabilities**

## Instructor Registration

New instructors can register by:
1. Clicking "Instructor Login" on the main page
2. Going to the "Register" tab
3. Filling out the registration form:
   - First Name and Last Name
   - Username (must be unique)
   - Email (must be unique)
   - Department selection
   - Specialization field
   - Password (minimum 6 characters)
   - Password confirmation

## Class Management Features

### Creating Classes
- **Class Code:** Unique identifier (e.g., CS101)
- **Class Name:** Descriptive title
- **Schedule:** Days and times
- **Room:** Physical location
- **Enrolled Students:** List of student usernames

### Managing Students
- **Add students** to classes
- **Remove students** from classes
- **View enrollment** lists
- **Track student** participation

### Sample Classes
The system comes with pre-configured sample classes:
- **CS101:** Introduction to Computer Science
- **CS201:** Data Structures and Algorithms

## Attendance Features

### Photo-Based Attendance
- **Upload class photos** for face recognition
- **Automatic student** identification
- **Confidence scores** for recognition
- **Unknown face** detection

### Manual Attendance
- **Date and time** selection
- **Student-by-student** marking
- **Present/Absent/Late** status options
- **Bulk attendance** entry

### Attendance Tracking
- **Historical records** for each class
- **Attendance trends** and patterns
- **Student attendance** rates
- **Class statistics** and analytics

## Notification Features

### Class Notifications
- **Targeted messaging** to specific classes
- **Multiple notification types:**
  - Announcements
  - Reminders
  - Assignments
  - Exams
  - General messages

### Quick Announcements
- **Assignment due** reminders
- **Class cancellation** notices
- **Exam schedule** updates
- **Template-based** messaging

### Notification Management
- **Priority levels** (1-5)
- **Scheduled delivery** options
- **Notification history** tracking
- **Status monitoring** (pending/sent/failed)

## Reports & Analytics

### Class Overview
- **Total classes** taught
- **Total students** across all classes
- **Average class size** calculations
- **Class distribution** charts

### Attendance Analytics
- **14-day attendance** trends
- **Average daily attendance**
- **Highest/lowest** attendance records
- **Visual trend** analysis

### Student Performance
- **Attendance rates** by student
- **Performance vs attendance** correlation
- **Individual student** tracking
- **Comparative analysis**

## Instructor Permissions

### Available Permissions
- **class_management:** Create and manage classes
- **attendance:** Take and track attendance
- **notifications:** Send class notifications
- **reports:** Access analytics and reports

### Permission Levels
- **Full Instructor:** All permissions
- **Teaching Assistant:** Limited permissions
- **Guest Instructor:** Basic permissions

## Session Management

### Instructor Sessions
- **12-hour timeout** (longer than users)
- **Automatic cleanup** of expired sessions
- **Secure session** tokens
- **Session persistence** across browser refreshes

### Security Features
- **Password hashing** with salt
- **Session-based** authentication
- **Permission-based** access control
- **Automatic logout** on session expiry

## File Structure

### Instructor Authentication Files
- `instructor_auth.py` - Instructor authentication system
- `instructor_features.py` - Instructor-specific features
- `instructors.json` - Instructor database (auto-created)
- `instructor_sessions.json` - Active instructor sessions (auto-created)
- `classes.json` - Class database (auto-created)

### Integration Files
- `app.py` - Main application with triple authentication
- `config.py` - Configuration constants
- `admin_auth.py` - Admin authentication system
- `user_auth.py` - User authentication system

## Getting Started

### For Instructors
1. **Run the application:** `streamlit run app.py`
2. **Choose "Instructor Login"** on the main page
3. **Register a new account** or use default credentials
4. **Create classes** and manage students
5. **Take attendance** and send notifications

### For Administrators
1. **Choose "Admin Login"** on the main page
2. **Use admin credentials** to access full features
3. **Manage instructors** and system settings
4. **Monitor system** activity and logs

## Instructor Interface

### Navigation Menu
- **Dashboard:** Overview and quick actions
- **My Profile:** Personal information management
- **Class Management:** Create and manage classes
- **Attendance:** Take and track class attendance
- **Notifications:** Send class notifications
- **Reports:** View analytics and reports

### User Experience
- **Intuitive class** management interface
- **Visual attendance** tracking
- **Quick notification** templates
- **Comprehensive reporting** system

## Security Considerations

- **Separate authentication** systems for each role
- **Different session timeouts** (24h admin, 12h instructor, 8h user)
- **Permission-based** feature access
- **Secure password** storage with hashing
- **Session management** with automatic cleanup

## Educational Use Cases

### Classroom Management
- **Track student attendance** automatically
- **Send class announcements** instantly
- **Monitor attendance** patterns
- **Generate attendance** reports

### Communication
- **Notify students** about assignments
- **Send exam reminders**
- **Announce class cancellations**
- **Share important updates**

### Analytics
- **Monitor attendance** trends
- **Identify at-risk** students
- **Track class** participation
- **Generate performance** reports

## Troubleshooting

### Common Issues
1. **Session expired:** Re-login required
2. **Class not found:** Check class code
3. **Student not enrolled:** Add to class first
4. **Notification failed:** Check notification settings

### Support
- **Admin users** can manage all instructor accounts
- **System logs** track instructor activities
- **Session cleanup** runs automatically
- **Error messages** provide helpful guidance

## Future Enhancements

- **Grade management** integration
- **Assignment tracking** system
- **Student progress** monitoring
- **Mobile app** for instructors
- **Integration with** learning management systems
- **Advanced analytics** and insights

