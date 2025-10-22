import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64
from PIL import Image
import time
import json
import os
import qrcode
import hashlib
import uuid

# Import our custom modules
from attendance_system import AttendanceSystem
from notification_engine import NotificationEngine
from ai_features import AIFeatures
from database import DatabaseManager
from config import STREAMLIT_THEME
from admin_auth import AdminAuth, show_admin_login, show_admin_logout, check_admin_auth, require_admin_auth, show_admin_dashboard, show_user_management, show_system_settings, show_system_logs
from user_auth import StudentAuth, show_student_login, show_student_logout, check_student_auth, require_student_auth, show_student_profile, show_student_dashboard, show_student_attendance, show_student_reports
from instructor_auth import InstructorAuth, show_instructor_login, show_instructor_logout, check_instructor_auth, require_instructor_auth, show_instructor_dashboard, show_instructor_profile
from instructor_features import show_instructor_class_management, show_instructor_class_attendance, show_instructor_notifications, show_instructor_reports
from style import GLOBAL_CSS, with_primary_color

# Page configuration
st.set_page_config(
    page_title="Chat Ping (Smart Notification App)",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced mobile-friendly viewport and device detection
st.markdown(
    """
    <script>
    (function(){
      try {
        // Enhanced viewport meta tag for better mobile support
        var existing = document.querySelector('meta[name="viewport"]');
        if (!existing) {
          var m = document.createElement('meta');
          m.name = 'viewport';
          m.content = 'width=device-width, initial-scale=1, maximum-scale=5, minimum-scale=1, user-scalable=yes, viewport-fit=cover';
          document.head.appendChild(m);
        } else {
          // Update existing viewport for better mobile support
          existing.content = 'width=device-width, initial-scale=1, maximum-scale=5, minimum-scale=1, user-scalable=yes, viewport-fit=cover';
        }
        
        // Add mobile-specific CSS classes
        var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        var isAndroid = /Android/.test(navigator.userAgent);
        
        if (isMobile) {
          document.documentElement.classList.add('mobile-device');
        }
        if (isIOS) {
          document.documentElement.classList.add('ios-device');
        }
        if (isAndroid) {
          document.documentElement.classList.add('android-device');
        }
        
        // Fix iOS Safari viewport height issues
        if (isIOS) {
          function setViewportHeight() {
            var vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', vh + 'px');
          }
          setViewportHeight();
          window.addEventListener('resize', setViewportHeight);
          window.addEventListener('orientationchange', function() {
            setTimeout(setViewportHeight, 100);
          });
        }
        
        // Prevent zoom on input focus for iOS
        if (isIOS) {
          var inputs = document.querySelectorAll('input, textarea, select');
          inputs.forEach(function(input) {
            input.addEventListener('focus', function() {
              if (window.innerWidth < 768) {
                document.querySelector('meta[name="viewport"]').content = 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no';
              }
            });
            input.addEventListener('blur', function() {
              document.querySelector('meta[name="viewport"]').content = 'width=device-width, initial-scale=1, maximum-scale=5, minimum-scale=1, user-scalable=yes, viewport-fit=cover';
            });
          });
        }
        
      } catch(e) {
        console.log('Mobile detection error:', e);
      }
    })();
    </script>
    """,
    unsafe_allow_html=True,
)



# Simple notification sound (plays a short beep via Web Audio API)
def play_notification_sound():
    st.markdown(
        """
        <script>
        (function(){
          try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const ctx = new AudioCtx();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, ctx.currentTime);
            gain.gain.setValueAtTime(0.0001, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.15, ctx.currentTime + 0.01);
            gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.20);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.21);
          } catch(e) {}
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )

def show_browser_notification(title, body):
    script = (
        """
        <script>
        (function(){
          try {
            const show = () => new Notification({ title: __TITLE__, body: __BODY__ });
            if (!('Notification' in window)) return;
            if (Notification.permission === 'granted') {
              show();
            } else if (Notification.permission !== 'denied') {
              Notification.requestPermission().then(p => { if (p === 'granted') show(); });
            }
          } catch(e) {}
        })();
        </script>
        """
        .replace("__TITLE__", json.dumps(title))
        .replace("__BODY__", json.dumps(body))
    )
    st.markdown(script, unsafe_allow_html=True)

# QR Code Functions
def generate_qr_code(data, size=200):
    """Generate a QR code image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def generate_attendance_qr(class_code, instructor_username, valid_minutes=30):
    """Generate QR code for class attendance"""
    # Create unique attendance session
    session_id = str(uuid.uuid4())
    timestamp = datetime.now()
    expiry_time = timestamp + timedelta(minutes=valid_minutes)
    
    # Create QR data
    qr_data = {
        "type": "attendance",
        "class_code": class_code,
        "instructor": instructor_username,
        "session_id": session_id,
        "timestamp": timestamp.isoformat(),
        "expiry": expiry_time.isoformat(),
        "valid_minutes": valid_minutes
    }
    
    # Convert to JSON string
    qr_string = json.dumps(qr_data)
    
    # Generate QR code
    qr_img = generate_qr_code(qr_string, size=300)
    
    return qr_img, qr_data, session_id

def validate_qr_code(qr_data):
    """Validate QR code data"""
    try:
        # Check if QR data is valid JSON
        if isinstance(qr_data, str):
            data = json.loads(qr_data)
        else:
            data = qr_data
        
        # Check if it's an attendance QR code
        if data.get("type") != "attendance":
            return False, "Invalid QR code type"
        
        # Check expiry
        expiry_time = datetime.fromisoformat(data["expiry"])
        if datetime.now() > expiry_time:
            return False, "QR code has expired"
        
        return True, data
        
    except Exception as e:
        return False, f"Invalid QR code: {str(e)}"

def mark_attendance_from_qr(student_username, qr_data):
    """Mark attendance for student using QR code data"""
    try:
        class_code = qr_data["class_code"]
        instructor = qr_data["instructor"]
        session_id = qr_data["session_id"]
        
        # Check if student is enrolled in the class
        from instructor_auth import InstructorAuth
        instructor_auth = InstructorAuth()
        
        if class_code not in instructor_auth.classes:
            return False, "Class not found"
        
        if student_username not in instructor_auth.classes[class_code]["enrolled_students"]:
            return False, "You are not enrolled in this class"
        
        # Mark attendance in the system
        attendance_record = {
            "student_username": student_username,
            "class_code": class_code,
            "instructor": instructor,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "method": "qr_code"
        }
        
        # Save to database
        success = st.session_state.db.add_attendance_record(attendance_record)
        
        if success:
            # Send notification to instructor
            notification_title = f"Attendance Marked: {student_username}"
            notification_message = f"""
Student {student_username} has marked attendance via QR code!

Class: {class_code}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Method: QR Code Scan
            """.strip()
            
            st.session_state.notification_engine.create_notification(
                title=notification_title,
                message=notification_message,
                notification_type="attendance",
                priority=2
            )
            
            return True, "Attendance marked successfully!"
        else:
            return False, "Failed to save attendance record"
            
    except Exception as e:
        return False, f"Error marking attendance: {str(e)}"

# Custom CSS
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Initialize session state
if 'attendance_system' not in st.session_state:
    st.session_state.attendance_system = AttendanceSystem()
if 'notification_engine' not in st.session_state:
    st.session_state.notification_engine = NotificationEngine()
if 'ai_features' not in st.session_state:
    st.session_state.ai_features = AIFeatures()
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = AdminAuth()
if 'admin_page' not in st.session_state:
    st.session_state.admin_page = "dashboard"
if 'student_auth' not in st.session_state:
    st.session_state.student_auth = StudentAuth()
if 'student_page' not in st.session_state:
    st.session_state.student_page = "dashboard"
if 'instructor_auth' not in st.session_state:
    st.session_state.instructor_auth = InstructorAuth()
if 'instructor_page' not in st.session_state:
    st.session_state.instructor_page = "dashboard"
if 'qr_functions' not in st.session_state:
    st.session_state.generate_attendance_qr = generate_attendance_qr
    st.session_state.validate_qr_code = validate_qr_code
    st.session_state.mark_attendance_from_qr = mark_attendance_from_qr

def get_quick_meet_room():
    room_file = os.path.join('notifications', 'quick_meet_room.json')
    if os.path.exists(room_file):
        with open(room_file, 'r') as f:
            try:
                data = json.load(f)
                return data.get('room_name'), data.get('created_by'), data.get('timestamp')
            except Exception:
                return None, None, None
    return None, None, None

def set_quick_meet_room(room_name, created_by):
    room_file = os.path.join('notifications', 'quick_meet_room.json')
    data = {
        'room_name': room_name,
        'created_by': created_by,
        'timestamp': datetime.now().isoformat()
    }
    with open(room_file, 'w') as f:
        json.dump(data, f)

def clear_quick_meet_room():
    room_file = os.path.join('notifications', 'quick_meet_room.json')
    if os.path.exists(room_file):
        os.remove(room_file)

def main():
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 class="main-header">🔔 Chat Ping</h1>
            <p>Smart Notification App</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check authentication - admin, student, or instructor
    admin_logged_in = check_admin_auth()
    student_logged_in = check_student_auth()
    instructor_logged_in = check_instructor_auth()
    if not admin_logged_in and not student_logged_in and not instructor_logged_in:
        # Minimal login screen: only login options and forms
        st.subheader("Choose Login Type")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 🛡️ Admin Login")
            if st.button("Admin Login", type="primary", use_container_width=True):
                st.session_state.login_type = "admin"
                st.rerun()
        with col2:
            st.markdown("### 🎓 Student Login")
            if st.button("Student Login", type="primary", use_container_width=True):
                st.session_state.login_type = "student"
                st.rerun()
        with col3:
            st.markdown("### 🎓 Instructor Login")
            if st.button("Instructor Login", type="primary", use_container_width=True):
                st.session_state.login_type = "instructor"
                st.rerun()
        # Show login form based on selected type
        if 'login_type' in st.session_state:
            if st.session_state.login_type == "admin":
                show_admin_login()
            elif st.session_state.login_type == "student":
                show_student_login()
            elif st.session_state.login_type == "instructor":
                show_instructor_login()
        # No extra info, no AI, no meet, no default credentials
        return
    # User is logged in - show appropriate interface
    if admin_logged_in:
        show_admin_interface()
    elif student_logged_in:
        show_student_interface()
    elif instructor_logged_in:
        show_instructor_interface()

def show_admin_interface():
    """Show admin interface"""
    # Admin logout button in sidebar
    show_admin_logout()
    
    # Show user info in sidebar
    user_info = st.session_state.admin_auth.get_user_info(st.session_state.admin_session_id)
    if user_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 Logged in as:** {user_info['username']}")
        st.sidebar.markdown(f"**🔑 Role:** {user_info['role']}")
        st.sidebar.markdown(f"**⚡ Permissions:** {', '.join(user_info['permissions'])}")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Add admin section to navigation
    navigation_options = ["Dashboard", "Attendance Management", "Smart Notifications", "AI Features", "Analytics", "Settings", "🛡️ Admin Panel"]
    page = st.sidebar.selectbox(
        "Choose a page",
        navigation_options
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Attendance Management":
        show_attendance_management()
    elif page == "Smart Notifications":
        show_notifications()
    elif page == "AI Features":
        show_ai_features()
    elif page == "Analytics":
        show_analytics()
    elif page == "Settings":
        show_settings()
    elif page == "🛡️ Admin Panel":
        show_admin_panel()

    # Handle admin deep-links triggered from dashboard action buttons
    if 'admin_page' in st.session_state:
        if st.session_state.admin_page == "admin_panel":
            show_admin_panel()
        elif st.session_state.admin_page == "user_management":
            show_user_management()
        elif st.session_state.admin_page == "system_settings":
            show_system_settings()
        elif st.session_state.admin_page == "system_logs":
            show_system_logs()
        elif st.session_state.admin_page == "dashboard":
            # Optional: ensure dashboard renders when requested
            show_admin_dashboard()

def show_student_interface():
    """Show student interface"""
    # Student logout button in sidebar
    show_student_logout()
    
    # Show student info in sidebar
    student_info = st.session_state.student_auth.get_student_info(st.session_state.student_session_id)
    if student_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 Logged in as:** {student_info['username']}")
        st.sidebar.markdown(f"**🔑 Role:** {student_info['role']}")
        st.sidebar.markdown(f"**🎓 Major:** {student_info['profile']['major']}")
        st.sidebar.markdown(f"**📚 Year:** {student_info['profile']['year']}")
        st.sidebar.markdown(f"**⚡ Permissions:** {', '.join(student_info['permissions'])}")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Student navigation options (limited based on permissions)
    navigation_options = ["Dashboard", "My Profile"]
    
    if st.session_state.student_auth.has_student_permission(st.session_state.student_session_id, "attendance"):
        navigation_options.append("Attendance")
    
    if st.session_state.student_auth.has_student_permission(st.session_state.student_session_id, "read"):
        navigation_options.extend(["Notifications", "Reports"])
    
    # Add AI Features, Class Enrollment, and Quick Meet for students
    navigation_options.extend(["Class Enrollment", "AI Features", "Quick Meet"])
    
    page = st.sidebar.selectbox(
        "Choose a page",
        navigation_options
    )
    
    if page == "Dashboard":
        show_student_dashboard()
    elif page == "My Profile":
        show_student_profile()
    elif page == "Attendance":
        show_student_attendance()
    elif page == "Notifications":
        show_student_notifications()
    elif page == "Reports":
        show_student_reports()
    elif page == "Class Enrollment":
        show_student_class_enrollment()
    elif page == "AI Features":
        show_ai_features()
    elif page == "Quick Meet":
        show_quick_meet()
    
    # Handle student page routing from dashboard buttons
    if 'student_page' in st.session_state:
        if st.session_state.student_page == "attendance":
            show_student_attendance()
        elif st.session_state.student_page == "reports":
            show_student_reports()
        elif st.session_state.student_page == "profile":
            show_student_profile()

def show_instructor_interface():
    """Show instructor interface"""
    # Instructor logout button in sidebar
    show_instructor_logout()
    
    # Show instructor info in sidebar
    instructor_info = st.session_state.instructor_auth.get_instructor_info(st.session_state.instructor_session_id)
    if instructor_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 Logged in as:** {instructor_info['username']}")
        st.sidebar.markdown(f"**🔑 Role:** {instructor_info['role']}")
        st.sidebar.markdown(f"**🏢 Department:** {instructor_info['profile']['department']}")
        st.sidebar.markdown(f"**⚡ Permissions:** {', '.join(instructor_info['permissions'])}")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Instructor navigation options
    navigation_options = ["Dashboard", "My Profile", "Class Management", "Attendance", "Notifications", "Reports", "AI Features", "Quick Meet"]
    
    page = st.sidebar.selectbox(
        "Choose a page",
        navigation_options
    )
    
    if page == "Dashboard":
        show_instructor_dashboard()
    elif page == "My Profile":
        show_instructor_profile()
    elif page == "Class Management":
        show_instructor_class_management()
    elif page == "Attendance":
        show_instructor_class_attendance()
    elif page == "Notifications":
        show_instructor_notifications()
    elif page == "Reports":
        show_instructor_reports()
    elif page == "AI Features":
        show_ai_features()
    elif page == "Quick Meet":
        show_quick_meet()
    
    # Handle instructor page routing from dashboard buttons
    if 'instructor_page' in st.session_state:
        if st.session_state.instructor_page == "class_management":
            show_instructor_class_management()
        elif st.session_state.instructor_page == "attendance":
            show_instructor_class_attendance()
        elif st.session_state.instructor_page == "notifications":
            show_instructor_notifications()
        elif st.session_state.instructor_page == "reports":
            show_instructor_reports()

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    # Get attendance summary
    attendance_summary = st.session_state.attendance_system.get_attendance_summary(7)
    
    # Get notification analytics
    notification_analytics = st.session_state.notification_engine.get_notification_analytics(7)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Today's Attendance",
            value=attendance_summary.get('stats', {}).get('today_attendance', 0),
            delta=f"{attendance_summary.get('registered_people', 0)} registered"
        )
    
    with col2:
        st.metric(
            label="Total Notifications",
            value=notification_analytics.get('total_notifications', 0),
            delta=f"{notification_analytics.get('delivery_rate', 0)}% delivery rate"
        )
    
    with col3:
        st.metric(
            label="Registered People",
            value=attendance_summary.get('registered_people', 0),
            delta="Face recognition ready"
        )
    
    with col4:
        st.metric(
            label="AI Features",
            value="Active",
            delta="Sentiment analysis enabled"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Attendance Trend (Last 7 Days)")
        if attendance_summary.get('today_attendance'):
            # Create a simple attendance chart
            dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
            attendance_data = [attendance_summary.get('stats', {}).get('today_attendance', 0)] * 7
            
            df_attendance = pd.DataFrame({
                'Date': dates,
                'Attendance': attendance_data
            })
            
            fig_attendance = px.line(df_attendance, x='Date', y='Attendance', 
                                   title='Daily Attendance Count')
            st.plotly_chart(fig_attendance, use_container_width=True)
        else:
            st.info("No attendance data available yet. Register people and mark attendance to see trends.")
    
    with col2:
        st.subheader("🔔 Notification Categories")
        if notification_analytics.get('patterns', {}).get('category_distribution'):
            categories = notification_analytics['patterns']['category_distribution']
            
            fig_categories = px.pie(
                values=list(categories.values()),
                names=list(categories.keys()),
                title='Notification Distribution by Category'
            )
            st.plotly_chart(fig_categories, use_container_width=True)
        else:
            st.info("No notification data available yet. Create notifications to see analytics.")
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Recent Attendance:**")
        today_attendance = attendance_summary.get('today_attendance', [])
        if today_attendance:
            for record in today_attendance[:5]:  # Show last 5
                st.write(f"• {record['person_name']} - {record['timestamp']}")
        else:
            st.write("No recent attendance records")
    
    with col2:
        st.write("**Recent Notifications:**")
        recent_notifications = st.session_state.db.get_notifications(limit=5)
        if recent_notifications:
            # Play sound once per rerun when there are any notifications
            play_notification_sound()
            for notification in recent_notifications:
                st.write(f"• {notification['title']} - {notification['created_at']}")
        else:
            st.write("No recent notifications")

def show_attendance_management():
    st.header("👥 Attendance Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Register Person", "Mark Attendance", "View Records", "Camera Capture"])
    
    with tab1:
        st.subheader("Register New Person")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            person_name = st.text_input("Person Name", placeholder="Enter full name")
            uploaded_file = st.file_uploader("Upload Photo", type=['jpg', 'jpeg', 'png'], key="register_person_photo")
            
            if st.button("Register Person", type="primary"):
                if person_name and uploaded_file:
                    # Convert uploaded file to bytes
                    image_bytes = uploaded_file.read()
                    
                    success = st.session_state.attendance_system.register_person(
                        person_name, image_bytes=image_bytes
                    )
                    
                    if success:
                        st.success(f"✅ {person_name} registered successfully!")
                        st.session_state.notification_engine.create_system_notification(
                            "Person Registered", f"{person_name} has been registered for attendance tracking"
                        )
                    else:
                        st.error("❌ Failed to register person. Please check the image and try again.")
                else:
                    st.warning("Please provide both name and photo")
        
        with col2:
            st.info("""
            **Registration Tips:**
            - Use clear, well-lit photos
            - Face should be clearly visible
            - Avoid sunglasses or hats
            - Single person per photo
            """)
    
    with tab2:
        st.subheader("Mark Attendance")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_attendance = st.file_uploader("Upload Photo for Attendance", type=['jpg', 'jpeg', 'png'], key="admin_attendance_photo")
            
            if st.button("Mark Attendance", type="primary"):
                if uploaded_attendance:
                    image_bytes = uploaded_attendance.read()
                    
                    with st.spinner("Processing attendance..."):
                        result = st.session_state.attendance_system.mark_attendance(image_bytes=image_bytes)
                    
                    if result['success']:
                        st.success("✅ Attendance marked successfully!")
                        
                        # Show recognized faces
                        if result['recognized_faces']:
                            st.write("**Recognized People:**")
                            for face in result['recognized_faces']:
                                st.write(f"• {face['name']} (Confidence: {face['confidence']:.2f})")
                        
                        # Show unknown faces
                        if result['unknown_faces']:
                            st.warning(f"⚠️ {len(result['unknown_faces'])} unknown faces detected")
                        
                        # Create notification
                        st.session_state.notification_engine.create_attendance_notification(result)
                        
                    else:
                        st.error("❌ Failed to mark attendance")
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                else:
                    st.warning("Please upload a photo")
        
        with col2:
            st.info("""
            **Attendance Tips:**
            - Ensure good lighting
            - Face should be clearly visible
            - Multiple people can be detected
            - System will recognize registered faces
            """)
    
    with tab3:
        st.subheader("Attendance Records")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            days_filter = st.selectbox("Time Period", [7, 30, 90], index=0)
        with col2:
            person_filter = st.selectbox("Person", ["All"] + st.session_state.attendance_system.known_face_names)
        with col3:
            if st.button("Refresh Data"):
                st.rerun()
        
        # Get attendance data
        attendance_summary = st.session_state.attendance_system.get_attendance_summary(days_filter)
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", attendance_summary.get('stats', {}).get('total_attendance', 0))
        with col2:
            st.metric("Unique People", attendance_summary.get('stats', {}).get('unique_people', 0))
        with col3:
            st.metric("Today's Count", attendance_summary.get('stats', {}).get('today_attendance', 0))
        
        # Display records table
        today_records = attendance_summary.get('today_attendance', [])
        if today_records:
            df = pd.DataFrame(today_records)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No attendance records found for the selected period.")
    
    with tab4:
        st.subheader("Live Camera Capture")
        
        if st.button("Capture from Camera", type="primary"):
            with st.spinner("Capturing from camera..."):
                frame = st.session_state.attendance_system.capture_from_camera()
            
            if frame is not None:
                # Convert frame to image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, caption="Captured Image", use_container_width=True)
                
                # Process the captured image
                if st.button("Process Captured Image"):
                    # Convert frame to bytes
                    _, buffer = cv2.imencode('.jpg', frame)
                    image_bytes = buffer.tobytes()
                    
                    with st.spinner("Processing..."):
                        result = st.session_state.attendance_system.mark_attendance(image_bytes=image_bytes)
                    
                    if result['success']:
                        st.success("✅ Attendance processed!")
                        
                        # Show results
                        if result['recognized_faces']:
                            st.write("**Recognized:**")
                            for face in result['recognized_faces']:
                                st.write(f"• {face['name']} ({face['confidence']:.2f})")
                        
                        # Create notification
                        st.session_state.notification_engine.create_attendance_notification(result)
                    else:
                        st.error("❌ No faces recognized")
            else:
                st.error("❌ Failed to capture from camera")

def show_notifications():
    # Default values
    default_date = datetime.now().date()
    default_time = (datetime.now() + timedelta(hours=1)).time()

    # Separate date and time pickers
    scheduled_date = st.date_input("Select date", value=default_date)
    scheduled_time = st.time_input("Select time", value=default_time)

    # Combine into a single datetime object
    scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
    st.header("🔔 Smart Notifications")
    
    tab1, tab2, tab3 = st.tabs(["Create Notification", "Notification History", "Send Notifications"])
    
    with tab1:
        st.subheader("Create New Notification")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            title = st.text_input("Notification Title", placeholder="Enter notification title")
            message = st.text_area("Message", placeholder="Enter notification message", height=100)
            
            col_type, col_priority = st.columns(2)
            with col_type:
                notification_type = st.selectbox(
                    "Type",
                    ["info", "warning", "error", "success", "attendance", "meeting", "system"]
                )
            with col_priority:
                priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=1)
            
            ai_enhanced = st.checkbox("🤖 AI Enhanced", help="Use AI to improve notification content")
            schedule_notification = st.checkbox("📅 Schedule Notification")
            
            scheduled_time = None
            if schedule_notification:
                scheduled_time = st.write("📅 Scheduled for:", scheduled_datetime)
            
            if st.button("Create Notification", type="primary"):
                if title and message:
                    success = st.session_state.notification_engine.create_notification(
                        title=title,
                        message=message,
                        notification_type=notification_type,
                        priority=priority,
                        scheduled_for=scheduled_time,
                        ai_enhanced=ai_enhanced
                    )
                    
                    if success:
                        st.success("✅ Notification created successfully!")
                        # Play sound and show a browser notification preview
                        play_notification_sound()
                        show_browser_notification(title, message)
                        if ai_enhanced:
                            st.info("🤖 AI has enhanced your notification content")
                    else:
                        st.error("❌ Failed to create notification")
                else:
                    st.warning("Please provide both title and message")
        
        with col2:
            st.info("""
            **Notification Types:**
            - **info**: General information
            - **warning**: Important notices
            - **error**: Error alerts
            - **success**: Success messages
            - **attendance**: Attendance related
            - **meeting**: Meeting reminders
            - **system**: System notifications
            
            **Priority Levels:**
            1. Low
            2. Normal
            3. High
            4. Urgent
            5. Critical
            """)
    
    with tab2:
        st.subheader("Notification History")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "pending", "sent", "failed"])
        with col2:
            type_filter = st.selectbox("Type", ["All", "info", "warning", "error", "success", "attendance", "meeting", "system"])
        with col3:
            limit = st.selectbox("Limit", [10, 25, 50, 100], index=1)
        
        # Get notifications
        notifications = st.session_state.db.get_notifications(limit=limit)
        
        # Filter notifications
        if status_filter != "All":
            notifications = [n for n in notifications if n['status'] == status_filter]
        if type_filter != "All":
            notifications = [n for n in notifications if n['notification_type'] == type_filter]
        
        # Display notifications
        for notification in notifications:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{notification['title']}**")
                    st.write(notification['message'])
                    st.caption(f"Created: {notification['created_at']}")
                
                with col2:
                    priority_color = {
                        1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"
                    }
                    st.write(f"{priority_color.get(notification['priority'], '⚪')} Priority {notification['priority']}")
                    st.write(f"Type: {notification['notification_type']}")
                
                with col3:
                    status_color = {
                        'pending': '🟡',
                        'sent': '✅',
                        'failed': '❌'
                    }
                    st.write(f"{status_color.get(notification['status'], '❓')} {notification['status'].title()}")
                    
                    if notification['status'] == 'pending':
                        if st.button(f"Send", key=f"send_{notification['id']}"):
                            success = st.session_state.notification_engine.send_notification(notification['id'])
                            if success:
                                st.success("Sent!")
                                play_notification_sound()
                                show_browser_notification(notification['title'], notification['message'])
                                st.rerun()
                            else:
                                st.error("Failed to send")
    
    with tab3:
        st.subheader("Send Notifications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Process Notification Queue**")
            if st.button("Process All Pending", type="primary"):
                with st.spinner("Processing notifications..."):
                    sent_count = st.session_state.notification_engine.process_notification_queue()
                st.success(f"✅ Sent {sent_count} notifications!")
                if sent_count:
                    play_notification_sound()
                    show_browser_notification("Notifications Sent", f"Sent {sent_count} notifications")
        
        with col2:
            st.write("**Test Notification System**")
            if st.button("Run System Test", type="secondary"):
                with st.spinner("Testing system..."):
                    test_results = st.session_state.notification_engine.test_notification_system()
                
                st.write("**Test Results:**")
                for test, result in test_results.items():
                    status = "✅" if result else "❌"
                    st.write(f"{status} {test.title()}: {'Pass' if result else 'Fail'}")
                play_notification_sound()
                show_browser_notification("System Test", "Notification system test completed")

def show_ai_features():
    st.header("🤖 AI Features")
    
    tab1, tab2, tab3 = st.tabs(["Sentiment Analysis", "Smart Scheduling", "Content Generation"])
    
    with tab1:
        st.subheader("Sentiment Analysis")
        
        text_input = st.text_area("Enter text for sentiment analysis", height=100)
        
        if st.button("Analyze Sentiment", type="primary"):
            if text_input:
                with st.spinner("Analyzing sentiment..."):
                    result = st.session_state.ai_features.analyze_sentiment(text_input)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    sentiment = result['sentiment']
                    confidence = result['confidence']
                    
                    # Color coding for sentiment
                    if sentiment == 'positive':
                        st.success(f"😊 Positive ({confidence:.2f})")
                    elif sentiment == 'negative':
                        st.error(f"😞 Negative ({confidence:.2f})")
                    else:
                        st.info(f"😐 Neutral ({confidence:.2f})")
                
                with col2:
                    st.write("**Confidence Score:**")
                    st.progress(confidence)
                
                with col3:
                    st.write("**Detailed Scores:**")
                    for label, score in result.get('scores', {}).items():
                        st.write(f"{label}: {score:.3f}")
                
                # Extract keywords
                keywords = st.session_state.ai_features.extract_keywords(text_input)
                if keywords:
                    st.write("**Keywords:**")
                    st.write(", ".join(keywords))
            else:
                st.warning("Please enter some text to analyze")
    
    with tab2:
        st.subheader("Smart Scheduling")
        
        col1, col2 = st.columns(2)
        
        with col1:
            notification_type = st.selectbox(
                "Notification Type",
                ["attendance", "meeting", "reminder", "alert", "announcement", "system"]
            )
            
            user_preferences = st.text_area(
                "User Preferences (JSON format)",
                value='{"notification_times": "09:00,13:00,17:00"}',
                height=100
            )
            
            if st.button("Suggest Optimal Time", type="primary"):
                try:
                    import json
                    prefs = json.loads(user_preferences) if user_preferences else {}
                    optimal_time = st.session_state.ai_features.suggest_optimal_time(notification_type, prefs)
                    
                    st.success(f"📅 Suggested time: {optimal_time.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Show reasoning
                    st.info(f"""
                    **Reasoning:**
                    - Notification type: {notification_type}
                    - User preferences: {prefs.get('notification_times', 'default')}
                    - Optimal engagement time based on type
                    """)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            st.info("""
            **Smart Scheduling Features:**
            - Analyzes notification type
            - Considers user preferences
            - Optimizes for engagement
            - Avoids off-hours
            - Learns from patterns
            """)
    
    with tab3:
        st.subheader("AI Content Generation")
        
        context = st.text_area("Context for AI notification", height=100)
        notification_type = st.selectbox(
            "Notification Type",
            ["general", "attendance", "meeting", "system"],
            key="ai_gen_type"
        )
        
        if st.button("Generate Smart Notification", type="primary"):
            if context:
                with st.spinner("Generating AI notification..."):
                    result = st.session_state.ai_features.generate_smart_notification(context, notification_type)
                
                st.success("🤖 AI-generated notification:")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Title:**")
                    st.write(result['title'])
                    
                    st.write("**Message:**")
                    st.write(result['message'])
                
                with col2:
                    st.write("**Category:**", result['category'])
                    st.write("**Priority:**", result['priority'])
                    st.write("**Sentiment:**", result['sentiment'])
                    st.write("**Suggested Time:**", result['suggested_time'].strftime('%Y-%m-%d %H:%M'))
                    
                    if result['keywords']:
                        st.write("**Keywords:**")
                        st.write(", ".join(result['keywords']))
                
                # Option to create the notification
                if st.button("Create This Notification"):
                    success = st.session_state.notification_engine.create_notification(
                        title=result['title'],
                        message=result['message'],
                        notification_type=result['category'],
                        priority=result['priority'],
                        scheduled_for=result['suggested_time'],
                        ai_enhanced=True
                    )
                    
                    if success:
                        st.success("✅ AI notification created!")
                    else:
                        st.error("❌ Failed to create notification")
            else:
                st.warning("Please provide context for AI generation")

def show_analytics():
    st.header("📊 Analytics & Insights")
    
    tab1, tab2, tab3 = st.tabs(["Attendance Analytics", "Notification Analytics", "AI Insights"])
    
    with tab1:
        st.subheader("Attendance Analytics")
        
        # Get attendance data
        days = st.selectbox("Time Period", [7, 30, 90], key="attendance_days")
        attendance_summary = st.session_state.attendance_system.get_attendance_summary(days)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        stats = attendance_summary.get('stats', {})
        
        with col1:
            st.metric("Total Records", stats.get('total_attendance', 0))
        with col2:
            st.metric("Unique People", stats.get('unique_people', 0))
        with col3:
            st.metric("Today's Count", stats.get('today_attendance', 0))
        with col4:
            st.metric("Registered People", attendance_summary.get('registered_people', 0))
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Attendance Trend**")
            # Create sample trend data
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            attendance_data = np.random.randint(5, 20, days)  # Sample data
            
            df_trend = pd.DataFrame({
                'Date': dates,
                'Attendance': attendance_data
            })
            
            fig_trend = px.line(df_trend, x='Date', y='Attendance', title='Daily Attendance Trend')
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            st.write("**People Distribution**")
            people_list = attendance_summary.get('people_list', [])
            if people_list:
                # Create sample attendance count for each person
                people_data = {person: np.random.randint(1, days) for person in people_list}
                
                fig_people = px.bar(
                    x=list(people_data.keys()),
                    y=list(people_data.values()),
                    title='Attendance by Person'
                )
                st.plotly_chart(fig_people, use_container_width=True)
            else:
                st.info("No registered people found")
    
    with tab2:
        st.subheader("Notification Analytics")
        
        days = st.selectbox("Time Period", [7, 30, 90], key="notification_days")
        analytics = st.session_state.notification_engine.get_notification_analytics(days)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Notifications", analytics.get('total_notifications', 0))
        with col2:
            st.metric("Sent Notifications", analytics.get('sent_notifications', 0))
        with col3:
            st.metric("Delivery Rate", f"{analytics.get('delivery_rate', 0)}%")
        with col4:
            patterns = analytics.get('patterns', {})
            st.metric("Peak Hour", patterns.get('peak_hour', 'N/A'))
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Category Distribution**")
            category_dist = patterns.get('category_distribution', {})
            if category_dist:
                fig_categories = px.pie(
                    values=list(category_dist.values()),
                    names=list(category_dist.keys()),
                    title='Notifications by Category'
                )
                st.plotly_chart(fig_categories, use_container_width=True)
            else:
                st.info("No category data available")
        
        with col2:
            st.write("**Priority Distribution**")
            priority_dist = analytics.get('priority_distribution', {})
            if priority_dist:
                fig_priority = px.bar(
                    x=list(priority_dist.keys()),
                    y=list(priority_dist.values()),
                    title='Notifications by Priority'
                )
                st.plotly_chart(fig_priority, use_container_width=True)
            else:
                st.info("No priority data available")
    
    with tab3:
        st.subheader("AI Insights")
        
        st.write("**Sentiment Analysis Trends**")
        
        # Get recent notifications for sentiment analysis
        notifications = st.session_state.db.get_notifications(limit=100)
        
        if notifications:
            sentiments = []
            for n in notifications:
                if n.get('sentiment_score') is not None:
                    sentiments.append(n['sentiment_score'])
            
            if sentiments:
                avg_sentiment = np.mean(sentiments)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
                    
                    # Sentiment distribution
                    sentiment_labels = ['Negative', 'Neutral', 'Positive']
                    sentiment_counts = [
                        len([s for s in sentiments if s < 0.4]),
                        len([s for s in sentiments if 0.4 <= s <= 0.6]),
                        len([s for s in sentiments if s > 0.6])
                    ]
                    
                    fig_sentiment = px.pie(
                        values=sentiment_counts,
                        names=sentiment_labels,
                        title='Sentiment Distribution'
                    )
                    st.plotly_chart(fig_sentiment, use_container_width=True)
                
                with col2:
                    st.write("**Sentiment Trend**")
                    # Create sample trend
                    dates = pd.date_range(end=datetime.now(), periods=len(sentiments), freq='H')
                    df_sentiment = pd.DataFrame({
                        'Time': dates,
                        'Sentiment': sentiments
                    })
                    
                    fig_trend = px.line(df_sentiment, x='Time', y='Sentiment', title='Sentiment Over Time')
                    st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No sentiment data available")
        else:
            st.info("No notifications available for analysis")

def show_settings():
    st.header("⚙️ Settings")
    
    # Check if user has admin permissions
    user_info = st.session_state.admin_auth.get_user_info(st.session_state.admin_session_id)
    is_admin = user_info and ("admin" in user_info["permissions"] or "all" in user_info["permissions"])
    
    if is_admin:
        tab1, tab2, tab3, tab4 = st.tabs(["System Settings", "AI Configuration", "Database Management", "Admin Settings"])
    else:
        tab1, tab2, tab3 = st.tabs(["System Settings", "AI Configuration", "Database Management"])
    
    with tab1:
        st.subheader("System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Face Recognition Settings**")
            tolerance = st.slider("Recognition Tolerance", 0.1, 1.0, 0.6, 0.1)
            model = st.selectbox("Recognition Model", ["hog", "cnn"])
            
            if st.button("Update Face Recognition Settings"):
                st.success("Settings updated!")
        
        with col2:
            st.write("**Notification Settings**")
            email_enabled = st.checkbox("Email Notifications", value=True)
            push_enabled = st.checkbox("Push Notifications", value=True)
            webhook_enabled = st.checkbox("Webhook Notifications", value=True)
            
            if st.button("Update Notification Settings"):
                st.success("Settings updated!")
    
    with tab2:
        st.subheader("AI Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Sentiment Analysis**")
            model_name = st.text_input("Model Name", value="sentiment-analysis")
            max_length = st.number_input("Max Text Length", value=512)
            
            if st.button("Update AI Settings"):
                st.success("AI settings updated!")
        
        with col2:
            st.write("**Smart Scheduling**")
            default_schedule = st.text_input("Default Schedule", value="09:00,13:00,17:00")
            enable_learning = st.checkbox("Enable Learning Mode", value=True)
            
            if st.button("Update Scheduling Settings"):
                st.success("Scheduling settings updated!")
    
    with tab3:
        st.subheader("Database Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Database Operations**")
            
            # Check admin permissions for sensitive operations
            user_info = st.session_state.admin_auth.get_user_info(st.session_state.admin_session_id)
            can_backup = user_info and ("admin" in user_info["permissions"] or "all" in user_info["permissions"])
            can_clean = user_info and ("write" in user_info["permissions"] or "admin" in user_info["permissions"] or "all" in user_info["permissions"])
            
            if can_backup:
                if st.button("Backup Database", type="primary"):
                    st.success("Database backup created!")
            else:
                st.button("Backup Database", disabled=True, help="Admin permission required")
            
            if can_clean:
                if st.button("Clean Old Records"):
                    cleaned = st.session_state.notification_engine.cleanup_old_notifications(30)
                    st.success(f"Cleaned {cleaned} old records!")
            else:
                st.button("Clean Old Records", disabled=True, help="Write permission required")
        
        with col2:
            st.write("**Database Statistics**")
            
            # Get database stats
            attendance_stats = st.session_state.attendance_system.get_attendance_summary(30)
            notification_stats = st.session_state.notification_engine.get_notification_analytics(30)
            
            st.write(f"**Attendance Records:** {attendance_stats.get('stats', {}).get('total_attendance', 0)}")
            st.write(f"**Notifications:** {notification_stats.get('total_notifications', 0)}")
            st.write(f"**Registered People:** {attendance_stats.get('registered_people', 0)}")
    
    # Add admin settings tab if user is admin
    if is_admin:
        with tab4:
            st.subheader("Admin Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Admin Actions**")
                
                if st.button("🛡️ Open Admin Panel", type="primary"):
                    st.session_state.admin_page = "admin_panel"
                    st.rerun()
                
                if st.button("👥 Manage Users"):
                    st.session_state.admin_page = "user_management"
                    st.rerun()
                
                if st.button("📊 View System Logs"):
                    st.session_state.admin_page = "system_logs"
                    st.rerun()
            
            with col2:
                st.write("**Admin Information**")
                user_info = st.session_state.admin_auth.get_user_info(st.session_state.admin_session_id)
                if user_info:
                    st.write(f"**Username:** {user_info['username']}")
                    st.write(f"**Role:** {user_info['role']}")
                    st.write(f"**Permissions:** {', '.join(user_info['permissions'])}")
                
                # Quick admin stats
                admin_stats = st.session_state.admin_auth.get_admin_stats()
                st.write(f"**Total Admin Users:** {admin_stats['total_users']}")
                st.write(f"**Active Sessions:** {admin_stats['active_sessions']}")

def show_admin_panel():
    """Show admin panel with different admin functions"""
    st.header("🛡️ Admin Panel")
    
    # Admin navigation tabs
    admin_tabs = ["Dashboard", "User Management", "System Settings", "System Logs"]
    selected_tab = st.selectbox("Admin Functions", admin_tabs)
    
    if selected_tab == "Dashboard":
        show_admin_dashboard()
    elif selected_tab == "User Management":
        show_user_management()
    elif selected_tab == "System Settings":
        show_system_settings()
    elif selected_tab == "System Logs":
        show_system_logs()

def show_student_attendance():
    """Show student attendance interface"""
    st.header("📝 My Attendance")
    
    # Ensure valid student session
    session_id = st.session_state.get('student_session_id')
    if not session_id:
        st.error("No student session found. Please login again.")
        show_student_login()
        return
    is_valid, _ = st.session_state.student_auth.verify_student_session(session_id)
    if not is_valid:
        st.error("Student session expired. Please login again.")
        show_student_login()
        return
    
    student_info = st.session_state.student_auth.get_student_info(session_id)
    if not student_info:
        st.error("Unable to load student information")
        show_student_login()
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Mark Attendance")
        
        # QR Code Scanner Interface
        st.info("📱 Scan the QR code displayed by your instructor to mark attendance")
        
        # QR Code input field
        qr_code_data = st.text_area(
            "QR Code Data", 
            placeholder="Paste the QR code data here or scan with your camera",
            height=100,
            help="You can scan the QR code with your phone's camera app and copy the text, or use a QR scanner app"
        )
        
        if st.button("Mark Attendance", type="primary", key="mark_attendance_qr"):
            if qr_code_data.strip():
                # Validate QR code
                is_valid, qr_data = st.session_state.validate_qr_code(qr_code_data.strip())
                
                if is_valid:
                    # Mark attendance
                    success, message = st.session_state.mark_attendance_from_qr(student_info['username'], qr_data)
                    
                    if success:
                        st.success(f"✅ {message}")
                        
                        # Show class information
                        st.info(f"""
                        **Attendance Details:**
                        - Class: {qr_data['class_code']}
                        - Instructor: {qr_data['instructor']}
                        - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        - Method: QR Code Scan
                        """)
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error(f"❌ {qr_data}")
            else:
                st.warning("Please enter QR code data")
        
        # Alternative: Camera upload for QR code scanning
        st.markdown("---")
        st.write("**Alternative: Upload QR Code Image**")
        uploaded_qr = st.file_uploader("Upload QR Code Image", type=['jpg', 'jpeg', 'png'], key="qr_code_image")
        
        if uploaded_qr:
            st.image(uploaded_qr, caption="Uploaded QR Code", width=200)
            st.info("📱 Please scan this QR code with your phone's camera app to get the text data, then paste it above.")
        
        # Mobile QR Scanner Instructions
        st.markdown("---")
        st.markdown("""
        <div style="background:#e3f2fd;padding:15px;border-radius:8px;border:1px solid #2196f3;">
            <h4 style="margin:0 0 10px 0;color:#1976d2;">📱 How to Scan QR Code</h4>
            <ol style="margin:5px 0;padding-left:20px;">
                <li>Open your phone's camera app</li>
                <li>Point the camera at the QR code displayed by your instructor</li>
                <li>Tap the notification that appears</li>
                <li>Copy the text and paste it in the field above</li>
                <li>Click "Mark Attendance"</li>
            </ol>
            <p style="margin:5px 0;"><strong>Note:</strong> QR codes expire after 30 minutes for security.</p>
        </div>
        """, unsafe_allow_html=True)
    
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

def show_student_notifications():
    """Show student notifications interface"""
    st.header("🔔 My Notifications")
    
    # Ensure valid student session
    session_id = st.session_state.get('student_session_id')
    if not session_id:
        st.error("No student session found. Please login again.")
        show_student_login()
        return
    is_valid, _ = st.session_state.student_auth.verify_student_session(session_id)
    if not is_valid:
        st.error("Student session expired. Please login again.")
        show_student_login()
        return
    
    student_info = st.session_state.student_auth.get_student_info(session_id)
    if not student_info:
        st.error("Unable to load student information")
        show_student_login()
        return
    
    # Get notifications (targeted to this student or general notifications)
    all_notifications = st.session_state.db.get_notifications(limit=50)
    student_username = student_info['username']
    
    # Filter notifications for this student
    notifications = []
    for notification in all_notifications:
        # Include if targeted to this student or if it's a general notification
        if (notification.get('target_student') == student_username or 
            notification.get('target_student') is None):
            notifications.append(notification)
    
    if notifications:
        st.subheader("Recent Notifications")
        
        for notification in notifications:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{notification['title']}**")
                    st.write(notification['message'])
                    st.caption(f"Created: {notification['created_at']}")
                
                with col2:
                    priority_color = {
                        1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🚨"
                    }
                    st.write(f"{priority_color.get(notification['priority'], '⚪')} Priority {notification['priority']}")
                    st.write(f"Type: {notification['notification_type']}")
    else:
        st.info("No notifications available")

def show_student_reports():
    """Show student reports interface"""
    st.header("📊 My Reports")
    
    # Ensure valid student session
    session_id = st.session_state.get('student_session_id')
    if not session_id:
        st.error("No student session found. Please login again.")
        show_student_login()
        return
    is_valid, _ = st.session_state.student_auth.verify_student_session(session_id)
    if not is_valid:
        st.error("Student session expired. Please login again.")
        show_student_login()
        return
    
    student_info = st.session_state.student_auth.get_student_info(session_id)
    if not student_info:
        st.error("Unable to load student information")
        show_student_login()
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
    st.subheader("Attendance Trend")
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    attendance_data = [5, 7, 6, 8, 9, 7, 8]  # Sample data
    
    df_trend = pd.DataFrame({
        'Date': dates,
        'Attendance': attendance_data
    })
    
    fig_trend = px.line(df_trend, x='Date', y='Attendance', title='My Attendance Trend (Last 7 Days)')
    st.plotly_chart(fig_trend, use_container_width=True)

def show_quick_meet():
    st.header("📹 Quick Meet")
    user_type = None
    if check_instructor_auth():
        user_type = "instructor"
    elif check_student_auth():
        user_type = "student"
    else:
        user_type = "user"

    # Instructor: create a new meeting
    if user_type == "instructor":
        st.info("Start a quick video meeting. Room name is auto-generated for your session.")
        room_name = f"quickmeet-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        st.text_input("Room name", value=room_name, disabled=True)
        meet_url = f"https://meet.jit.si/{room_name}"
        if st.button("Start/Announce Meeting", type="primary"):
            set_quick_meet_room(room_name, "instructor")
            st.success("Meeting announced! Students will see a join prompt.")
            
            # Mobile-friendly meeting links
            st.markdown(f"""
            <div style="text-align: center; margin: 1rem 0;">
                <a href="{meet_url}" target="_blank" style="
                    display: inline-block;
                    background-color: #FF6B6B;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    min-height: 48px;
                    line-height: 24px;
                    box-sizing: border-box;
                ">📱 Open Meeting in New Tab</a>
            </div>
            """, unsafe_allow_html=True)
            
            # Responsive iframe with mobile detection
            st.markdown("""
            <script>
            function adjustIframeHeight() {
                var iframe = document.querySelector('iframe[src*="meet.jit.si"]');
                if (iframe) {
                    var isMobile = window.innerWidth < 768;
                    iframe.style.height = isMobile ? '300px' : '500px';
                }
            }
            adjustIframeHeight();
            window.addEventListener('resize', adjustIframeHeight);
            </script>
            """, unsafe_allow_html=True)
            
            st.components.v1.iframe(meet_url, height=500)
        # Option to clear meeting
        if st.button("End Meeting", type="secondary"):
            clear_quick_meet_room()
            st.info("Meeting ended. Students will no longer see the join prompt.")
    # Student: join if meeting exists
    elif user_type == "student":
        room_name, created_by, timestamp = get_quick_meet_room()
        if room_name:
            st.success(f"Instructor has started a Quick Meet: {room_name}")
            meet_url = f"https://meet.jit.si/{room_name}"
            
            # Mobile-friendly join button
            st.markdown(f"""
            <div style="text-align: center; margin: 1rem 0;">
                <a href="{meet_url}" target="_blank" style="
                    display: inline-block;
                    background-color: #FF6B6B;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 16px;
                    min-height: 48px;
                    line-height: 24px;
                    box-sizing: border-box;
                ">📱 Join Meeting</a>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Show Meeting Preview", type="secondary"):
                # Responsive iframe with mobile detection
                st.markdown("""
                <script>
                function adjustIframeHeight() {
                    var iframe = document.querySelector('iframe[src*="meet.jit.si"]');
                    if (iframe) {
                        var isMobile = window.innerWidth < 768;
                        iframe.style.height = isMobile ? '300px' : '500px';
                    }
                }
                adjustIframeHeight();
                window.addEventListener('resize', adjustIframeHeight);
                </script>
                """, unsafe_allow_html=True)
                
                st.components.v1.iframe(meet_url, height=500)
            
            # Enhanced mobile instructions
            st.markdown(
                f"""
                <div style='background:#e3f2fd;padding:15px;border-radius:8px;border:1px solid #2196f3;margin-top:15px;'>
                    <h4 style='margin:0 0 10px 0;color:#1976d2;'>📱 Mobile Instructions</h4>
                    <p style='margin:5px 0;'><strong>For iPhone/iPad:</strong> Tap the "Join Meeting" button above for the best experience.</p>
                    <p style='margin:5px 0;'><strong>For Android:</strong> The embedded video should work, but use the button above if you have issues.</p>
                    <p style='margin:5px 0;'><strong>Note:</strong> Some mobile browsers may not support embedded video calls.</p>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.info("No active Quick Meet. Please wait for your instructor to start one.")
    else:
        st.info("Quick Meet is available for instructors and students only.")

def show_student_class_enrollment():
    """Show student class enrollment interface"""
    st.header("📚 Class Enrollment")
    
    # Ensure valid student session
    session_id = st.session_state.get('student_session_id')
    if not session_id:
        st.error("No student session found. Please login again.")
        show_student_login()
        return
    is_valid, _ = st.session_state.student_auth.verify_student_session(session_id)
    if not is_valid:
        st.error("Student session expired. Please login again.")
        show_student_login()
        return
    
    student_info = st.session_state.student_auth.get_student_info(session_id)
    if not student_info:
        st.error("Unable to load student information")
        show_student_login()
        return
    
    student_username = student_info['username']
    
    tab1, tab2 = st.tabs(["Available Classes", "My Enrolled Classes"])
    
    with tab1:
        st.subheader("Available Classes")
        
        # Get all available classes
        available_classes = st.session_state.student_auth.get_available_classes()
        
        if available_classes:
            st.write("Browse and enroll in available classes:")
            
            for class_code, class_data in available_classes.items():
                # Check if student is already enrolled
                is_enrolled = student_username in class_data['enrolled_students']
                
                with st.container():
                    # Mobile-responsive layout
                    st.markdown(f"""
                    <div style="
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        margin-bottom: 15px;
                        border-left: 4px solid {'#28a745' if is_enrolled else '#FF6B6B'};
                    ">
                        <h4 style="margin: 0 0 10px 0; color: #333;">{class_data['class_name']} ({class_code})</h4>
                        <p style="margin: 5px 0; color: #666;"><strong>Instructor:</strong> {class_data['instructor']}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>Schedule:</strong> {class_data['schedule']}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>Room:</strong> {class_data['room']}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>Students:</strong> {len(class_data['enrolled_students'])} enrolled</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mobile-friendly buttons
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if is_enrolled:
                            st.success("✅ You are enrolled")
                        else:
                            st.info("📚 Available for enrollment")
                    
                    with col2:
                        if not is_enrolled:
                            if st.button(f"📝 Enroll", key=f"enroll_{class_code}", use_container_width=True):
                                success, message = st.session_state.student_auth.enroll_in_class(student_username, class_code)
                                if success:
                                    st.success(f"✅ {message}")
                                    # Send notification to instructor
                                    notification_title = f"Student Enrolled: {student_username}"
                                    notification_message = f"""
Student {student_username} has enrolled in your class!

Class Details:
• Class Code: {class_code}
• Class Name: {class_data['class_name']}
• Student: {student_username}
• Enrollment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                                    """.strip()
                                    
                                    st.session_state.notification_engine.create_notification(
                                        title=notification_title,
                                        message=notification_message,
                                        notification_type="enrollment",
                                        priority=2
                                    )
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                        else:
                            if st.button(f"❌ Unenroll", key=f"unenroll_{class_code}", use_container_width=True):
                                success, message = st.session_state.student_auth.unenroll_from_class(student_username, class_code)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
        else:
            st.info("No classes are currently available for enrollment.")
    
    with tab2:
        st.subheader("My Enrolled Classes")
        
        # Get student's enrolled classes
        enrolled_classes = st.session_state.student_auth.get_student_classes(student_username)
        
        if enrolled_classes:
            st.write(f"You are enrolled in {len(enrolled_classes)} class(es):")
            
            for class_code in enrolled_classes:
                if class_code in available_classes:
                    class_data = available_classes[class_code]
                    
                    with st.container():
                        # Mobile-responsive enrolled class card
                        st.markdown(f"""
                        <div style="
                            background: #e8f5e8;
                            padding: 15px;
                            border-radius: 8px;
                            margin-bottom: 15px;
                            border-left: 4px solid #28a745;
                        ">
                            <h4 style="margin: 0 0 10px 0; color: #333;">{class_data['class_name']} ({class_code})</h4>
                            <p style="margin: 5px 0; color: #666;"><strong>Instructor:</strong> {class_data['instructor']}</p>
                            <p style="margin: 5px 0; color: #666;"><strong>Schedule:</strong> {class_data['schedule']}</p>
                            <p style="margin: 5px 0; color: #666;"><strong>Room:</strong> {class_data['room']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mobile-friendly unenroll button
                        if st.button(f"❌ Unenroll from {class_code}", key=f"unenroll_my_{class_code}", use_container_width=True):
                            success, message = st.session_state.student_auth.unenroll_from_class(student_username, class_code)
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
        else:
            st.info("You are not enrolled in any classes yet. Browse available classes to enroll!")

if __name__ == "__main__":
    main()

