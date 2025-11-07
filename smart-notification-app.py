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
                 st.rerun()
        with col2:
            st.markdown("### 🎓 Student Login")
            if st.button("Student Login", key="student_login_btn"):
                 st.session_state.login_type = "student"
                 st.rerun()
        with col3:
            st.markdown("### 🎓 Instructor Login")
            if st.button("Instructor Login", key="instructor_login_btn"):
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
    
    # Offline Sync Button
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        if st.button("🔄 Sync", help="Sync offline data"):
            st.markdown("""
            <script>
            if (window.offlineManager) {
                window.offlineManager.manualSync();
            }
            </script>
            """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div id="sync-status" style="font-size: 12px; color: #666;">
            <span id="sync-indicator">🟢</span> <span id="sync-text">Online</span>
        </div>
        """, unsafe_allow_html=True)
    
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
                # ...existing code...
                with col1:
                    person_name = st.text_input("Person Name", placeholder="Enter full name")
                    uploaded_file = st.file_uploader("Upload Photo", type=['jpg', 'jpeg', 'png'], key="register_person_photo")
                    
        -            if st.button("Register Person", type="primary"):
        +            if st.button("Register Person", key="register_person_btn"):
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
        # ...existing code...
                with col1:
                    uploaded_attendance = st.file_uploader("Upload Photo for Attendance", type=['jpg', 'jpeg', 'png'], key="admin_attendance_photo")
                    
        -        if st.button("Mark Attendance", type="primary"):
        +        if st.button("Mark Attendance", key="mark_attendance_btn_admin"):
                     if uploaded_attendance:
                         image_bytes = uploaded_attendance.read()
                         
                         with st.spinner("Processing attendance..."):
                             result = st.session_state.attendance_system.mark_attendance(image_bytes=image_bytes)
                
                if result and result.get('success'):
                    st.success("✅ Attendance marked successfully!")

                    # Show recognized faces
                    if result.get('recognized_faces'):
                        st.write("**Recognized People:**")
                        for face in result['recognized_faces']:
                            st.write(f"• {face['name']} (Confidence: {face.get('confidence', 0):.2f})")

                    # Show unknown faces
                    if result.get('unknown_faces'):
                        st.warning(f"⚠️ {len(result['unknown_faces'])} unknown faces detected")

                    # Create notification
                    st.session_state.notification_engine.create_attendance_notification(result)

                    # Store offline if needed
                    st.markdown(
                        """
                        <script>
                        if (!navigator.onLine && window.offlineManager) {
                            const offlineData = {
                                type: 'attendance',
                                data: """ + str(result).replace("'", '"') + """,
                                timestamp: new Date().toISOString()
                            };
                            window.offlineManager.storeOfflineData('attendance', offlineData);
                            console.log('Attendance data stored offline');
                        }
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error("❌ Failed to mark attendance")
                    if result and 'error' in result:
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
        
        if st.button("Capture from Camera", key="capture_from_camera_btn"):
            with st.spinner("Capturing from camera..."):
                frame = st.session_state.attendance_system.capture_from_camera()
            
            if frame is not None:
                # Convert frame to image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, caption="Captured Image", use_container_width=True)
                
                # Process the captured image
                if st.button("Process Captured Image", key="process_captured_image_btn"):
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
            
            if st.button("Create Notification", key="create_notification_btn"):
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
                        
                        # Store offline if needed
                        st.markdown("""
                        <script>
                        if (!navigator.onLine && window.offlineManager) {
                            const offlineData = {
                                type: 'notification',
                                data: {
                                    title: '""" + title + """',
                                    message: '""" + message + """',
                                    notification_type: '""" + notification_type + """',
                                    priority: """ + str(priority) + """,
                                    ai_enhanced: """ + str(ai_enhanced).lower() + """
                                },
                                timestamp: new Date().toISOString()
                            };
                            window.offlineManager.storeOfflineData('notifications', offlineData);
                            console.log('Notification stored offline');
                        }
                        </script>
                        """, unsafe_allow_html=True)
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
            if st.button("Process All Pending", key="process_all_pending_btn"):
                with st.spinner("Processing notifications..."):
                    sent_count = st.session_state.notification_engine.process_notification_queue()
                st.success(f"✅ Sent {sent_count} notifications!")
                if sent_count:
                    play_notification_sound()
                    show_browser_notification("Notifications Sent", f"Sent {sent_count} notifications")
        
        with col2:
            st.write("**Test Notification System**")
            if st.button("Run System Test", key="run_system_test_btn"):
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
    
    tab_chat, tab_sentiment, tab_scheduling, tab_gen = st.tabs(["Chatbot", "Sentiment Analysis", "Smart Scheduling", "Content Generation"])
    
    # --- Chatbot Tab ---
    with tab_chat:
        st.subheader("AI Chatbot — Ask questions, get help with assignments, brainstorm")
        if 'ai_chat_history' not in st.session_state:
            st.session_state.ai_chat_history = []  # list of {"role": "user"|"assistant", "text": "..."}
        chat_history = st.session_state.ai_chat_history
        
        # Display chat history
        for chat in chat_history:
            with st.chat_message(chat["role"]):
                st.markdown(chat["text"])
        
        # User input
        prompt = st.text_input("You:", placeholder="Ask me anything...", key="user_input")
        
        if st.button("Send", key="send_msg"):
            if prompt:
                # Add user message to chat history
                chat_history.append({"role": "user", "text": prompt})
                
                # Generate AI response
                with st.spinner("AI is typing..."):
                    response = st.session_state.ai_features.chat_with_gpt(chat_history)
                
                # Add AI response to chat history
                chat_history.append({"role": "assistant", "text": response})
                
                # Clear input field
                st.session_state.user_input = ""
                
                # Update chat history display
                st.experimental_rerun()
            else:
                st.warning("Please enter a message")
    
    # --- Sentiment Analysis Tab ---
    with tab_sentiment:
        st.subheader("Sentiment Analysis — Analyze text sentiment, get insights")
        
        text_to_analyze = st.text_area("Enter text for sentiment analysis", height=150)
        
        if st.button("Analyze Sentiment", key="analyze_sentiment"):
            if text_to_analyze:
                with st.spinner("Analyzing sentiment..."):
                    result = st.session_state.ai_features.analyze_sentiment(text_to_analyze)
                
                st.write("**Sentiment Analysis Result:**")
                st.write(f"Overall Sentiment: {result['sentiment']}")
                st.write(f"Positive Score: {result['positive']:.2f}")
                st.write(f"Negative Score: {result['negative']:.2f}")
                st.write(f"Neutral Score: {result['neutral']:.2f}")
                
                # Show sentiment distribution chart
                fig = go.Figure(data=[
                    go.Pie(labels=list(result['emotion'].keys()), values=list(result['emotion'].values()), hole=.3)
                ])
                fig.update_layout(title_text="Emotion Distribution", title_x=0.5)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please enter some text for analysis")
        
        st.markdown("""
        **Tip:** You can use sentiment analysis to:
        - Analyze customer feedback
        - Monitor brand sentiment
        - Improve communication tone
        """)
    
    # --- Smart Scheduling Tab ---
    with tab_scheduling:
        st.subheader("Smart Scheduling — Schedule meetings, events, with AI suggestions")
        
        # Meeting details
        title = st.text_input("Meeting Title", placeholder="Enter meeting title")
        description = st.text_area("Description", placeholder="Enter meeting description", height=100)
        
        # Date and time pickers
        date = st.date_input("Date", datetime.now())
        start_time = st.time_input("Start Time", datetime.now().time())
        end_time = st.time_input("End Time", datetime.now().time())
        
        # Attendees
        attendees = st.text_input("Attendees (comma-separated)", placeholder="Enter email addresses")
        
        if st.button("Suggest Optimal Time", key="suggest_time"):
            if title and date and start_time and end_time and attendees:
                with st.spinner("AI is suggesting optimal time..."):
                    # Parse attendees
                    attendee_list = [a.strip() for a in attendees.split(",")]
                    
                    # Call AI scheduling function
                    suggestion = st.session_state.ai_features.schedule_meeting_ai(
                        title, description, date, start_time, end_time, attendee_list
                    )
                
                if suggestion:
                    st.success("✅ Optimal time suggested!")
                    st.write(f"**Suggested Time:** {suggestion['start_time']} - {suggestion['end_time']}")
                    st.write(f"**Duration:** {suggestion['duration']} minutes")
                else:
                    st.warning("AI could not find an optimal time. Please try again.")
            else:
                st.warning("Please fill in all meeting details")
        
        st.markdown("""
        **Tip:** Use smart scheduling to:
        - Find optimal meeting times
        - Avoid scheduling conflicts
        - Save time on back-and-forth emails
        """)
    
    # --- Content Generation Tab ---
    with tab_gen:
        st.subheader("Content Generation — Generate text content, summaries, ideas")
        
        content_type = st.selectbox(
            "Select content type",
            ["Article", "Blog Post", "Summary", "Ideas"]
        )
        
        tone = st.selectbox(
            "Select tone",
            ["Formal", "Informal", "Friendly", "Professional"]
        )
        
        keywords = st.text_input("Keywords (comma-separated)", placeholder="Enter keywords for content")
        
        if st.button("Generate Content", key="generate_content"):
            if content_type and tone and keywords:
                with st.spinner("Generating content..."):
                    # Parse keywords
                    keyword_list = [k.strip() for k in keywords.split(",")]
                    
                    # Call AI content generation function
                    content = st.session_state.ai_features.generate_content_ai(
                        content_type, tone, keyword_list
                    )
                
                if content:
                    st.success("✅ Content generated!")
                    st.write("**Generated Content:**")
                    st.write(content)
                else:
                    st.warning("AI could not generate content. Please try again.")
            else:
                st.warning("Please fill in all fields")
        
        st.markdown("""
        **Tip:** Content generation can be used for:
        - Creating articles or blog posts
        - Summarizing long texts
        - Generating content ideas
        """)

