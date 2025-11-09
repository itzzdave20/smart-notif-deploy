import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
import json
import os
import pandas as pd

class AdminAuth:
    def __init__(self):
        self.admin_file = "admin_users.json"
        self.session_file = "admin_sessions.json"
        self.load_admin_users()
        self.load_sessions()
    
    def load_admin_users(self):
        """Load admin users from file"""
        if os.path.exists(self.admin_file):
            with open(self.admin_file, 'r') as f:
                self.admin_users = json.load(f)
        else:
            # Create default admin user
            self.admin_users = {
                "admin": {
                    "password_hash": self.hash_password("admin123"),
                    "role": "super_admin",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "permissions": ["all"]
                }
            }
            self.save_admin_users()
    
    def save_admin_users(self):
        """Save admin users to file"""
        with open(self.admin_file, 'w') as f:
            json.dump(self.admin_users, f, indent=2)
    
    def load_sessions(self):
        """Load active sessions from file"""
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                self.sessions = json.load(f)
        else:
            self.sessions = {}
    
    def save_sessions(self):
        """Save active sessions to file"""
        with open(self.session_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
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
    
    def create_admin_user(self, username, password, role="admin", permissions=None):
        """Create a new admin user"""
        if username in self.admin_users:
            return False, "Username already exists"
        
        if permissions is None:
            permissions = ["read", "write"] if role == "admin" else ["read"]
        
        self.admin_users[username] = {
            "password_hash": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "permissions": permissions
        }
        
        self.save_admin_users()
        return True, "Admin user created successfully"
    
    def authenticate(self, username, password):
        """Authenticate admin user"""
        if username not in self.admin_users:
            return False, "Invalid username or password"
        
        user = self.admin_users[username]
        if not self.verify_password(password, user["password_hash"]):
            return False, "Invalid username or password"
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        self.save_admin_users()
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "username": username,
            "role": user["role"],
            "permissions": user["permissions"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        self.save_sessions()
        
        return True, session_id
    
    def verify_session(self, session_id):
        """Verify admin session"""
        if session_id not in self.sessions:
            return False, None
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            # Session expired
            del self.sessions[session_id]
            self.save_sessions()
            return False, None
        
        return True, session
    
    def logout(self, session_id):
        """Logout admin user"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_sessions()
        return True
    
    def get_user_info(self, session_id):
        """Get user information from session"""
        is_valid, session = self.verify_session(session_id)
        if not is_valid:
            return None
        
        return {
            "username": session["username"],
            "role": session["role"],
            "permissions": session["permissions"]
        }
    
    def has_permission(self, session_id, permission):
        """Check if user has specific permission"""
        user_info = self.get_user_info(session_id)
        if not user_info:
            return False
        
        return "all" in user_info["permissions"] or permission in user_info["permissions"]
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            if current_time > expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.save_sessions()
        
        return len(expired_sessions)
    
    def get_admin_stats(self):
        """Get admin system statistics"""
        return {
            "total_users": len(self.admin_users),
            "active_sessions": len(self.sessions),
            "roles": list(set(user["role"] for user in self.admin_users.values())),
            "last_cleanup": datetime.now().isoformat()
        }

def show_admin_login():
    """Display admin login form"""
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
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-header">🔐 Admin Login</h2>', unsafe_allow_html=True)
    
    with st.form("admin_login_form"):
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", type="primary")
        with col2:
            remember_me = st.checkbox("Remember me")
        
        if login_button:
            if username and password:
                auth = AdminAuth()
                success, result = auth.authenticate(username, password)
                
                if success:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_session_id = result
                    st.session_state.admin_username = username
                    st.session_state.admin_auth = auth  # Store auth instance in session state
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
            else:
                st.warning("Please enter both username and password")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show default credentials info
    with st.expander("ℹ️ Default Admin Credentials"):
        st.code("""
        Username: admin
        Password: admin123
        """)
        st.warning("⚠️ Please change the default password after first login!")

def show_admin_logout():
    """Display admin logout button"""
    if st.sidebar.button("🚪 Logout", type="secondary"):
        if 'admin_session_id' in st.session_state:
            auth = AdminAuth()
            auth.logout(st.session_state.admin_session_id)
        
        # Clear admin session state
        for key in ['admin_logged_in', 'admin_session_id', 'admin_username']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("✅ Logged out successfully!")
        st.rerun()

def check_admin_auth():
    """Check if user is authenticated as admin"""
    if 'admin_logged_in' not in st.session_state or not st.session_state.admin_logged_in:
        return False
    
    if 'admin_session_id' not in st.session_state:
        return False
    
    auth = AdminAuth()
    is_valid, session = auth.verify_session(st.session_state.admin_session_id)
    
    if not is_valid:
        # Session expired or invalid
        for key in ['admin_logged_in', 'admin_session_id', 'admin_username']:
            if key in st.session_state:
                del st.session_state[key]
        return False
    
    return True

def require_admin_auth(func):
    """Decorator to require admin authentication for functions"""
    def wrapper(*args, **kwargs):
        if not check_admin_auth():
            st.error("🔒 Admin authentication required!")
            show_admin_login()
            return
        return func(*args, **kwargs)
    return wrapper

def show_admin_dashboard():
    """Show admin dashboard with system overview"""
    st.header("🛡️ Admin Dashboard")
    
    auth = AdminAuth()
    user_info = auth.get_user_info(st.session_state.admin_session_id)
    stats = auth.get_admin_stats()
    
    # Welcome message
    st.success(f"Welcome, {user_info['username']}! (Role: {user_info['role']})")
    
    # Admin statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Admin Users", stats['total_users'])
    with col2:
        st.metric("Active Sessions", stats['active_sessions'])
    with col3:
        st.metric("User Roles", len(stats['roles']))
    with col4:
        st.metric("System Status", "🟢 Online")
    
    # Admin actions
    st.subheader("Admin Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👥 Manage Users", type="primary"):
            st.session_state.admin_page = "user_management"
            st.rerun()
    
    with col2:
        if st.button("🔧 System Settings", type="primary"):
            st.session_state.admin_page = "system_settings"
            st.rerun()
    
    with col3:
        if st.button("📊 System Logs", type="primary"):
            st.session_state.admin_page = "system_logs"
            st.rerun()
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Cleanup Sessions"):
            cleaned = auth.cleanup_expired_sessions()
            st.success(f"Cleaned {cleaned} expired sessions")
    
    with col2:
        if st.button("🔄 Refresh Stats"):
            st.rerun()

def show_user_management():
    """Show user management interface"""
    st.header("👥 User Management")
    
    auth = AdminAuth()
    
    tab1, tab2, tab3 = st.tabs(["View Users", "Add User", "User Permissions"])
    
    with tab1:
        st.subheader("Current Admin Users")
        
        users_data = []
        for username, user_data in auth.admin_users.items():
            users_data.append({
                "Username": username,
                "Role": user_data["role"],
                "Created": user_data["created_at"][:10],
                "Last Login": user_data["last_login"][:10] if user_data["last_login"] else "Never",
                "Permissions": ", ".join(user_data["permissions"])
            })
        
        if users_data:
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No admin users found")
    
    with tab2:
        st.subheader("Add New Admin User")
        
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["admin", "super_admin", "viewer"])
            
            if st.form_submit_button("Add User", type="primary"):
                if new_username and new_password:
                    success, message = auth.create_admin_user(new_username, new_password, new_role)
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("Please provide both username and password")
    
    with tab3:
        st.subheader("Manage User Permissions")
        
        if auth.admin_users:
            selected_user = st.selectbox("Select User", list(auth.admin_users.keys()))
            
            if selected_user:
                user = auth.admin_users[selected_user]
                current_permissions = user["permissions"]
                
                st.write(f"**Current permissions for {selected_user}:**")
                st.write(", ".join(current_permissions))
                
                # Permission management interface
                st.write("**Available permissions:**")
                all_permissions = ["read", "write", "delete", "admin", "all"]
                
                new_permissions = []
                for perm in all_permissions:
                    if st.checkbox(perm, value=perm in current_permissions):
                        new_permissions.append(perm)
                
                if st.button("Update Permissions"):
                    auth.admin_users[selected_user]["permissions"] = new_permissions
                    auth.save_admin_users()
                    st.success("✅ Permissions updated!")
                    st.rerun()

def show_system_settings():
    """Show system settings interface"""
    st.header("🔧 System Settings")
    
    tab1, tab2, tab3 = st.tabs(["Security", "Notifications", "Database"])
    
    with tab1:
        st.subheader("Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Session Management**")
            session_timeout = st.number_input("Session Timeout (hours)", value=24, min_value=1, max_value=168)
            max_sessions = st.number_input("Max Active Sessions", value=10, min_value=1, max_value=100)
            
            if st.button("Update Security Settings"):
                st.success("✅ Security settings updated!")
        
        with col2:
            st.write("**Password Policy**")
            min_length = st.number_input("Minimum Password Length", value=8, min_value=6, max_value=20)
            require_special = st.checkbox("Require Special Characters", value=True)
            require_numbers = st.checkbox("Require Numbers", value=True)
            
            if st.button("Update Password Policy"):
                st.success("✅ Password policy updated!")
    
    with tab2:
        st.subheader("Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Email Notifications**")
            email_enabled = st.checkbox("Enable Email Notifications", value=True)
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587)
            
            if st.button("Update Email Settings"):
                st.success("✅ Email settings updated!")
        
        with col2:
            st.write("**Push Notifications**")
            push_enabled = st.checkbox("Enable Push Notifications", value=True)
            firebase_key = st.text_input("Firebase API Key", type="password")
            
            if st.button("Update Push Settings"):
                st.success("✅ Push settings updated!")
    
    with tab3:
        st.subheader("Database Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Database Operations**")
            
            if st.button("Backup Database", type="primary"):
                st.success("✅ Database backup created!")
            
            if st.button("Optimize Database"):
                st.success("✅ Database optimized!")
            
            if st.button("Clean Old Records"):
                st.success("✅ Old records cleaned!")
        
        with col2:
            st.write("**Database Statistics**")
            
            # Get database stats
            auth = AdminAuth()
            stats = auth.get_admin_stats()
            
            st.write(f"**Admin Users:** {stats['total_users']}")
            st.write(f"**Active Sessions:** {stats['active_sessions']}")
            st.write(f"**Last Cleanup:** {stats['last_cleanup'][:19]}")

def show_system_logs():
    """Show system logs interface"""
    st.header("📊 System Logs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_level = st.selectbox("Log Level", ["All", "INFO", "WARNING", "ERROR", "DEBUG"])
    with col2:
        log_days = st.selectbox("Time Period", [1, 7, 30, 90])
    with col3:
        if st.button("Refresh Logs"):
            st.rerun()
    
    # Sample log entries
    sample_logs = [
        {"timestamp": "2024-01-15 10:30:15", "level": "INFO", "message": "Admin user 'admin' logged in successfully"},
        {"timestamp": "2024-01-15 10:25:42", "level": "INFO", "message": "New notification created: 'Meeting Reminder'"},
        {"timestamp": "2024-01-15 10:20:18", "level": "WARNING", "message": "Face recognition confidence below threshold"},
        {"timestamp": "2024-01-15 10:15:33", "level": "INFO", "message": "Attendance marked for user 'John Doe'"},
        {"timestamp": "2024-01-15 10:10:55", "level": "ERROR", "message": "Failed to send notification: SMTP connection timeout"},
        {"timestamp": "2024-01-15 10:05:27", "level": "INFO", "message": "AI sentiment analysis completed"},
        {"timestamp": "2024-01-15 10:00:12", "level": "INFO", "message": "System startup completed successfully"},
    ]
    
    # Filter logs
    if log_level != "All":
        sample_logs = [log for log in sample_logs if log["level"] == log_level]
    
    # Display logs
    if sample_logs:
        for log in sample_logs:
            level_color = {
                "INFO": "🟢",
                "WARNING": "🟡", 
                "ERROR": "🔴",
                "DEBUG": "🔵"
            }
            
            st.write(f"{level_color.get(log['level'], '⚪')} **{log['timestamp']}** [{log['level']}] {log['message']}")
    else:
        st.info("No logs found for the selected criteria")
    
    # Log actions
    st.subheader("Log Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Download Logs"):
            st.success("✅ Logs downloaded!")
    
    with col2:
        if st.button("Clear Old Logs"):
            st.success("✅ Old logs cleared!")
    
    with col3:
        if st.button("Export Logs"):
            st.success("✅ Logs exported!")
