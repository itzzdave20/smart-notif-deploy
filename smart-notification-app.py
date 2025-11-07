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
try:
    import qrcode
    QR_LIB_AVAILABLE = True
except ImportError:
    QR_LIB_AVAILABLE = False
    qrcode = None
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

# Enhanced mobile-friendly viewport and device detection with PWA support
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
        
        // PWA Support - Register Service Worker with Offline Support
        if ('serviceWorker' in navigator) {
          window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
              .then(function(registration) {
                console.log('ServiceWorker registration successful');
                
                // Set up offline manager
                if (typeof OfflineManager !== 'undefined') {
                  window.offlineManager = new OfflineManager();
                }
              })
              .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
              });
          });
        }
        
        // Offline/Online Status Management
        function updateConnectionStatus() {
          const isOnline = navigator.onLine;
          const statusElement = document.getElementById('connection-status');
          
          if (statusElement) {
            statusElement.textContent = isOnline ? '🟢 Online' : '🔴 Offline';
            statusElement.className = isOnline ? 'online' : 'offline';
          }
          
          // Show/hide offline indicators
          const offlineIndicators = document.querySelectorAll('.offline-indicator');
          offlineIndicators.forEach(indicator => {
            indicator.style.display = isOnline ? 'none' : 'block';
          });
          
          // Show sync button when offline
          const syncButtons = document.querySelectorAll('.sync-button');
          syncButtons.forEach(button => {
            button.style.display = isOnline ? 'none' : 'inline-block';
          });
          
          // Trigger sync when back online
          if (isOnline && window.offlineManager) {
            window.offlineManager.syncOfflineData();
          }
        }
        
        // Listen for online/offline events
        window.addEventListener('online', updateConnectionStatus);
        window.addEventListener('offline', updateConnectionStatus);
        
        // Initial status check
        updateConnectionStatus();
        
        // PWA Install Prompt
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
          e.preventDefault();
          deferredPrompt = e;
          // Show install button or banner
          showInstallButton();
        });
        
        function showInstallButton() {
          // Create install button
          var installBtn = document.createElement('button');
          installBtn.innerHTML = '📱 Install App';
          installBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #FF6B6B;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
            z-index: 1000;
            cursor: pointer;
            transition: all 0.3s ease;
          `;
          
          installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
              deferredPrompt.prompt();
              const { outcome } = await deferredPrompt.userChoice;
              console.log(`User response to the install prompt: ${outcome}`);
              deferredPrompt = null;
              installBtn.remove();
            }
          });
          
          document.body.appendChild(installBtn);
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
    if not QR_LIB_AVAILABLE:
        raise RuntimeError("QR code library not installed. Please install with: pip install qrcode[pil]")
    
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
    if not QR_LIB_AVAILABLE:
        # Provide a graceful fallback object so UI can instruct user/admin
        fallback = {
            "type": "attendance",
            "class_code": class_code,
            "instructor": instructor_username,
            "session_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(minutes=valid_minutes)).isoformat(),
            "valid_minutes": valid_minutes
        }
        return None, fallback, fallback["session_id"]
    
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

# PWA Manifest and Meta Tags with Offline Support
st.markdown("""
<link rel="manifest" href="manifest.json">
<script src="offline-manager.js"></script>
<meta name="theme-color" content="#FF6B6B">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Chat Ping">
<meta name="mobile-web-app-capable" content="yes">
<meta name="msapplication-TileColor" content="#FF6B6B">
<meta name="msapplication-tap-highlight" content="no">
""", unsafe_allow_html=True)

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
    # Connection Status Indicator
    st.markdown("""
    <div id="connection-status" style="
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        z-index: 1000;
        background: #4CAF50;
        color: white;
    ">🟢 Online</div>
    """, unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 class="main-header">🔔 Chat Ping</h1>
            <p>Smart Notification App</p>
            <div class="offline-indicator" style="display: none; background: #ffeb3b; color: #333; padding: 8px; border-radius: 8px; margin: 10px auto; max-width: 300px;">
                📱 Working Offline - Data will sync when online
            </div>
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
            if st.button("Admin Login", key="admin_login_btn"):
                st.session_state.login_type = "admin"
                st.experimental_rerun()
        with col2:
            st.markdown("### 🎓 Student Login")
            if st.button("Student Login", key="student_login_btn"):
                st.session_state.login_type = "student"
                st.experimental_rerun()
        with col3:
            st.markdown("### 🎓 Instructor Login")
            if st.button("Instructor Login", key="instructor_login_btn"):
                st.session_state.login_type = "instructor"
                st.experimental_rerun()
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

    # Offline Sync Button
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.button("🔄 Sync", help="Sync offline data"):
            st.markdown(
                """
                <script>
                if (window.offlineManager) {
                    window.offlineManager.manualSync();
                }
                </script>
                """,
                unsafe_allow_html=True,
            )
    with col2:
        st.markdown(
            """
            <div id="sync-status" style="font-size: 12px; color: #666;">
                <span id="sync-indicator">🟢</span> <span id="sync-text">Online</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Add admin section to navigation
    navigation_options = [
        "Dashboard",
        "Attendance Management",
        "Smart Notifications",
        "AI Features",
        "Analytics",
        "Settings",
        "🛡️ Admin Panel",
    ]
    page = st.sidebar.selectbox("Choose a page", navigation_options)

    if page == "Dashboard":
        show_dashboard()
    elif page == "Attendance Management":
        show_attendance_management()
    elif page == "Smart Notifications":
        show_notifications()
    elif page == "AI Features":
        show_ai_features()
    elif page == "Analytics":
        # Analytics layout: registration, upload attendance, records, live capture
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Register Person", "Mark Attendance (Upload)", "Attendance Records", "Live Camera Capture"]
        )

        # Register Person
        with tab1:
            st.subheader("Register Person")
            col1, col2 = st.columns([2, 1])
            with col1:
                person_name = st.text_input("Person Name", placeholder="Enter full name")
                uploaded_file = st.file_uploader(
                    "Upload Photo", type=["jpg", "jpeg", "png"], key="register_person_photo"
                )

                if st.button("Register Person", key="register_person_btn"):
                    if person_name and uploaded_file:
                        image_bytes = uploaded_file.read()
                        success = st.session_state.attendance_system.register_person(
                            person_name, image_bytes=image_bytes
                        )
                        if success:
                            st.success(f"✅ {person_name} registered successfully!")
                            st.session_state.notification_engine.create_system_notification(
                                "Person Registered",
                                f"{person_name} has been registered for attendance tracking",
                            )
                        else:
                            st.error("❌ Failed to register person. Please check the image and try again.")
                    else:
                        st.warning("Please provide both name and photo")
            with col2:
                st.info(
                    """
                    **Registration Tips:**
                    - Use a clear frontal photo
                    - Name must match official records
                    """
                )

        # Mark Attendance via Upload
        with tab2:
            st.subheader("Mark Attendance (Upload Photo)")
            col1, col2 = st.columns([2, 1])
            with col1:
                uploaded_attendance = st.file_uploader(
                    "Upload Photo for Attendance", type=["jpg", "jpeg", "png"], key="admin_attendance_photo"
                )

                if st.button("Mark Attendance", key="mark_attendance_btn_admin"):
                    if uploaded_attendance:
                        image_bytes = uploaded_attendance.read()
                        with st.spinner("Processing attendance..."):
                            result = st.session_state.attendance_system.mark_attendance(
                                image_bytes=image_bytes
                            )

                        if result and result.get("success"):
                            st.success("✅ Attendance marked successfully!")

                            # Show recognized faces
                            if result.get("recognized_faces"):
                                st.write("**Recognized People:**")
                                for face in result["recognized_faces"]:
                                    st.write(
                                        f"• {face['name']} (Confidence: {face.get('confidence', 0):.2f})"
                                    )

                            # Show unknown faces
                            if result.get("unknown_faces"):
                                st.warning(f"⚠️ {len(result['unknown_faces'])} unknown faces detected")

                            # Create notification
                            st.session_state.notification_engine.create_attendance_notification(result)

                            # Store offline if needed                            # ...existing code...
                                    with col1:
                                        st.markdown("### 🛡️ Admin Login")
                                        if st.button("Admin Login", key="admin_login_btn"):
                                            st.session_state.login_type = "admin"
                            -                st.rerun()
                            +                st.experimental_rerun()
                                    with col2:
                                        st.markdown("### 🎓 Student Login")
                                        if st.button("Student Login", key="student_login_btn"):
                                            st.session_state.login_type = "student"
                            -                st.rerun()
                            +                st.experimental_rerun()
                                    with col3:
                                        st.markdown("### 🎓 Instructor Login")
                                        if st.button("Instructor Login", key="instructor_login_btn"):
                                            st.session_state.login_type = "instructor"
                            -                st.rerun()
                            +                st.experimental_rerun()
                            # ...existing code...
                            
                                    with col3:
                                        if st.button("Refresh Data", key="refresh_attendance_data"):
                            -                st.rerun()
                            +                st.experimental_rerun()
                            # ...existing code...

# Ensure app runs when executed
if __name__ == "__main__":
    main()

