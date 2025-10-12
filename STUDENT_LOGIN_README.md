# Smart Notification App - Student Login System

## Overview

The application now supports **three authentication types**: Admin, **Student**, and Instructor. The student system is specifically designed for educational institutions to provide students with access to attendance tracking, notifications, and academic features.

## Authentication Types

### 🛡️ Admin Login
- **Full administrative access** to all features
- **User and instructor management**
- **System settings** and configuration
- **Database management** tools

### 🎓 Student Login
- **Student access** with educational features
- **Personal attendance** tracking
- **Academic profile** management
- **View notifications** and reports
- **Student-specific** dashboard

### 🎓 Instructor Login
- **Class management** capabilities
- **Attendance tracking** for classes
- **Student notification** system
- **Educational reports** and analytics

## Default Credentials

### Student Account
- **Username:** `student`
- **Password:** `student123`

⚠️ **Important:** Change default passwords after first login!

## Student Features

### Dashboard
- **Personal welcome** message with student details
- **Academic information** (major, year, student ID)
- **Quick action** buttons for common tasks
- **Recent activity** display
- **Notification status** indicator

### Profile Management
- **View and update** personal information
- **Academic details** (major, year, student ID)
- **Contact information** management
- **Notification preferences**
- **Self-service** profile updates

### Attendance Features
- **Mark personal attendance** with photo upload
- **View attendance** history and records
- **Attendance tracking** and analytics
- **Confidence scores** for face recognition
- **Personal attendance** statistics

### Notification System
- **View class notifications** from instructors
- **Priority-based** notification display
- **Notification history** tracking
- **Real-time updates** from classes
- **Academic announcements**

### Reports & Analytics
- **Personal attendance** summary
- **Attendance trends** and patterns
- **Academic performance** tracking
- **Visual charts** and analytics
- **Student-specific** insights

## Student Registration

New students can register by:
1. Clicking "Student Login" on the main page
2. Going to the "Register" tab
3. Filling out the registration form:
   - First Name and Last Name
   - Username (must be unique)
   - Email (must be unique)
   - Student ID (unique identifier)
   - Major selection
   - Academic Year (Freshman, Sophomore, etc.)
   - Password (minimum 6 characters)
   - Password confirmation

## Student Profile Features

### Academic Information
- **Student ID:** Unique identifier
- **Major:** Academic field of study
- **Academic Year:** Freshman, Sophomore, Junior, Senior, Graduate
- **Department:** Based on major selection
- **Contact Information:** Phone, email

### Profile Management
- **Update academic** information
- **Change major** and year
- **Update contact** details
- **Manage notification** preferences
- **View login** history

## Attendance Features

### Photo-Based Attendance
- **Upload personal photos** for attendance
- **Face recognition** technology
- **Automatic attendance** marking
- **Confidence scores** for recognition
- **Personal attendance** records

### Attendance Tracking
- **Historical records** for personal attendance
- **Attendance trends** and patterns
- **Personal statistics** and analytics
- **Visual charts** and reports
- **Attendance history** export

## Notification Features

### Class Notifications
- **Receive notifications** from instructors
- **Class announcements** and updates
- **Assignment reminders** and due dates
- **Exam schedules** and notifications
- **Academic alerts** and updates

### Notification Management
- **View notification** history
- **Priority-based** display
- **Real-time updates** from classes
- **Notification preferences** management
- **Academic communication** tracking

## Reports & Analytics

### Personal Dashboard
- **Attendance summary** statistics
- **Academic progress** tracking
- **Personal performance** metrics
- **Visual analytics** and charts
- **Student-specific** insights

### Attendance Analytics
- **Personal attendance** trends
- **Attendance patterns** and analysis
- **Performance tracking** over time
- **Visual representation** of data
- **Academic progress** monitoring

## Student Permissions

### Available Permissions
- **read:** View system information and reports
- **attendance:** Mark and view personal attendance
- **notifications:** Access notification features
- **profile:** Manage personal profile

### Permission Levels
- **Full Student:** All permissions
- **Limited Student:** Basic permissions
- **Guest Student:** Read-only access

## Session Management

### Student Sessions
- **8-hour timeout** (same as before)
- **Automatic cleanup** of expired sessions
- **Secure session** tokens
- **Session persistence** across browser refreshes

### Security Features
- **Password hashing** with salt
- **Session-based** authentication
- **Permission-based** access control
- **Automatic logout** on session expiry

## File Structure

### Student Authentication Files
- `user_auth.py` - Student authentication system (renamed from user_auth)
- `students.json` - Student database (auto-created)
- `student_sessions.json` - Active student sessions (auto-created)

### Integration Files
- `app.py` - Main application with triple authentication
- `config.py` - Configuration constants
- `admin_auth.py` - Admin authentication system
- `instructor_auth.py` - Instructor authentication system

## Getting Started

### For Students
1. **Run the application:** `streamlit run app.py`
2. **Choose "Student Login"** on the main page
3. **Register a new account** or use default credentials
4. **Explore student features** and academic tools
5. **Mark attendance** and view notifications

### For Administrators
1. **Choose "Admin Login"** on the main page
2. **Use admin credentials** to access full features
3. **Manage students** and system settings
4. **Monitor system** activity and logs

## Student Interface

### Navigation Menu
- **Dashboard:** Overview and quick actions
- **My Profile:** Academic information management
- **Attendance:** Mark and track personal attendance
- **Notifications:** View class notifications
- **Reports:** Personal analytics and insights

### User Experience
- **Student-focused** interface design
- **Academic terminology** and context
- **Educational features** and tools
- **Personal dashboard** with relevant information
- **Easy navigation** for students

## Educational Context

### Student-Centric Design
- **Academic focus** with student terminology
- **Educational features** and tools
- **Student-specific** dashboard and interface
- **Academic progress** tracking
- **Educational notifications** and updates

### Academic Integration
- **Student ID** management
- **Major and year** tracking
- **Academic progress** monitoring
- **Educational notifications** from instructors
- **Student performance** analytics

## Security Considerations

- **Separate authentication** systems for each role
- **Different session timeouts** (24h admin, 12h instructor, 8h student)
- **Permission-based** feature access
- **Secure password** storage with hashing
- **Session management** with automatic cleanup

## Student Management

### Admin Capabilities
- **View all students** and their information
- **Create new students** with specific permissions
- **Manage student roles** and academic information
- **Monitor student activity** and sessions

### Self-Service Features
- **Profile updates** by students themselves
- **Academic information** management
- **Notification preferences** control
- **Personal attendance** tracking

## Troubleshooting

### Common Issues
1. **Session expired:** Re-login required
2. **Permission denied:** Contact admin for access
3. **Registration failed:** Username/email already exists
4. **Login failed:** Check credentials or contact admin

### Support
- **Admin users** can manage all student accounts
- **System logs** track authentication events
- **Session cleanup** runs automatically
- **Error messages** provide helpful guidance

## Future Enhancements

- **Grade management** integration
- **Assignment tracking** system
- **Academic calendar** integration
- **Mobile app** for students
- **Integration with** learning management systems
- **Advanced analytics** and insights
- **Student collaboration** features
