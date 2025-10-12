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
    
    def authenticate_student(self, username, password):
        """Authenticate student"""
        if username not in self.students:
            return False, "Invalid username or password"
        
        student = self.students[username]
        if not self.verify_password(password, student["password_hash"]):
            return False, "Invalid username or password"
        
        # Update last login
        student["last_login"] = datetime.now().isoformat()
        self.save_students()
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        self.student_sessions[session_id] = {
            "username": username,
            "role": student["role"],
            "permissions": student["permissions"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=8)).isoformat()  # 8 hour session
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
                remember_me = st.checkbox("Remember me")
            
            if login_button:
                if username and password:
                    auth = StudentAuth()
                    success, result = auth.authenticate_student(username, password)
                    
                    if success:
                        # Use the same auth instance that created the session
                        st.session_state.student_auth = auth
                        st.session_state.student_logged_in = True
                        st.session_state.student_session_id = result
                        st.session_state.student_username = username
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
    
    # Show default credentials info
    with st.expander("ℹ️ Default Student Credentials"):
        st.code("""
        Username: student
        Password: student123
        """)
        st.warning("⚠️ Please change the default password after first login!")

    # AI Assistant panel (optional helper on login screen)
    with st.expander("🤖 AI Assistant (optional)"):
        ai = AIFeatures()
        user_text = st.text_area("Tell the assistant what you want to focus on today")
        if st.button("Analyze", key="student_ai_analyze"):
            if user_text.strip():
                sentiment = ai.analyze_sentiment(user_text)
                keywords = ai.extract_keywords(user_text, max_keywords=5)
                suggestion = ai.suggest_optimal_time("announcement")
                st.write(f"**Sentiment:** {sentiment.get('sentiment','neutral').title()} (conf: {sentiment.get('confidence',0.5):.2f})")
                st.write(f"**Keywords:** {', '.join(keywords) if keywords else 'None'}")
                st.write(f"**Suggested time to start:** {suggestion.strftime('%Y-%m-%d %H:%M')}")

    # Quick Meet section
    with st.expander("📹 Quick Meet"):
        default_room = suggest_room_for_user(st.session_state.get('student_username', 'student'))
        room = st.text_input("Room name", value=default_room, key="student_meet_room")
        if st.button("Start/Join Meeting", key="student_meet_start"):
            st.info("If the embed does not load, click the 'open in new tab' link below.")
            render_meeting(room_name=room, height=600)
            st.markdown(f"[Open in new tab](https://meet.jit.si/{room})")

def show_student_logout():
    """Display student logout button"""
    if st.sidebar.button("🚪 Logout", type="secondary"):
        if 'student_session_id' in st.session_state:
            auth = StudentAuth()
            auth.logout_student(st.session_state.student_session_id)
        
        # Clear student session state
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

def show_student_dashboard():
    """Show student dashboard"""
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
    
    # Welcome message
    profile = student_info["profile"]
    st.success(f"Welcome back, {profile['first_name']}!")
    
    # Student stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Your Role", student_info['role'].title())
    with col2:
        st.metric("Major", profile['major'])
    with col3:
        st.metric("Year", profile['year'])
    with col4:
        st.metric("Notifications", "🔔 On" if profile.get('notifications_enabled') else "🔕 Off")
    
    # Quick actions based on permissions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if auth.has_student_permission(st.session_state.student_session_id, "attendance"):
            if st.button("📝 Mark Attendance", type="primary", key="dashboard_attendance"):
                st.session_state.student_page = "attendance"
                st.rerun()
    
    with col2:
        if auth.has_student_permission(st.session_state.student_session_id, "read"):
            if st.button("📊 View Reports", type="primary", key="dashboard_reports"):
                st.session_state.student_page = "reports"
                st.rerun()
    
    with col3:
        if st.button("👤 My Profile", type="primary", key="dashboard_profile"):
            st.session_state.student_page = "profile"
            st.rerun()
    
    # Recent activity (placeholder)
    st.subheader("Recent Activity")
    st.info("Your recent activity will appear here as you use the system.")

def show_student_attendance():
    """Show student attendance interface"""
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
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Mark Attendance")
        
        uploaded_file = st.file_uploader("Upload Photo for Attendance", type=['jpg', 'jpeg', 'png'], key="student_attendance_photo_auth")
        
        if st.button("Mark Attendance", type="primary"):
            if uploaded_file:
                image_bytes = uploaded_file.read()
                
                with st.spinner("Processing attendance..."):
                    # Use the attendance system to process the image
                    result = st.session_state.attendance_system.mark_attendance(image_bytes=image_bytes)
                
                if result['success']:
                    st.success("✅ Attendance marked successfully!")
                    
                    # Show recognized faces
                    if result['recognized_faces']:
                        st.write("**Recognized:**")
                        for face in result['recognized_faces']:
                            st.write(f"• {face['name']} (Confidence: {face['confidence']:.2f})")
                    
                    # Show unknown faces
                    if result['unknown_faces']:
                        st.warning(f"⚠️ {len(result['unknown_faces'])} unknown faces detected")
                    
                    # Create notification
                    st.session_state.notification_engine.create_attendance_notification(result)
                else:
                    st.error("❌ Failed to mark attendance")
            else:
                st.warning("Please upload a photo")
    
    with col2:
        st.subheader("My Attendance Records")
        
        # Get student's attendance records
        attendance_summary = st.session_state.attendance_system.get_attendance_summary(30)
        student_records = []
        
        if attendance_summary.get('today_attendance'):
            for record in attendance_summary['today_attendance']:
                if record['person_name'].lower() == student_info['username'].lower():
                    student_records.append(record)
        
        if student_records:
            df = pd.DataFrame(student_records)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No attendance records found for you")

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

