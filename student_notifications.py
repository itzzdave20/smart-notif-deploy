import time

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