import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from ai_features import AIFeatures
from meetings import render_meeting, suggest_room_for_user

class InstructorAuth:
    def __init__(self):
        self.instructors_file = "instructors.json"
        self.instructor_sessions_file = "instructor_sessions.json"
        self.classes_file = "classes.json"
        self.load_instructors()
        self.load_instructor_sessions()
        self.load_classes()
    
    def load_instructors(self):
        """Load instructors from file"""
        if os.path.exists(self.instructors_file):
            with open(self.instructors_file, 'r') as f:
                self.instructors = json.load(f)
        else:
            # Create default instructor
            self.instructors = {
                "instructor": {
                    "password_hash": self.hash_password("instructor123"),
                    "email": "instructor@example.com",
                    "role": "instructor",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "permissions": ["class_management", "attendance", "notifications", "reports"],
                    "profile": {
                        "first_name": "Dr. Sarah",
                        "last_name": "Johnson",
                        "department": "Computer Science",
                        "phone": "+1-555-0123",
                        "office": "CS-101",
                        "notifications_enabled": True,
                        "specialization": "AI/ML"
                    }
                }
            }
            self.save_instructors()
    
    def save_instructors(self):
        """Save instructors to file"""
        with open(self.instructors_file, 'w') as f:
            json.dump(self.instructors, f, indent=2)
    
    def load_instructor_sessions(self):
        """Load active instructor sessions from file"""
        if os.path.exists(self.instructor_sessions_file):
            with open(self.instructor_sessions_file, 'r') as f:
                self.instructor_sessions = json.load(f)
        else:
            self.instructor_sessions = {}
    
    def save_instructor_sessions(self):
        """Save active instructor sessions to file"""
        with open(self.instructor_sessions_file, 'w') as f:
            json.dump(self.instructor_sessions, f, indent=2)
    
    def load_classes(self):
        """Load classes from file"""
        if os.path.exists(self.classes_file):
            with open(self.classes_file, 'r') as f:
                self.classes = json.load(f)
        else:
            # Create sample classes
            self.classes = {
                "CS101": {
                    "class_name": "Introduction to Computer Science",
                    "instructor": "instructor",
                    "schedule": "Mon/Wed/Fri 10:00-11:00",
                    "room": "CS-101",
                    "enrolled_students": ["student1", "student2", "student3"],
                    "created_at": datetime.now().isoformat(),
                    "status": "active"
                },
                "CS201": {
                    "class_name": "Data Structures and Algorithms",
                    "instructor": "instructor",
                    "schedule": "Tue/Thu 14:00-15:30",
                    "room": "CS-201",
                    "enrolled_students": ["student4", "student5", "student6"],
                    "created_at": datetime.now().isoformat(),
                    "status": "active"
                }
            }
            self.save_classes()
    
    def save_classes(self):
        """Save classes to file"""
        with open(self.classes_file, 'w') as f:
            json.dump(self.classes, f, indent=2)
    
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
    
    def register_instructor(self, username, password, email, first_name, last_name, department="Computer Science", specialization=""):
        """Register a new instructor"""
        if username in self.instructors:
            return False, "Username already exists"
        
        if email in [instructor_data.get('email', '') for instructor_data in self.instructors.values()]:
            return False, "Email already registered"
        
        self.instructors[username] = {
            "password_hash": self.hash_password(password),
            "email": email,
            "role": "instructor",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "permissions": ["class_management", "attendance", "notifications", "reports"],
            "profile": {
                "first_name": first_name,
                "last_name": last_name,
                "department": department,
                "phone": "",
                "office": "",
                "notifications_enabled": True,
                "specialization": specialization
            }
        }
        
        self.save_instructors()
        return True, "Instructor registered successfully"
    
    def authenticate_instructor(self, username, password):
        """Authenticate instructor"""
        if username not in self.instructors:
            return False, "Invalid username or password"
        
        instructor = self.instructors[username]
        if not self.verify_password(password, instructor["password_hash"]):
            return False, "Invalid username or password"
        
        # Update last login
        instructor["last_login"] = datetime.now().isoformat()
        self.save_instructors()
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        self.instructor_sessions[session_id] = {
            "username": username,
            "role": instructor["role"],
            "permissions": instructor["permissions"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=12)).isoformat()  # 12 hour session
        }
        self.save_instructor_sessions()
        
        return True, session_id
    
    def verify_instructor_session(self, session_id):
        """Verify instructor session"""
        if session_id not in self.instructor_sessions:
            return False, None
        
        session = self.instructor_sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            # Session expired
            del self.instructor_sessions[session_id]
            self.save_instructor_sessions()
            return False, None
        
        return True, session
    
    def logout_instructor(self, session_id):
        """Logout instructor"""
        if session_id in self.instructor_sessions:
            del self.instructor_sessions[session_id]
            self.save_instructor_sessions()
        return True
    
    def get_instructor_info(self, session_id):
        """Get instructor information from session"""
        is_valid, session = self.verify_instructor_session(session_id)
        if not is_valid:
            return None
        
        username = session["username"]
        instructor_data = self.instructors[username]
        
        return {
            "username": username,
            "role": session["role"],
            "permissions": session["permissions"],
            "email": instructor_data["email"],
            "profile": instructor_data["profile"],
            "last_login": instructor_data["last_login"]
        }
    
    def has_instructor_permission(self, session_id, permission):
        """Check if instructor has specific permission"""
        instructor_info = self.get_instructor_info(session_id)
        if not instructor_info:
            return False
        
        return permission in instructor_info["permissions"]
    
    def create_class(self, class_code, class_name, instructor_username, schedule, room, enrolled_students=None):
        """Create a new class"""
        if class_code in self.classes:
            return False, "Class code already exists"
        
        if enrolled_students is None:
            enrolled_students = []
        
        self.classes[class_code] = {
            "class_name": class_name,
            "instructor": instructor_username,
            "schedule": schedule,
            "room": room,
            "enrolled_students": enrolled_students,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.save_classes()
        return True, "Class created successfully"
    
    def get_instructor_classes(self, instructor_username):
        """Get classes taught by instructor"""
        instructor_classes = {}
        for class_code, class_data in self.classes.items():
            if class_data["instructor"] == instructor_username:
                instructor_classes[class_code] = class_data
        
        return instructor_classes
    
    def add_student_to_class(self, class_code, student_username):
        """Add student to class"""
        if class_code not in self.classes:
            return False, "Class not found"
        
        if student_username not in self.classes[class_code]["enrolled_students"]:
            self.classes[class_code]["enrolled_students"].append(student_username)
            self.save_classes()
            return True, "Student added to class"
        else:
            return False, "Student already enrolled"
    
    def remove_student_from_class(self, class_code, student_username):
        """Remove student from class"""
        if class_code not in self.classes:
            return False, "Class not found"
        
        if student_username in self.classes[class_code]["enrolled_students"]:
            self.classes[class_code]["enrolled_students"].remove(student_username)
            self.save_classes()
            return True, "Student removed from class"
        else:
            return False, "Student not enrolled"
    
    def get_instructor_stats(self):
        """Get instructor system statistics"""
        return {
            "total_instructors": len(self.instructors),
            "active_sessions": len(self.instructor_sessions),
            "total_classes": len(self.classes),
            "departments": list(set(instructor["profile"].get("department", "Computer Science") for instructor in self.instructors.values()))
        }

def show_instructor_login():
    """Display instructor login form"""
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
    st.markdown('<h2 class="login-header">🎓 Instructor Login</h2>', unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("instructor_login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("Login", type="primary")
            with col2:
                remember_me = st.checkbox("Remember me")
            
            if login_button:
                if username and password:
                    auth = InstructorAuth()
                    success, result = auth.authenticate_instructor(username, password)
                    
                    if success:
                        st.session_state.instructor_logged_in = True
                        st.session_state.instructor_session_id = result
                        st.session_state.instructor_username = username
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        with st.form("instructor_register_form"):
            st.subheader("Register as Instructor")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", placeholder="Enter first name")
                username = st.text_input("Username", placeholder="Choose username")
            with col2:
                last_name = st.text_input("Last Name", placeholder="Enter last name")
                email = st.text_input("Email", placeholder="Enter email address")
            
            department = st.selectbox("Department", ["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "Engineering", "Business", "Arts"])
            specialization = st.text_input("Specialization", placeholder="e.g., AI/ML, Database Systems")
            password = st.text_input("Password", type="password", placeholder="Choose password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            
            if st.form_submit_button("Register", type="primary"):
                if all([first_name, last_name, username, email, password, confirm_password]):
                    if password == confirm_password:
                        if len(password) >= 6:
                            auth = InstructorAuth()
                            success, message = auth.register_instructor(
                                username, password, email, first_name, last_name, department, specialization
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
    with st.expander("ℹ️ Default Instructor Credentials"):
        st.code("""
        Username: instructor
        Password: instructor123
        """)
        st.warning("⚠️ Please change the default password after first login!")

    # AI Assistant panel for instructors
    with st.expander("🤖 AI Assistant (optional)"):
        ai = AIFeatures()
        user_text = st.text_area("Describe class goals or announcements")
        if st.button("Analyze", key="instructor_ai_analyze"):
            if user_text.strip():
                smart = ai.generate_smart_notification(user_text, notification_type='announcement')
                st.write(f"**Suggested Title:** {smart['title']}")
                st.write(f"**Message:** {smart['message']}")
                st.write(f"**Category:** {smart['category']} | **Priority:** {smart['priority']}")
                st.write(f"**Suggested time:** {smart['suggested_time'].strftime('%Y-%m-%d %H:%M')}")

    # Quick Meet section
    with st.expander("📹 Quick Meet"):
        default_room = suggest_room_for_user(st.session_state.get('instructor_username', 'instructor'))
        room = st.text_input("Room name", value=default_room, key="instructor_meet_room")
        if st.button("Start/Join Meeting", key="instructor_meet_start"):
            st.info("If the embed does not load, click the 'open in new tab' link below.")
            render_meeting(room_name=room, height=600)
            st.markdown(f"[Open in new tab](https://meet.jit.si/{room})")

def show_instructor_logout():
    """Display instructor logout button"""
    if st.sidebar.button("🚪 Logout", type="secondary"):
        if 'instructor_session_id' in st.session_state:
            auth = InstructorAuth()
            auth.logout_instructor(st.session_state.instructor_session_id)
        
        # Clear instructor session state
        for key in ['instructor_logged_in', 'instructor_session_id', 'instructor_username']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("✅ Logged out successfully!")
        st.rerun()

def check_instructor_auth():
    """Check if instructor is authenticated"""
    if 'instructor_logged_in' not in st.session_state or not st.session_state.instructor_logged_in:
        return False
    
    if 'instructor_session_id' not in st.session_state:
        return False
    
    auth = InstructorAuth()
    is_valid, session = auth.verify_instructor_session(st.session_state.instructor_session_id)
    
    if not is_valid:
        # Session expired or invalid
        for key in ['instructor_logged_in', 'instructor_session_id', 'instructor_username']:
            if key in st.session_state:
                del st.session_state[key]
        return False
    
    return True

def show_instructor_dashboard():
    """Show instructor dashboard"""
    st.header("🎓 Instructor Dashboard")
    
    auth = InstructorAuth()
    instructor_info = auth.get_instructor_info(st.session_state.instructor_session_id)
    
    if not instructor_info:
        st.error("Unable to load instructor information")
        return
    
    # Welcome message
    profile = instructor_info["profile"]
    st.success(f"Welcome back, {profile['first_name']} {profile['last_name']}!")
    
    # Instructor stats
    col1, col2, col3, col4 = st.columns(4)
    
    instructor_classes = auth.get_instructor_classes(instructor_info['username'])
    
    with col1:
        st.metric("My Classes", len(instructor_classes))
    with col2:
        total_students = sum(len(class_data["enrolled_students"]) for class_data in instructor_classes.values())
        st.metric("Total Students", total_students)
    with col3:
        st.metric("Department", profile['department'])
    with col4:
        st.metric("Specialization", profile.get('specialization', 'N/A'))
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Manage Classes", type="primary"):
            st.session_state.instructor_page = "class_management"
            st.rerun()
    
    with col2:
        if st.button("📝 Take Attendance", type="primary"):
            st.session_state.instructor_page = "attendance"
            st.rerun()
    
    with col3:
        if st.button("🔔 Send Notifications", type="primary"):
            st.session_state.instructor_page = "notifications"
            st.rerun()
    
    # Recent classes
    st.subheader("My Classes")
    if instructor_classes:
        for class_code, class_data in instructor_classes.items():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{class_code}:** {class_data['class_name']}")
                    st.write(f"Schedule: {class_data['schedule']} | Room: {class_data['room']}")
                
                with col2:
                    st.write(f"Students: {len(class_data['enrolled_students'])}")
                
                with col3:
                    if st.button(f"Manage", key=f"dashboard_manage_{class_code}"):
                        st.session_state.selected_class = class_code
                        st.session_state.instructor_page = "class_detail"
                        st.rerun()
    else:
        st.info("No classes assigned yet. Create a new class to get started!")

def show_instructor_profile():
    """Show instructor profile management"""
    st.header("👤 Instructor Profile")
    
    auth = InstructorAuth()
    instructor_info = auth.get_instructor_info(st.session_state.instructor_session_id)
    
    if not instructor_info:
        st.error("Unable to load instructor information")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Profile Information")
        
        # Display current profile
        profile = instructor_info["profile"]
        # Show profile picture if available
        avatar_dir = os.path.join(os.getcwd(), "avatars")
        avatar_path = os.path.join(avatar_dir, f"{instructor_info['username']}.png")
        if os.path.exists(avatar_path):
            st.image(avatar_path, caption="Profile Picture", width=160)
        st.write(f"**Name:** {profile['first_name']} {profile['last_name']}")
        st.write(f"**Username:** {instructor_info['username']}")
        st.write(f"**Email:** {instructor_info['email']}")
        st.write(f"**Department:** {profile['department']}")
        st.write(f"**Specialization:** {profile.get('specialization', 'N/A')}")
        st.write(f"**Office:** {profile.get('office', 'N/A')}")
        st.write(f"**Role:** {instructor_info['role']}")
        st.write(f"**Last Login:** {instructor_info['last_login'][:19] if instructor_info['last_login'] else 'Never'}")
    
    with col2:
        st.subheader("Update Profile")
        
        with st.form("update_instructor_profile_form"):
            uploaded_avatar = st.file_uploader("Profile Picture", type=['png', 'jpg', 'jpeg'], key="instructor_profile_avatar")
            new_first_name = st.text_input("First Name", value=profile['first_name'])
            new_last_name = st.text_input("Last Name", value=profile['last_name'])
            new_department = st.selectbox("Department", 
                ["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "Engineering", "Business", "Arts"],
                index=["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "Engineering", "Business", "Arts"].index(profile.get('department', 'Computer Science'))
            )
            new_specialization = st.text_input("Specialization", value=profile.get('specialization', ''))
            new_office = st.text_input("Office", value=profile.get('office', ''))
            new_phone = st.text_input("Phone", value=profile.get('phone', ''))
            notifications_enabled = st.checkbox("Enable Notifications", value=profile.get('notifications_enabled', True))
            
            if st.form_submit_button("Update Profile", type="primary"):
                profile_data = {
                    "first_name": new_first_name,
                    "last_name": new_last_name,
                    "department": new_department,
                    "specialization": new_specialization,
                    "office": new_office,
                    "phone": new_phone,
                    "notifications_enabled": notifications_enabled
                }
                
                # Update instructor profile
                if instructor_info['username'] in auth.instructors:
                    auth.instructors[instructor_info['username']]["profile"].update(profile_data)
                    auth.save_instructors()
                    # Save avatar if uploaded
                    if uploaded_avatar is not None:
                        try:
                            if not os.path.exists(avatar_dir):
                                os.makedirs(avatar_dir, exist_ok=True)
                            with open(avatar_path, 'wb') as f:
                                f.write(uploaded_avatar.getbuffer())
                            st.success("📷 Profile picture updated!")
                        except Exception as e:
                            st.warning(f"Could not save profile picture: {e}")
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update profile")

def require_instructor_auth(func):
    """Decorator to require instructor authentication for functions"""
    def wrapper(*args, **kwargs):
        if not check_instructor_auth():
            st.error("🔒 Instructor authentication required!")
            show_instructor_login()
            return
        return func(*args, **kwargs)
    return wrapper

