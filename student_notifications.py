import time
import os
import json
from datetime import datetime
from instructor_auth import InstructorAuth  # Assuming this is where InstructorAuth is defined
from email_service import send_email_notification  # Assuming this is the correct import for the email function

def show_student_notifications():
    """Show student notifications interface"""
    st.header("🔔 My Notifications")

    # Ensure valid student session
    session_id = st.session_state.get("student_session_id")
    if not session_id:
        st.error("No student session found. Please login again.")
        return

    student_info = st.session_state.student_auth.get_student_info(session_id)
    if not student_info:
        st.error("Unable to load student information")
        return

    student_username = student_info["username"]

    # Poll for notifications
    notifications_file = "notifications.json"
    if not os.path.exists(notifications_file):
        st.info("No notifications available")
        return

    # Display notifications dynamically
    st.subheader("Live Notifications")
    last_seen_notification = st.session_state.get("last_seen_notification", None)

    while True:
        with open(notifications_file, "r") as f:
            notifications = json.load(f)

        # Filter notifications for this student
        student_notifications = [
            notif
            for notif in notifications
            if student_username in notif["students"]
            and (last_seen_notification is None or notif["timestamp"] > last_seen_notification)
        ]

        if student_notifications:
            for notif in student_notifications:
                st.toast(
                    f"📢 {notif['title']}: {notif['message']}",
                    icon="🔔",
                    duration=10,
                )
                last_seen_notification = notif["timestamp"]

            st.session_state["last_seen_notification"] = last_seen_notification

        time.sleep(5)  # Poll every 5 seconds

def get_student_email(self, student_username):
    """Retrieve the email address of a student"""
    student_emails = {
        "student1": "student1@example.com",
        "student2": "student2@example.com",
        "student3": "student3@example.com",
        "student4": "student4@example.com",
        "student5": "student5@example.com",
        "student6": "student6@example.com",
    }
    return student_emails.get(student_username, None)

def send_notification_to_students(class_code, title, message):
    """Send a notification to all students in a class and email them"""
    auth = InstructorAuth()
    if class_code not in auth.classes:
        return False, "Class not found"

    class_data = auth.classes[class_code]
    students = class_data["enrolled_students"]

    # Create notification object
    notification = {
        "title": title,
        "message": message,
        "class_code": class_code,
        "timestamp": datetime.now().isoformat(),
        "students": students,
    }

    # Save notification to a shared file
    notifications_file = "notifications.json"
    if os.path.exists(notifications_file):
        with open(notifications_file, "r") as f:
            notifications = json.load(f)
    else:
        notifications = []

    notifications.append(notification)

    with open(notifications_file, "w") as f:
        json.dump(notifications, f, indent=2)

    # Send email notifications to students
    for student in students:
        student_email = auth.get_student_email(student)  # Fetch student email from the database
        if not student_email:
            print(f"Error: No email found for student {student}")
            continue

        email_subject = f"New Notification: {title}"
        email_body = f"""
        Dear {student},

        You have a new notification from your instructor:

        Title: {title}
        Message: {message}
        Class Code: {class_code}

        Best regards,
        Smart Notification App
        """
        success, email_message = send_email_notification(student_email, email_subject, email_body)
        if not success:
            print(f"Failed to send email to {student_email}: {email_message}")

    return True, "Notification sent successfully"

def show_student_profile():
    """Display and manage the student profile"""
    st.header("👤 My Profile")

    # Ensure valid student session
    session_id = st.session_state.get("student_session_id")
    if not session_id:
        st.error("No student session found. Please login again.")
        return

    student_info = st.session_state.student_auth.get_student_info(session_id)
    if not student_info:
        st.error("Unable to load student information")
        return

    # Display student profile details
    st.subheader("Profile Details")
    st.write(f"**Username:** {student_info['username']}")
    st.write(f"**Full Name:** {student_info.get('full_name', 'N/A')}")
    st.write(f"**Email:** {student_info.get('email', 'N/A')}")
    st.write(f"**Phone:** {student_info.get('phone', 'N/A')}")
    st.write(f"**Enrolled Classes:** {', '.join(student_info.get('enrolled_classes', [])) or 'None'}")

    # Allow the student to update their profile
    st.subheader("Update Profile")
    full_name = st.text_input("Full Name", value=student_info.get("full_name", ""))
    email = st.text_input("Email", value=student_info.get("email", ""))
    phone = st.text_input("Phone", value=student_info.get("phone", ""))

    if st.button("Update Profile"):
        # Update the student profile in the database
        student_info["full_name"] = full_name
        student_info["email"] = email
        student_info["phone"] = phone
        st.session_state.student_auth.update_student_info(session_id, student_info)
        st.success("Profile updated successfully!")

def student_dashboard():
    """Main student dashboard"""
    st.sidebar.title("Student Dashboard")
    option = st.sidebar.radio("Navigate", ["Notifications", "Profile"])

    if option == "Notifications":
        show_student_notifications()
    elif option == "Profile":
        show_student_profile()

# Test email sending
success, message = send_email_notification(
    to_email="test_student@example.com",
    subject="Test Notification",
    body="This is a test email from the Smart Notification App."
)
print(success, message)