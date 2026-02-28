import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
import json
import os
import pandas as pd
import plotly.express as px
from ai_features import AIFeatures
from meetings import render_meeting, suggest_room_for_user

class StudentAuth:
    def __init__(self):
        self.students_file = "students.json"
        self.student_sessions_file = "student_sessions.json"
        self.load_students()
        self.load_student_sessions()
    
    def load_students(self):
        """Load students from file"""
        if os.path.exists(self.students_file):
            with open(self.students_file, 'r') as f:
                self.students = json.load(f)
        else:
            # Create default student
            self.students = {
                "student": {
                    "password_hash": self.hash_password("student123"),
                    "email": "student@example.com",
                    "role": "student",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "permissions": ["read", "attendance", "notifications"],
                    "profile": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "student_id": "STU001",
                        "major": "Computer Science",
                        "year": "Sophomore",
                        "phone": "",
                        "notifications_enabled": True
                    }
                }
            }
            self.save_students()
    
    def save_students(self):
        """Save students to file"""
        with open(self.students_file, 'w') as f:
            json.dump(self.students, f, indent=2)
    
    def load_student_sessions(self):
        """Load active student sessions from file"""
        if os.path.exists(self.student_sessions_file):
            with open(self.student_sessions_file, 'r') as f:
                self.student_sessions = json.load(f)
        else:
            self.student_sessions = {}
    
    def save_student_sessions(self):
        """Save active student sessions to file"""
        with open(self.student_sessions_file, 'w') as f:
            json.dump(self.student_sessions, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            password_hash_check = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash_check == stored_hash
        except:
            return False
    
    def register_student(self, username, password, email, first_name, last_name, student_id, major="Computer Science", year="Freshman"):
        """Register a new student"""
        if username in self.students:
            return False, "Username already exists"
        
        if email in [student_data.get('email', '') for student_data in self.students.values()]:
            return False, "Email already registered"
        
        self.students[username] = {
            "password_hash": self.hash_password(password),
            "email": email,
            "role": "student",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "permissions": ["read", "attendance", "notifications"],
            "profile": {
                "first_name": first_name,
                "last_name": last_name,
                "student_id": student_id,
                "major": major,
                "year": year,
                "phone": "",
                "notifications_enabled": True
            }
        }
        
        self.save_students()
        return True, "Student registered successfully"
    
    def authenticate_student(self, username, password, remember_me=False):
        """Authenticate student"""
        if username not in self.students:
            return False, "Invalid username or password"
        
        student = self.students[username]
        if not self.verify_password(password, student["password_hash"]):
            return False, "Invalid username or password"
        
        # Update last login
        student["last_login"] = datetime.now().isoformat()
        self.save_students()
        
        # Create session with longer expiration if "remember me" is checked
        session_id = secrets.token_urlsafe(32)
        # If remember_me, extend session to 30 days, otherwise 8 hours
        expiration = timedelta(days=30) if remember_me else timedelta(hours=8)
        self.student_sessions[session_id] = {
            "username": username,
            "role": student["role"],
            "permissions": student["permissions"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + expiration).isoformat(),
            "remember_me": remember_me
        }
        self.save_student_sessions()
        
        return True, session_id
    
    def verify_student_session(self, session_id):
        """Verify student session"""
        if not session_id:
            return False, None
            
        # Ensure we have the latest sessions from disk
        if session_id not in self.student_sessions:
            self.load_student_sessions()
            if session_id not in self.student_sessions:
                return False, None
        
        session = self.student_sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            # Session expired
            del self.student_sessions[session_id]
            self.save_student_sessions()
            return False, None
        
        return True, session
    
    def logout_student(self, session_id):
        """Logout student"""
        if session_id in self.student_sessions:
            del self.student_sessions[session_id]
            self.save_student_sessions()
        return True
    
    def get_student_info(self, session_id):
        """Get student information from session"""
        is_valid, session = self.verify_student_session(session_id)
        if not is_valid:
            return None
        
        username = session["username"]
        if username not in self.students:
            return None
            
        student_data = self.students[username]
        
        return {
            "username": username,
            "role": session["role"],
            "permissions": session["permissions"],
            "email": student_data["email"],
            "profile": student_data["profile"],
            "last_login": student_data["last_login"]
        }
    
    def has_student_permission(self, session_id, permission):
        """Check if student has specific permission"""
        student_info = self.get_student_info(session_id)
        if not student_info:
            return False
        
        return permission in student_info["permissions"]
    
    def update_student_profile(self, username, profile_data):
        """Update student profile"""
        if username in self.students:
            self.students[username]["profile"].update(profile_data)
            self.save_students()
            return True
        return False
    
    def get_student_stats(self):
        """Get student system statistics"""
        return {
            "total_students": len(self.students),
            "active_sessions": len(self.student_sessions),
            "roles": list(set(student["role"] for student in self.students.values())),
            "majors": list(set(student["profile"].get("major", "Computer Science") for student in self.students.values())),
            "years": list(set(student["profile"].get("year", "Freshman") for student in self.students.values()))
        }
    
    def enroll_in_class(self, student_username, class_code):
        """Enroll student in a class"""
        # Verify that the username is actually a student
        if student_username not in self.students:
            return False, "User not found. Only registered students can enroll in classes."
        
        # Verify the user has student role
        student_data = self.students.get(student_username, {})
        if student_data.get("role") != "student":
            return False, "Only students can enroll in classes."
        
        # Check if user is an instructor (additional safeguard)
        from instructor_auth import InstructorAuth
        instructor_auth = InstructorAuth()
        if student_username in instructor_auth.instructors:
            return False, "Instructors cannot enroll in classes. Only students can enroll."
        
        # Load instructor auth to access classes
        # Check if class exists
        if class_code not in instructor_auth.classes:
            return False, "Class not found"
        
        # Check if student is already enrolled
        if student_username in instructor_auth.classes[class_code]["enrolled_students"]:
            return False, "Student already enrolled in this class"
        
        # Add student to class
        success, message = instructor_auth.add_student_to_class(class_code, student_username)
        
        if success:
            # Update student's enrolled classes
            if "enrolled_classes" not in self.students[student_username]:
                self.students[student_username]["enrolled_classes"] = []
            
            if class_code not in self.students[student_username]["enrolled_classes"]:
                self.students[student_username]["enrolled_classes"].append(class_code)
                self.save_students()
        
        return success, message
    
    def unenroll_from_class(self, student_username, class_code):
        """Unenroll student from a class"""
        # Load instructor auth to access classes
        from instructor_auth import InstructorAuth
        instructor_auth = InstructorAuth()
        
        # Remove student from class
        success, message = instructor_auth.remove_student_from_class(class_code, student_username)
        
        if success:
            # Update student's enrolled classes
            if "enrolled_classes" in self.students[student_username]:
                if class_code in self.students[student_username]["enrolled_classes"]:
                    self.students[student_username]["enrolled_classes"].remove(class_code)
                    self.save_students()
        
        return success, message
    
    def get_student_classes(self, student_username):
        """Get classes that student is enrolled in"""
        if "enrolled_classes" not in self.students[student_username]:
            return []
        return self.students[student_username]["enrolled_classes"]
    
    def get_available_classes(self):
        """Get all available classes for enrollment"""
        from instructor_auth import InstructorAuth
        instructor_auth = InstructorAuth()
        return instructor_auth.classes

def show_student_login():
    """Display student login form"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .login-header {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    .login-tabs {
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-header">🎓 Student Login</h2>', unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("student_login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("Login", type="primary")
            with col2:
                # Default to remembering the student on this device
                remember_me = st.checkbox("Remember me", value=True)
            
            if login_button:
                if username and password:
                    auth = StudentAuth()
                    success, result = auth.authenticate_student(username, password, remember_me=remember_me)
                    
                    if success:
                        # Use the same auth instance that created the session
                        st.session_state.student_auth = auth
                        st.session_state.student_logged_in = True
                        st.session_state.student_session_id = result
                        st.session_state.student_username = username
                        
                        # Save to localStorage if "Remember me" is checked
                        if remember_me:
                            st.markdown(f"""
                            <script>
                            localStorage.setItem('student_session_id', '{result}');
                            localStorage.setItem('student_username', '{username}');
                            localStorage.setItem('student_remember_me', 'true');
                            localStorage.setItem('user_type', 'student');
                            </script>
                            """, unsafe_allow_html=True)
                        
                        # AI-powered welcome notification
                        try:
                            if 'notification_engine' in st.session_state:
                                st.session_state.notification_engine.create_system_notification(
                                    system_event="Student Login",
                                    details=f"User {username} logged in"
                                )
                        except Exception as _e:
                            pass
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        with st.form("student_register_form"):
            st.subheader("Create New Student Account")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", placeholder="Enter first name")
                username = st.text_input("Username", placeholder="Choose username")
            with col2:
                last_name = st.text_input("Last Name", placeholder="Enter last name")
                email = st.text_input("Email", placeholder="Enter email address")
            
            student_id = st.text_input("Student ID", placeholder="Enter your student ID")
            major = st.selectbox("Major", ["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "Engineering", "Business", "Arts"])
            year = st.selectbox("Academic Year", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
            password = st.text_input("Password", type="password", placeholder="Choose password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            
            if st.form_submit_button("Register", type="primary"):
                if all([first_name, last_name, username, email, student_id, password, confirm_password]):
                    if password == confirm_password:
                        if len(password) >= 6:
                            auth = StudentAuth()
                            success, message = auth.register_student(
                                username, password, email, first_name, last_name, student_id, major, year
                            )
                            
                            if success:
                                st.success(f"✅ {message}")
                                st.info("You can now login with your new account!")
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error("Password must be at least 6 characters long")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.warning("Please fill in all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_student_logout():
    """Display student logout button"""
    if st.sidebar.button("🚪 Logout", type="secondary"):
        # Clear student session state for the current browser session only.
        # The persistent "remember me" session remains on disk/localStorage
        # so that reopening the app can automatically log the student back in.
        for key in ['student_logged_in', 'student_session_id', 'student_username']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("✅ Logged out successfully!")
        st.rerun()

def check_student_auth():
    """Check if student is authenticated"""
    if 'student_logged_in' not in st.session_state or not st.session_state.student_logged_in:
        return False
    
    if 'student_session_id' not in st.session_state:
        return False
    
    auth = StudentAuth()
    is_valid, session = auth.verify_student_session(st.session_state.student_session_id)
    
    if not is_valid:
        # Session expired or invalid
        for key in ['student_logged_in', 'student_session_id', 'student_username']:
            if key in st.session_state:
                del st.session_state[key]
        return False
    
    return True

def show_student_profile():
    """Show student profile management"""
    st.header("👤 Student Profile")
    
    auth = StudentAuth()
    student_info = auth.get_student_info(st.session_state.student_session_id)
    
    if not student_info:
        st.error("Unable to load student information")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Profile Information")
        
        # Display current profile
        profile = student_info["profile"]
        # Show profile picture if available
        avatar_dir = os.path.join(os.getcwd(), "avatars")
        avatar_path = os.path.join(avatar_dir, f"{student_info['username']}.png")
        if os.path.exists(avatar_path):
            st.image(avatar_path, caption="Profile Picture", width=160)
        st.write(f"**Name:** {profile['first_name']} {profile['last_name']}")
        st.write(f"**Username:** {student_info['username']}")
        st.write(f"**Email:** {student_info['email']}")
        st.write(f"**Student ID:** {profile['student_id']}")
        st.write(f"**Major:** {profile['major']}")
        st.write(f"**Year:** {profile['year']}")
        st.write(f"**Role:** {student_info['role']}")
        st.write(f"**Last Login:** {student_info['last_login'][:19] if student_info['last_login'] else 'Never'}")
    
    with col2:
        st.subheader("Update Profile")
        
        with st.form("update_student_profile_form"):
            uploaded_avatar = st.file_uploader("Profile Picture", type=['png', 'jpg', 'jpeg'], key="student_profile_avatar")
            new_first_name = st.text_input("First Name", value=profile['first_name'])
            new_last_name = st.text_input("Last Name", value=profile['last_name'])
            new_major = st.selectbox("Major", 
                ["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "Engineering", "Business", "Arts"],
                index=["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "Engineering", "Business", "Arts"].index(profile.get('major', 'Computer Science'))
            )
            new_year = st.selectbox("Academic Year", 
                ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"],
                index=["Freshman", "Sophomore", "Junior", "Senior", "Graduate"].index(profile.get('year', 'Freshman'))
            )
            new_phone = st.text_input("Phone", value=profile.get('phone', ''))
            notifications_enabled = st.checkbox("Enable Notifications", value=profile.get('notifications_enabled', True))
            
            if st.form_submit_button("Update Profile", type="primary"):
                profile_data = {
                    "first_name": new_first_name,
                    "last_name": new_last_name,
                    "major": new_major,
                    "year": new_year,
                    "phone": new_phone,
                    "notifications_enabled": notifications_enabled
                }
                
                # Save avatar if uploaded
                if uploaded_avatar is not None:
                    try:
                        if not os.path.exists(avatar_dir):
                            os.makedirs(avatar_dir, exist_ok=True)
                        # Normalize to PNG for consistency
                        with open(avatar_path, 'wb') as f:
                            f.write(uploaded_avatar.getbuffer())
                        st.success("📷 Profile picture updated!")
                    except Exception as e:
                        st.warning(f"Could not save profile picture: {e}")
                
                success = auth.update_student_profile(student_info['username'], profile_data)
                if success:
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update profile")
    
    st.markdown("---")
    
    # Class Enrollment Section
    st.subheader("📚 Class Enrollment")
    
    student_username = student_info['username']
    enrolled_classes = auth.get_student_classes(student_username)
    available_classes = auth.get_available_classes()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**My Enrolled Classes**")
        if enrolled_classes:
            for class_code in enrolled_classes:
                if class_code in available_classes:
                    class_data = available_classes[class_code]
                    with st.container():
                        st.write(f"**{class_code}:** {class_data.get('class_name', 'N/A')}")
                        st.caption(f"Schedule: {class_data.get('schedule', 'N/A')} | Room: {class_data.get('room', 'N/A')}")
                        if st.button(f"Unenroll", key=f"unenroll_{class_code}"):
                            success, message = auth.unenroll_from_class(student_username, class_code)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        st.markdown("---")
        else:
            st.info("You are not enrolled in any classes yet.")
    
    with col2:
        st.write("**Available Classes**")
        if available_classes:
            # Filter out already enrolled classes
            available_to_enroll = {code: data for code, data in available_classes.items() 
                                  if code not in enrolled_classes and data.get('status') == 'active'}
            
            if available_to_enroll:
                for class_code, class_data in available_to_enroll.items():
                    with st.container():
                        st.write(f"**{class_code}:** {class_data.get('class_name', 'N/A')}")
                        st.caption(f"Instructor: {class_data.get('instructor', 'N/A')}")
                        st.caption(f"Schedule: {class_data.get('schedule', 'N/A')} | Room: {class_data.get('room', 'N/A')}")
                        st.caption(f"Students: {len(class_data.get('enrolled_students', []))}")
                        if st.button(f"Enroll", key=f"enroll_{class_code}", type="primary"):
                            success, message = auth.enroll_in_class(student_username, class_code)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        st.markdown("---")
            else:
                st.info("No new classes available to enroll in.")
        else:
            st.info("No classes available at the moment.")

def show_student_classes():
    """Show student class enrollment interface"""
    st.header("📚 Class Enrollment")
    
    auth = StudentAuth()
    session_id = st.session_state.get('student_session_id')
    
    if not session_id:
        st.error("No student session found. Please login again.")
        return
    
    student_info = auth.get_student_info(session_id)
    
    if not student_info:
        st.error("Unable to load student information")
        return
    
    student_username = student_info['username']
    enrolled_classes = auth.get_student_classes(student_username)
    available_classes = auth.get_available_classes()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("My Enrolled Classes")
        if enrolled_classes:
            for class_code in enrolled_classes:
                if class_code in available_classes:
                    class_data = available_classes[class_code]
                    with st.container():
                        st.write(f"**{class_code}:** {class_data.get('class_name', 'N/A')}")
                        st.caption(f"Instructor: {class_data.get('instructor', 'N/A')}")
                        st.caption(f"Schedule: {class_data.get('schedule', 'N/A')} | Room: {class_data.get('room', 'N/A')}")
                        st.caption(f"Enrolled Students: {len(class_data.get('enrolled_students', []))}")
                        if st.button(f"Unenroll", key=f"unenroll_{class_code}"):
                            success, message = auth.unenroll_from_class(student_username, class_code)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        st.markdown("---")
        else:
            st.info("You are not enrolled in any classes yet.")
    
    with col2:
        st.subheader("Available Classes")
        if available_classes:
            # Filter out already enrolled classes
            available_to_enroll = {code: data for code, data in available_classes.items() 
                                  if code not in enrolled_classes and data.get('status') == 'active'}
            
            if available_to_enroll:
                for class_code, class_data in available_to_enroll.items():
                    with st.container():
                        st.write(f"**{class_code}:** {class_data.get('class_name', 'N/A')}")
                        st.caption(f"Instructor: {class_data.get('instructor', 'N/A')}")
                        st.caption(f"Schedule: {class_data.get('schedule', 'N/A')} | Room: {class_data.get('room', 'N/A')}")
                        st.caption(f"Students: {len(class_data.get('enrolled_students', []))}")
                        if st.button(f"Enroll", key=f"enroll_{class_code}", type="primary"):
                            success, message = auth.enroll_in_class(student_username, class_code)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        st.markdown("---")
            else:
                st.info("No new classes available to enroll in.")
        else:
            st.info("No classes available at the moment.")

def show_student_dashboard():
    """Show a polished, student-focused dashboard"""
    st.header("📊 Student Dashboard")

    auth = st.session_state.student_auth
    session_id = st.session_state.get('student_session_id')

    if not session_id:
        st.error("No student session found. Please login again.")
        return

    student_info = auth.get_student_info(session_id)

    if not student_info:
        st.error("Unable to load student information")
        st.write(f"Debug: Session ID: {session_id}")
        return

    profile = student_info["profile"]

    # Hero / welcome card
    st.markdown(
        f"""
        <div class="metric-card" style="margin-bottom: 1.5rem; display:flex; align-items:flex-start; justify-content:space-between; gap:1.5rem;">
          <div>
            <div style="font-size:0.85rem;color:var(--text-light);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.15rem;">
              Student Overview
            </div>
            <div style="font-size:1.8rem;font-weight:700;color:var(--text-color);margin-bottom:0.25rem;">
              Welcome back, {profile['first_name'].title()} 👋
            </div>
            <div style="font-size:0.95rem;color:var(--text-light);max-width:420px;">
              Stay on top of your classes, attendance, and notifications in one clean dashboard.
            </div>
          </div>
          <div style="text-align:right;min-width:180px;">
            <div style="font-size:0.8rem;color:var(--text-light);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.35rem;">
              At a glance
            </div>
            <div style="font-size:0.95rem;color:var(--text-light);">
              <div><strong>Major:</strong> {profile['major']}</div>
              <div><strong>Year:</strong> {profile['year']}</div>
              <div><strong>Role:</strong> {student_info['role'].title()}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Check for new notifications
    student_username = student_info['username']
    all_notifications = st.session_state.db.get_notifications(limit=100)
    student_notifications = []
    for n in all_notifications or []:
        target_student = n.get('target_student')
        # Include if targeted to this student or is a general/broadcast notification
        if target_student is None or target_student == '' or target_student == student_username:
            student_notifications.append(n)

    if 'last_seen_notification_id' not in st.session_state:
        st.session_state.last_seen_notification_id = 0

    new_notifications = [
        n for n in student_notifications
        if n.get('id', 0) > st.session_state.last_seen_notification_id
    ]

    # Subtle notification banner
    if new_notifications:
        count = len(new_notifications)
        st.markdown(
            f"""
            <div style="
                border-radius: var(--radius-lg);
                padding: 0.9rem 1.1rem;
                margin-bottom: 1.25rem;
                background: rgba(251, 191, 36, 0.08);
                border: 1px solid rgba(251, 191, 36, 0.4);
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:0.75rem;
            ">
              <div style="display:flex;align-items:center;gap:0.6rem;">
                <span style="font-size:1.25rem;">🔔</span>
                <div>
                  <div style="font-weight:600;color:var(--text-color);">
                    You have {count} new notification{'' if count == 1 else 's'}.
                  </div>
                  <div style="font-size:0.9rem;color:var(--text-light);">
                    Open the Notifications tab to review important updates from your instructors and the system.
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Key stats as professional cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
              <div style="font-size:0.8rem;color:var(--text-light);text-transform:uppercase;letter-spacing:0.12em;">Your Role</div>
              <div style="font-size:1.4rem;font-weight:700;margin-top:0.25rem;">{student_info['role'].title()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
              <div style="font-size:0.8rem;color:var(--text-light);text-transform:uppercase;letter-spacing:0.12em;">Major</div>
              <div style="font-size:1.4rem;font-weight:700;margin-top:0.25rem;">{profile['major']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
              <div style="font-size:0.8rem;color:var(--text-light);text-transform:uppercase;letter-spacing:0.12em;">Year</div>
              <div style="font-size:1.4rem;font-weight:700;margin-top:0.25rem;">{profile['year']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        notification_count = len(student_notifications)
        st.markdown(
            f"""
            <div class="metric-card">
              <div style="font-size:0.8rem;color:var(--text-light);text-transform:uppercase;letter-spacing:0.12em;">Notifications</div>
              <div style="font-size:1.4rem;font-weight:700;margin-top:0.25rem;">{notification_count}</div>
              <div style="font-size:0.85rem;color:var(--text-light);margin-top:0.1rem;">total received</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Quick actions based on permissions, inside a soft card
    st.markdown(
        """
        <div style="margin-top:1.75rem;margin-bottom:0.75rem;font-weight:600;font-size:1.05rem;color:var(--text-color);">
          Quick Actions ↪
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if auth.has_student_permission(st.session_state.student_session_id, "attendance"):
                if st.button("📝 Mark Attendance", type="primary", key="dashboard_attendance", use_container_width=True):
                    st.session_state.student_page = "attendance"
                    st.rerun()

        with col2:
            if auth.has_student_permission(st.session_state.student_session_id, "read"):
                if st.button("📊 View Reports", type="primary", key="dashboard_reports", use_container_width=True):
                    st.session_state.student_page = "reports"
                    st.rerun()

        with col3:
            if st.button("🔔 Notifications", type="primary", key="dashboard_notifications", use_container_width=True):
                st.session_state.student_page = "notifications"
                st.rerun()

        with col4:
            if st.button("👤 My Profile", type="primary", key="dashboard_profile", use_container_width=True):
                st.session_state.student_page = "profile"
                st.rerun()

    # Recent notifications preview
    if student_notifications:
        st.markdown(
            """
            <div style="margin-top:2rem;margin-bottom:0.5rem;font-weight:600;font-size:1.05rem;color:var(--text-color);">
              Recent Notifications
            </div>
            """,
            unsafe_allow_html=True,
        )
        for notification in student_notifications[:3]:  # Show last 3
            st.markdown(
                f"""
                <div class="notification-card">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.75rem;">
                    <div>
                      <div style="font-weight:600;color:var(--text-color);margin-bottom:0.15rem;">
                        {notification['title']}
                      </div>
                      <div style="font-size:0.9rem;color:var(--text-light);">
                        {notification['message'][:160]}{'...' if len(notification['message']) > 160 else ''}
                      </div>
                    </div>
                    <div style="font-size:0.8rem;color:var(--text-light);white-space:nowrap;">
                      {notification['created_at']}
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Recent activity placeholder
    st.markdown(
        """
        <div style="margin-top:2rem;font-weight:600;font-size:1.05rem;color:var(--text-color);">
          Recent Activity
        </div>
        <div style="
            margin-top:0.5rem;
            padding:1rem 1.1rem;
            border-radius:var(--radius-lg);
            background:rgba(148, 163, 184, 0.08);
            border:1px dashed rgba(148, 163, 184, 0.7);
            font-size:0.9rem;
            color:var(--text-light);
        ">
          Your recent activity will appear here as you continue using Chat Ping.
        </div>
        """,
        unsafe_allow_html=True,
    )

def show_student_attendance():
    """Show student attendance interface with QR code and selfie"""
    st.header("📝 My Attendance")
    
    auth = st.session_state.student_auth
    session_id = st.session_state.get('student_session_id')
    
    if not session_id:
        st.error("No student session found. Please login again.")
        return
    
    student_info = auth.get_student_info(session_id)
    
    if not student_info:
        st.error("Unable to load student information")
        st.write(f"Debug: Session ID: {session_id}")
        return
    
    student_username = student_info['username']
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📱 Mark Attendance")
        st.caption("Scan QR code and take a selfie to mark your attendance")
        
        # QR Code Input Section
        st.markdown("### Step 1: Scan QR Code")
        st.info("📱 Use your phone camera to scan the QR code displayed by your instructor")
        
        qr_method = st.radio(
            "How do you want to input the QR code?",
            ["Paste QR Code Data", "Upload QR Code Image"],
            key="qr_input_method"
        )
        
        qr_data_input = None
        qr_image = None
        
        if qr_method == "Paste QR Code Data":
            qr_data_input = st.text_area(
                "Paste QR Code Data",
                placeholder="Paste the QR code data here after scanning...",
                height=100,
                key="qr_data_paste"
            )
        else:
            qr_image = st.file_uploader(
                "Upload QR Code Image",
                type=['jpg', 'jpeg', 'png'],
                key="qr_code_image"
            )
            if qr_image:
                st.image(qr_image, caption="Uploaded QR Code", width=200)
                st.info("💡 Note: QR code image processing requires additional setup. Please use 'Paste QR Code Data' method for now.")
        
        st.markdown("---")
        
        # Selfie Photo Section
        st.markdown("### Step 2: Take Selfie")
        st.info("📸 Take a selfie photo to verify your identity")
        
        selfie_method = st.radio(
            "How do you want to capture your selfie?",
            ["Upload Photo", "Use Camera (if available)"],
            key="selfie_method"
        )
        
        selfie_image = None
        
        if selfie_method == "Upload Photo":
            selfie_image = st.file_uploader(
                "Upload Your Selfie",
                type=['jpg', 'jpeg', 'png'],
                key="student_selfie_upload",
                help="Upload a clear selfie photo of yourself"
            )
            if selfie_image:
                st.image(selfie_image, caption="Your Selfie", width=200)
        else:
            # Camera input (Streamlit camera input)
            try:
                camera_photo = st.camera_input("Take a selfie", key="student_selfie_camera")
                if camera_photo:
                    selfie_image = camera_photo
                    st.success("✅ Selfie captured!")
            except Exception as e:
                st.warning("Camera not available. Please use 'Upload Photo' method instead.")
                selfie_image = st.file_uploader(
                    "Upload Your Selfie",
                    type=['jpg', 'jpeg', 'png'],
                    key="student_selfie_fallback"
                )
        
        st.markdown("---")
        
        # Mark Attendance Button
        if st.button("✅ Mark Attendance", type="primary", use_container_width=True):
            if not qr_data_input and not qr_image:
                st.error("❌ Please scan or paste the QR code first!")
            elif not selfie_image:
                st.error("❌ Please take or upload your selfie photo!")
            else:
                with st.spinner("Processing attendance..."):
                    try:
                        # Validate QR code
                        if qr_method == "Paste QR Code Data":
                            # Parse QR code data
                            try:
                                if isinstance(qr_data_input, str):
                                    qr_data = json.loads(qr_data_input)
                                else:
                                    qr_data = qr_data_input
                            except json.JSONDecodeError:
                                st.error("❌ Invalid QR code data format. Please check and try again.")
                                return
                        else:
                            st.error("❌ QR code image processing not yet implemented. Please use 'Paste QR Code Data' method.")
                            return
                        
                        # Validate QR code
                        is_valid, qr_result = st.session_state.validate_qr_code(qr_data)
                        
                        if not is_valid:
                            st.error(f"❌ {qr_result}")
                            return
                        
                        # Verify student is enrolled
                        class_code = qr_result["class_code"]
                        from instructor_auth import InstructorAuth
                        instructor_auth = InstructorAuth()
                        
                        if class_code not in instructor_auth.classes:
                            st.error("❌ Class not found")
                            return
                        
                        if student_username not in instructor_auth.classes[class_code]["enrolled_students"]:
                            st.error("❌ You are not enrolled in this class")
                            return
                        
                        # Process selfie with face recognition
                        selfie_bytes = selfie_image.read()
                        face_result = st.session_state.attendance_system.mark_attendance(image_bytes=selfie_bytes)
                        
                        # Check if student is recognized
                        student_recognized = False
                        if face_result.get('success') and face_result.get('recognized_faces'):
                            for face in face_result['recognized_faces']:
                                if face['name'].lower() == student_username.lower():
                                    student_recognized = True
                                    break
                        
                        # Mark attendance using QR code data
                        success, message = st.session_state.mark_attendance_from_qr(student_username, qr_result)
                        
                        if success:
                            # Add selfie verification info to attendance record
                            attendance_record = {
                                "student_username": student_username,
                                "class_code": class_code,
                                "instructor": qr_result["instructor"],
                                "session_id": qr_result["session_id"],
                                "timestamp": datetime.now().isoformat(),
                                "method": "qr_code_selfie",
                                "selfie_verified": student_recognized,
                                "face_confidence": face_result.get('recognized_faces', [{}])[0].get('confidence', 0) if face_result.get('recognized_faces') else 0
                            }
                            
                            # Update database record
                            st.session_state.db.add_attendance_record(attendance_record)
                            
                            if student_recognized:
                                st.success("✅ Attendance marked successfully! Your identity has been verified.")
                            else:
                                st.warning("⚠️ Attendance marked, but face recognition couldn't verify your identity. Please ensure you're using a clear selfie.")
                            
                            st.balloons()
                        else:
                            st.error(f"❌ {message}")
                            
                    except Exception as e:
                        st.error(f"❌ Error marking attendance: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())
    
    with col2:
        st.subheader("📊 My Attendance Records")
        
        # Get student's attendance records from database
        try:
            # Check if method exists, if not recreate database instance
            if not hasattr(st.session_state.db, 'get_attendance_records'):
                from database import DatabaseManager
                st.session_state.db = DatabaseManager()
            
            all_records = st.session_state.db.get_attendance_records()
            student_records = [
                record for record in all_records 
                if record.get('student_username', record.get('person_name', '')).lower() == student_username.lower()
            ]
            
            # Sort by timestamp (newest first)
            student_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            if student_records:
                # Show recent records
                st.write(f"**Total Records:** {len(student_records)}")
                
                # Display as dataframe
                display_records = []
                for record in student_records[:20]:  # Show last 20
                    timestamp = record.get('timestamp', '')
                    date_str = 'N/A'
                    time_str = 'N/A'
                    
                    if timestamp:
                        try:
                            if isinstance(timestamp, str):
                                dt = datetime.fromisoformat(timestamp)
                            else:
                                dt = timestamp
                            date_str = dt.strftime('%Y-%m-%d')
                            time_str = dt.strftime('%H:%M:%S')
                        except:
                            date_str = str(timestamp)[:10] if len(str(timestamp)) >= 10 else 'N/A'
                            time_str = str(timestamp)[11:19] if len(str(timestamp)) >= 19 else 'N/A'
                    
                    display_records.append({
                        'Class': record.get('class_code', 'N/A'),
                        'Date': date_str,
                        'Time': time_str,
                        'Method': record.get('method', 'N/A').replace('_', ' ').title(),
                        'Verified': '✅' if record.get('selfie_verified') else '❌'
                    })
                
                df = pd.DataFrame(display_records)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Show statistics
                st.markdown("---")
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    today_count = 0
                    for r in student_records:
                        if r.get('timestamp'):
                            try:
                                if isinstance(r['timestamp'], str):
                                    record_date = datetime.fromisoformat(r['timestamp']).date()
                                else:
                                    record_date = r['timestamp'].date() if hasattr(r['timestamp'], 'date') else datetime.now().date()
                                if record_date == datetime.now().date():
                                    today_count += 1
                            except:
                                pass
                    st.metric("Today", today_count)
                with col_stat2:
                    verified_count = len([r for r in student_records if r.get('selfie_verified')])
                    st.metric("Verified", verified_count)
                with col_stat3:
                    qr_count = len([r for r in student_records if r.get('method') == 'qr_code_selfie'])
                    st.metric("QR + Selfie", qr_count)
            else:
                st.info("No attendance records found for you")
        except Exception as e:
            st.error(f"Error loading attendance records: {str(e)}")
            st.info("No attendance records found for you")

def show_student_notifications():
    """Show student notifications interface"""
    st.header("🔔 My Notifications")

    # Professional intro card for context
    st.markdown(
        """
        <div class="metric-card" style="margin-bottom: 1.25rem;">
          <div style="font-size:0.85rem;color:var(--text-light);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.15rem;">
            Notification Center
          </div>
          <div style="font-size:1.4rem;font-weight:700;color:var(--text-color);margin-bottom:0.35rem;">
            Stay on top of announcements, reminders, and alerts.
          </div>
          <div style="font-size:0.9rem;color:var(--text-light);max-width:520px;">
            Messages are sorted by most recent first. High-priority items are highlighted so you can act on what matters quickly.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    auth = st.session_state.student_auth
    session_id = st.session_state.get('student_session_id')
    
    if not session_id:
        st.error("No student session found. Please login again.")
        return
    
    student_info = auth.get_student_info(session_id)
    
    if not student_info:
        st.error("Unable to load student information")
        return
    
    student_username = student_info['username']
    
    # Get all notifications for this student
    try:
        db = st.session_state.db
        all_notifications = db.get_notifications(limit=100)
        
        # Filter notifications for this student
        student_notifications = []
        for n in all_notifications or []:
            target_student = n.get('target_student')
            # Include if targeted to this student or is a general/broadcast notification
            if target_student is None or target_student == '' or target_student == student_username:
                student_notifications.append(n)
        
        # Sort by created_at (newest first)
        student_notifications.sort(
            key=lambda x: x.get('created_at') or x.get('timestamp') or '',
            reverse=True
        )
        
        if not student_notifications:
            st.info("📭 No notifications yet. You'll see notifications from your instructors here.")
            return

        st.success(f"📬 You have {len(student_notifications)} notification(s)")
        st.markdown("")

        # Display notifications using polished cards
        type_labels = {
            'info': 'ℹ️ Information',
            'alert': '⚠️ Alert',
            'reminder': '⏰ Reminder',
            'announcement': '📢 Announcement',
            'attendance': '📝 Attendance',
            'test': '🧪 Test'
        }

        for idx, notification in enumerate(student_notifications):
            priority = notification.get('priority', 1)
            priority_emoji = "🔴" if priority >= 4 else "🟡" if priority >= 3 else "🟢"
            title = notification.get('title', 'Notification')
            message = notification.get('message', '')

            notification_type = notification.get('notification_type', 'info')
            type_label = type_labels.get(notification_type, notification_type)

            created_at = notification.get('created_at') or notification.get('timestamp', '')
            date_str = "N/A"
            if created_at:
                try:
                    if isinstance(created_at, str):
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00') if 'Z' in created_at else created_at)
                    else:
                        dt = created_at
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    date_str = str(created_at)

            st.markdown(
                f"""
                <div class="notification-card">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.75rem;">
                    <div>
                      <div style="font-weight:600;color:var(--text-color);margin-bottom:0.15rem;">
                        {priority_emoji} {title}
                      </div>
                      <div style="font-size:0.9rem;color:var(--text-light);white-space:pre-wrap;">
                        {message}
                      </div>
                      <div style="margin-top:0.6rem;font-size:0.8rem;color:var(--text-light);display:flex;flex-wrap:wrap;gap:1.25rem;">
                        <span><strong>Type:</strong> {type_label}</span>
                        <span><strong>Date:</strong> {date_str}</span>
                        <span><strong>Priority:</strong> {priority}/5</span>
                      </div>
                    </div>
                    <div>
                      <!-- Placeholder for Streamlit button area -->
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Simple mark-as-read interaction (non-persistent, for UX feedback)
            if st.button("✓ Mark as read", key=f"mark_read_{idx}", help="This will clear the highlight for this session only."):
                st.success(f"Marked '{title}' as read for this session.")
        
        # Refresh button
        if st.button("🔄 Refresh Notifications", key="refresh_notifications"):
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading notifications: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def show_student_reports():
    """Show student reports interface"""
    st.header("📊 My Reports")
    
    auth = st.session_state.student_auth
    session_id = st.session_state.get('student_session_id')
    
    if not session_id:
        st.error("No student session found. Please login again.")
        return
    
    student_info = auth.get_student_info(session_id)
    
    if not student_info:
        st.error("Unable to load student information")
        st.write(f"Debug: Session ID: {session_id}")
        return
    
    # Student-specific attendance stats
    st.subheader("My Attendance Summary")
    
    attendance_summary = st.session_state.attendance_system.get_attendance_summary(30)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", attendance_summary.get('stats', {}).get('total_attendance', 0))
    with col2:
        st.metric("This Month", attendance_summary.get('stats', {}).get('unique_people', 0))
    with col3:
        st.metric("Today", attendance_summary.get('stats', {}).get('today_attendance', 0))
    
    # Simple attendance chart
    st.subheader("My Attendance Trend")
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    attendance_data = [5, 7, 6, 8, 9, 7, 8]  # Sample data
    
    df_trend = pd.DataFrame({
        'Date': dates,
        'Attendance': attendance_data
    })
    
    fig_trend = px.line(df_trend, x='Date', y='Attendance', title='My Attendance Trend (Last 7 Days)')
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Academic information
    st.subheader("Academic Information")
    profile = student_info["profile"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Student ID:** {profile['student_id']}")
        st.write(f"**Major:** {profile['major']}")
        st.write(f"**Year:** {profile['year']}")
    
    with col2:
        st.write(f"**Username:** {student_info['username']}")
        st.write(f"**Email:** {student_info['email']}")
        st.write(f"**Last Login:** {student_info['last_login'][:19] if student_info['last_login'] else 'Never'}")

def require_student_auth(func):
    """Decorator to require student authentication for functions"""
    def wrapper(*args, **kwargs):
        if not check_student_auth():
            st.error("🔒 Student authentication required!")
            show_student_login()
            return
        return func(*args, **kwargs)
    return wrapper

    