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
from user_auth import StudentAuth, show_student_login, show_student_logout, check_student_auth, require_student_auth, show_student_profile, show_student_dashboard, show_student_attendance, show_student_reports, show_student_classes
from ai_chatbot_ui import show_ai_chatbot
from smart_scheduling_ui import show_smart_scheduling
from instructor_auth import InstructorAuth, show_instructor_login, show_instructor_logout, check_instructor_auth, require_instructor_auth, show_instructor_dashboard, show_instructor_profile
from instructor_features import show_instructor_class_management, show_instructor_class_attendance, show_instructor_notifications, show_instructor_reports
from style import GLOBAL_CSS, with_primary_color
from meetings import render_meeting, suggest_room_for_user, jitsi_url, sanitize_room_name

SIDEBAR_CUSTOM_CSS = """
<style>
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    color: #0f172a;
    padding: 24px 18px 48px;
    box-shadow: 4px 0 18px rgba(15, 23, 42, 0.25);
}

section[data-testid="stSidebar"] > div:first-child {
    height: 100%;
}

section[data-testid="stSidebar"] .block-container,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: rgba(255, 255, 255, 0.78);
    border-radius: 20px;
    padding: 20px 18px 36px;
    backdrop-filter: blur(6px);
    border: 1px solid rgba(148, 163, 184, 0.35);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #0f172a !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(148, 163, 184, 0.4) !important;
}

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(135deg, #fb7185, #f97316);
    color: #fff;
    font-weight: 600;
    letter-spacing: 0.3px;
    padding: 0.75rem 1rem;
    box-shadow: 0 10px 25px rgba(249, 115, 22, 0.35);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(249, 115, 22, 0.45);
}

section[data-testid="stSidebar"] .stButton > button:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.35);
}

section[data-testid="stSidebar"] [role="radiogroup"] > label {
    background: rgba(148, 163, 184, 0.12);
    border-radius: 14px;
    padding: 10px 14px;
    border: 1px solid transparent;
    margin-bottom: 8px;
    transition: all 0.18s ease;
    color: #0f172a !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] > label:hover {
    border-color: rgba(100, 116, 139, 0.45);
    background: rgba(148, 163, 184, 0.24);
}

section[data-testid="stSidebar"] [role="radiogroup"] > label[data-checked="true"] {
    border-color: rgba(249, 115, 22, 0.75);
    background: rgba(249, 115, 22, 0.2);
    box-shadow: 0 10px 22px rgba(249, 115, 22, 0.25);
    color: #0f172a !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] [role="radio"] {
    color: inherit !important;
}

section[data-testid="stSidebar"] .stMetric {
    background: rgba(226, 232, 240, 0.45);
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.25);
}

section[data-testid="stSidebar"] .stMarkdown a {
    color: #b91c1c !important;
    text-decoration: none;
    font-weight: 600;
}

section[data-testid="stSidebar"] .stMarkdown a:hover {
    color: #7f1d1d !important;
    text-decoration: underline;
}

section[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 10px;
}

section[data-testid="stSidebar"]::-webkit-scrollbar-track {
    background: transparent;
}

section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background-color: rgba(148, 163, 184, 0.45);
    border-radius: 12px;
}

@media (max-width: 992px) {
    section[data-testid="stSidebar"] {
        padding: 18px 16px 32px;
    }

    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding: 16px 14px 28px;
    }
}
</style>
"""

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
st.markdown(SIDEBAR_CUSTOM_CSS, unsafe_allow_html=True)

# Initialize session state
if 'attendance_system' not in st.session_state:
    st.session_state.attendance_system = AttendanceSystem()
if 'notification_engine' not in st.session_state:
    st.session_state.notification_engine = NotificationEngine()
if 'ai_features' not in st.session_state or not hasattr(st.session_state.ai_features, 'chat_with_ai'):
    st.session_state.ai_features = AIFeatures()
if 'db' not in st.session_state or not hasattr(st.session_state.db, 'get_attendance_records'):
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

def streamlit_rerun():
    rerun_fn = getattr(st, "experimental_rerun", None) or getattr(st, "rerun", None)
    if rerun_fn is None:
        raise RuntimeError("Streamlit rerun function not available in this version.")
    rerun_fn()

def show_dashboard():
    """Admin dashboard wrapper"""
    show_admin_dashboard()

def show_attendance_management():
    """Admin attendance management view"""
    st.header("📋 Attendance Management")

    summary = st.session_state.attendance_system.get_attendance_summary(30)
    if not summary:
        st.info("No attendance data available yet. Once records are created, you'll see insights here.")
        return

    stats = summary.get("stats", {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", stats.get("total_attendance", 0))
    with col2:
        st.metric("Unique People", stats.get("unique_people", 0))
    with col3:
        st.metric("Today's Attendance", stats.get("today_attendance", 0))
    with col4:
        st.metric("Tracking Period (days)", stats.get("period_days", 30))

    st.markdown("---")

    today_records = summary.get("today_attendance", [])
    if today_records:
        st.subheader("Today's Attendance Entries")
        df_today = pd.DataFrame(today_records)
        st.dataframe(df_today, use_container_width=True, hide_index=True)
    else:
        st.info("No attendance recorded today yet.")

    st.subheader("Registered People")
    registered = summary.get("people_list", [])
    if registered:
        st.write(", ".join(sorted(registered)))
    else:
        st.write("No registered faces yet. Use the Analytics tab to register people.")

    if st.button("🔄 Refresh Attendance Data", key="refresh_admin_attendance"):
        streamlit_rerun()

def show_notifications():
    """Admin notification management view"""
    st.header("🔔 Smart Notifications")

    engine = st.session_state.notification_engine
    db = st.session_state.db

    with st.form("create_notification_form"):
        st.subheader("Create Notification")
        title = st.text_input("Title", placeholder="Enter notification title")
        message = st.text_area("Message", placeholder="Enter notification message", height=150)
        notification_type = st.selectbox(
            "Type",
            ["info", "attendance", "meeting", "reminder", "alert", "system", "announcement"],
            index=0
        )
        priority = st.slider("Priority", min_value=1, max_value=5, value=3)
        target_students_raw = st.text_input(
            "Target Students (optional)",
            help="Provide comma-separated student usernames to send personal notifications"
        )
        ai_enhanced = st.checkbox("Enhance with AI", value=False)
        submitted = st.form_submit_button("Create Notification", type="primary")

        if submitted:
            if not title.strip() or not message.strip():
                st.warning("Please provide both a title and a message.")
            else:
                targets = [s.strip() for s in target_students_raw.split(",") if s.strip()]
                if targets:
                    success = engine.create_targeted_notification(
                        title=title.strip(),
                        message=message.strip(),
                        target_students=targets,
                        notification_type=notification_type,
                        priority=priority,
                        ai_enhanced=ai_enhanced
                    )
                else:
                    success = engine.create_notification(
                        title=title.strip(),
                        message=message.strip(),
                        notification_type=notification_type,
                        priority=priority,
                        ai_enhanced=ai_enhanced
                    )

                if success:
                    st.success("✅ Notification created successfully!")
                    streamlit_rerun()
                else:
                    st.error("❌ Failed to create notification. Please check the logs.")

    st.markdown("---")
    st.subheader("Recent Notifications")

    notifications = db.get_notifications(limit=50)
    if notifications:
        df_notifications = pd.DataFrame(notifications)
        st.dataframe(df_notifications, use_container_width=True)
    else:
        st.info("No notifications found yet.")

def show_ai_features():
    """Admin AI assistance view"""
    st.header("🤖 AI Features")

    ai = st.session_state.ai_features

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sentiment Analysis")
        sentiment_text = st.text_area("Text to analyze", key="ai_sentiment_text")
        if st.button("Analyze Sentiment", key="ai_sentiment_btn", type="primary"):
            if sentiment_text.strip():
                result = ai.analyze_sentiment(sentiment_text.strip())
                st.write("**Sentiment:**", result.get("sentiment", "unknown").title())
                st.write("**Confidence:**", f"{result.get('confidence', 0)*100:.1f}%")
                if result.get("scores"):
                    st.json(result["scores"])
            else:
                st.warning("Please enter text to analyze.")

    with col2:
        st.subheader("Generate Smart Notification")
        context = st.text_area("Context", key="ai_context_text", height=150)
        notif_type = st.selectbox(
            "Notification Type",
            ["general", "attendance", "meeting", "system", "reminder", "alert"],
            key="ai_notification_type"
        )
        if st.button("Generate Notification", key="ai_generate_btn", type="primary"):
            if context.strip():
                suggestion = ai.generate_smart_notification(context.strip(), notification_type=notif_type)
                st.success("AI-generated suggestion ready")
                st.write("**Title:**", suggestion.get("title"))
                st.write("**Message:**", suggestion.get("message"))
                st.write("**Category:**", suggestion.get("category"))
                st.write("**Priority:**", suggestion.get("priority"))
                st.write("**Sentiment:**", suggestion.get("sentiment", "neutral"))
                st.write("**Suggested Time:**", suggestion.get("suggested_time"))
                if suggestion.get("keywords"):
                    st.write("**Keywords:**", ", ".join(suggestion["keywords"]))
            else:
                st.warning("Please enter some context text.")

    st.markdown("---")
    st.subheader("Notification Pattern Insights")
    notifications = st.session_state.db.get_notifications(limit=200)
    if notifications:
        insights = ai.analyze_notification_patterns(notifications)
        if insights:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Notifications", insights.get("total_notifications", 0))
            with col2:
                st.metric("Peak Hour", insights.get("peak_hour", 9))
            with col3:
                st.metric("Common Category", insights.get("most_common_category", "general"))
            with col4:
                st.metric("Avg Sentiment", f"{insights.get('average_sentiment', 0.0):.2f}")
        else:
            st.info("Not enough data for pattern analysis yet.")
    else:
        st.info("Create some notifications to unlock AI insights.")

def show_student_interface():
    """Render the student portal interface"""
    show_student_logout()

    auth = st.session_state.student_auth
    session_id = st.session_state.get('student_session_id')
    if not session_id:
        st.error("No active student session. Please log in again.")
        return

    student_info = auth.get_student_info(session_id)
    if not student_info:
        st.error("Unable to load student information. Please contact support.")
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**👤 Logged in as:** {student_info['username']}")
    st.sidebar.markdown(f"**🎓 Major:** {student_info['profile'].get('major', 'N/A')}")
    st.sidebar.markdown(f"**📧 Email:** {student_info.get('email', 'N/A')}")

    render_quick_meet_sidebar("student", student_info['username'])

    student_pages = {
        "Dashboard": ("dashboard", show_student_dashboard),
        "Classes": ("classes", show_student_classes),
        "AI Chatbot": ("ai_chatbot", lambda: show_ai_chatbot("student")),
        "Attendance": ("attendance", show_student_attendance),
        "Reports": ("reports", show_student_reports),
        "Profile": ("profile", show_student_profile),
    }

    current_page_key = st.session_state.get('student_page', 'dashboard')
    if current_page_key not in {cfg[0] for cfg in student_pages.values()}:
        current_page_key = 'dashboard'
        st.session_state.student_page = current_page_key

    page_labels = list(student_pages.keys())
    label_to_key = {label: cfg[0] for label, cfg in student_pages.items()}

    try:
        default_index = page_labels.index(next(label for label, key in label_to_key.items() if key == current_page_key))
    except StopIteration:
        default_index = 0

    selected_label = st.sidebar.radio("Student Navigation", page_labels, index=default_index)
    st.session_state.student_page = label_to_key[selected_label]

    student_pages[selected_label][1]()

    render_active_quick_meet_embed("student")

def show_instructor_interface():
    """Render the instructor portal interface"""
    show_instructor_logout()

    auth = st.session_state.get('instructor_auth')
    if auth is None:
        auth = InstructorAuth()
        st.session_state.instructor_auth = auth
    else:
        auth.load_instructor_sessions()
        auth.load_instructors()
        auth.load_classes()

    session_id = st.session_state.get('instructor_session_id')
    if not session_id:
        st.error("No active instructor session. Please log in again.")
        return

    instructor_info = auth.get_instructor_info(session_id)
    if not instructor_info:
        st.error("Unable to load instructor information. Please contact support.")
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**👤 Logged in as:** {instructor_info['username']}")
    profile = instructor_info.get('profile', {})
    st.sidebar.markdown(f"**🏫 Department:** {profile.get('department', 'N/A')}")
    st.sidebar.markdown(f"**📧 Email:** {instructor_info.get('email', 'N/A')}")

    render_quick_meet_sidebar("instructor", instructor_info['username'])

    instructor_pages = {
        "Dashboard": ("dashboard", show_instructor_dashboard),
        "Class Management": ("class_management", show_instructor_class_management),
        "AI Chatbot": ("ai_chatbot", lambda: show_ai_chatbot("instructor")),
        "Smart Scheduling": ("scheduling", lambda: show_smart_scheduling("instructor", instructor_info['username'])),
        "Attendance": ("attendance", show_instructor_class_attendance),
        "Notifications": ("notifications", show_instructor_notifications),
        "Reports": ("reports", show_instructor_reports),
        "Profile": ("profile", show_instructor_profile),
    }

    current_page_key = st.session_state.get('instructor_page', 'dashboard')
    if current_page_key not in {cfg[0] for cfg in instructor_pages.values()}:
        current_page_key = 'dashboard'
        st.session_state.instructor_page = current_page_key

    page_labels = list(instructor_pages.keys())
    label_to_key = {label: cfg[0] for label, cfg in instructor_pages.items()}

    try:
        default_index = page_labels.index(next(label for label, key in label_to_key.items() if key == current_page_key))
    except StopIteration:
        default_index = 0

    selected_label = st.sidebar.radio("Instructor Navigation", page_labels, index=default_index)
    st.session_state.instructor_page = label_to_key[selected_label]

    page_function = instructor_pages[selected_label][1]

    if st.session_state.instructor_page == "attendance" and not st.session_state.get('selected_class'):
        st.info("Select a class from Class Management before taking attendance.")
        show_instructor_class_management()
        return

    page_function()

    render_active_quick_meet_embed("instructor")

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

def render_quick_meet_sidebar(role: str, username: str):
    """Render Quick Meet controls in the sidebar for students and instructors."""
    default_room = suggest_room_for_user(username or role)
    active_room, created_by, timestamp = get_quick_meet_room()

    with st.sidebar.expander("📹 Quick Meet", expanded=False):
        room_input = st.text_input(
            "Room name",
            value=default_room,
            key=f"{role}_quick_meet_room_input"
        )
        room_to_use = sanitize_room_name(room_input or default_room)

        # Students can only join, instructors can start and join
        if role == "student":
            # Students: Only Join Room button
            if st.button("Join Room", key=f"{role}_quick_meet_join", use_container_width=True):
                st.session_state['active_quick_meet_room'] = room_to_use
                st.info(f"Joining {room_to_use}")
        else:
            # Instructors/Admins: Both Start and Join buttons
            col_start, col_join = st.columns(2)
            with col_start:
                if st.button("Start Room", key=f"{role}_quick_meet_start"):
                    set_quick_meet_room(room_to_use, username or role)
                    st.session_state['active_quick_meet_room'] = room_to_use
                    st.success(f"Room '{room_to_use}' is ready")
            with col_join:
                if st.button("Join Room", key=f"{role}_quick_meet_join"):
                    st.session_state['active_quick_meet_room'] = room_to_use
                    st.info(f"Joining {room_to_use}")

        if active_room:
            if timestamp:
                try:
                    started_text = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')
                except Exception:
                    started_text = timestamp
            else:
                started_text = 'N/A'

            created_text = (
                f"**Active Room:** `{active_room}`\n\n"
                f"Created by: {created_by or 'Unknown'}\n\n"
                f"Started: {started_text}"
            )
            st.markdown(created_text)

            join_col, clear_col = st.columns(2)
            with join_col:
                if st.button("Join Active", key=f"{role}_quick_meet_join_active"):
                    st.session_state['active_quick_meet_room'] = active_room
            with clear_col:
                if st.button("Clear Active", key=f"{role}_quick_meet_clear"):
                    clear_quick_meet_room()
                    st.session_state.pop('active_quick_meet_room', None)
                    st.warning("Active room cleared")

def render_active_quick_meet_embed(role: str):
    """Render the embedded Quick Meet room if one is active."""
    room = st.session_state.get('active_quick_meet_room')
    if not room:
        return

    st.markdown("---")
    st.subheader("📹 Quick Meet Room")
    st.caption(f"Room: `{room}`")
    render_meeting(room, height=520)
    st.markdown(f"[Open in new tab]({jitsi_url(room)})")

    if st.button("Close Quick Meet", key=f"{role}_quick_meet_close"):
        st.session_state.pop('active_quick_meet_room', None)

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
                streamlit_rerun()
        with col2:
            st.markdown("### 🎓 Student Login")
            if st.button("Student Login", key="student_login_btn"):
                st.session_state.login_type = "student"
                streamlit_rerun()
        with col3:
            st.markdown("### 🎓 Instructor Login")
            if st.button("Instructor Login", key="instructor_login_btn"):
                st.session_state.login_type = "instructor"
                streamlit_rerun()
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
        "AI Chatbot",
        "Smart Scheduling",
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
    elif page == "AI Chatbot":
        show_ai_chatbot("admin")
    elif page == "Smart Scheduling":
        user_info = st.session_state.admin_auth.get_user_info(st.session_state.admin_session_id)
        show_smart_scheduling("admin", user_info['username'] if user_info else "admin")
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

                            # Store offline if needed (handled via frontend OfflineManager)
                            st.session_state["last_attendance_result"] = result
                        else:
                            st.error("❌ Unable to mark attendance. Please try again.")
                    else:
                        st.warning("Please upload a photo before marking attendance.")

# Ensure app runs when executed
if __name__ == "__main__":
    main()

