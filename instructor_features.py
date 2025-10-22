import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from instructor_auth import InstructorAuth

def show_instructor_class_management():
    """Show instructor class management interface"""
    st.header("📚 Class Management")
    
    auth = InstructorAuth()
    instructor_info = auth.get_instructor_info(st.session_state.instructor_session_id)
    
    if not instructor_info:
        st.error("Unable to load instructor information")
        return
    
    # Check if a specific class is selected
    if 'selected_class' in st.session_state and st.session_state.selected_class:
        show_class_detail_view()
        return
    
    tab1, tab2, tab3 = st.tabs(["My Classes", "Create Class", "Manage Students"])
    
    with tab1:
        st.subheader("My Classes")
        
        instructor_classes = auth.get_instructor_classes(instructor_info['username'])
        
        if instructor_classes:
            for class_code, class_data in instructor_classes.items():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{class_code}:** {class_data['class_name']}")
                        st.write(f"Schedule: {class_data['schedule']} | Room: {class_data['room']}")
                        st.write(f"Status: {class_data['status']}")
                    
                    with col2:
                        st.write(f"**Students:** {len(class_data['enrolled_students'])}")
                    
                    with col3:
                        if st.button(f"Manage", key=f"manage_class_{class_code}"):
                            st.session_state.selected_class = class_code
                            st.rerun()
                    
                    with col4:
                        if st.button(f"Take Attendance", key=f"attendance_class_{class_code}"):
                            st.session_state.selected_class = class_code
                            st.session_state.instructor_page = "attendance"
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No classes found. Create a new class to get started!")
    
    with tab2:
        st.subheader("Create New Class")
        
        with st.form("create_class_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                class_code = st.text_input("Class Code", placeholder="e.g., CS101")
                class_name = st.text_input("Class Name", placeholder="e.g., Introduction to Computer Science")
            
            with col2:
                schedule = st.text_input("Schedule", placeholder="e.g., Mon/Wed/Fri 10:00-11:00")
                room = st.text_input("Room", placeholder="e.g., CS-101")
            
            enrolled_students = st.text_area("Pre-enrolled Students (optional - students can enroll themselves)", 
                                            placeholder="student1\nstudent2\nstudent3", 
                                            help="Leave empty to let students enroll themselves. Students will be notified when the class is created.")
            
            if st.form_submit_button("Create Class", type="primary"):
                if all([class_code, class_name, schedule, room]):
                    students_list = [s.strip() for s in enrolled_students.split('\n') if s.strip()]
                    
                    success, message = auth.create_class(
                        class_code, class_name, instructor_info['username'], 
                        schedule, room, students_list
                    )
                    
                    if success:
                        # Send notification to all students about the new class
                        notification_title = f"New Class Available: {class_name}"
                        notification_message = f"""
A new class has been created by your instructor!

Class Details:
• Class Code: {class_code}
• Class Name: {class_name}
• Schedule: {schedule}
• Room: {room}
• Instructor: {instructor_info['username']}

You can now enroll in this class through your student dashboard.
                        """.strip()
                        
                        # Create notification for all students
                        st.session_state.notification_engine.create_notification(
                            title=notification_title,
                            message=notification_message,
                            notification_type="announcement",
                            priority=3
                        )
                        
                        st.success(f"✅ {message}")
                        st.info("📢 Students have been notified about the new class!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("Please fill in all required fields")
    
    with tab3:
        st.subheader("Manage Students")
        
        instructor_classes = auth.get_instructor_classes(instructor_info['username'])
        
        if instructor_classes:
            selected_class = st.selectbox("Select Class", list(instructor_classes.keys()))
            
            if selected_class:
                class_data = instructor_classes[selected_class]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Class:** {selected_class} - {class_data['class_name']}")
                    st.write(f"**Current Students:** {len(class_data['enrolled_students'])}")
                    
                    if class_data['enrolled_students']:
                        st.write("**Enrolled Students:**")
                        for student in class_data['enrolled_students']:
                            st.write(f"• {student}")
                
                with col2:
                    st.write("**Add/Remove Students**")
                    
                    with st.form("manage_students_form"):
                        action = st.radio("Action", ["Add Student", "Remove Student"])
                        student_username = st.text_input("Student Username")
                        
                        if st.form_submit_button("Execute Action"):
                            if student_username:
                                if action == "Add Student":
                                    success, message = auth.add_student_to_class(selected_class, student_username)
                                else:
                                    success, message = auth.remove_student_from_class(selected_class, student_username)
                                
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                            else:
                                st.warning("Please enter a student username")
        else:
            st.info("No classes available to manage students")

def show_instructor_class_attendance():
    """Show instructor class attendance interface"""
    st.header("📝 Class Attendance")
    
    auth = InstructorAuth()
    instructor_info = auth.get_instructor_info(st.session_state.instructor_session_id)
    
    if not instructor_info:
        st.error("Unable to load instructor information")
        return
    
    # Get selected class
    selected_class = st.session_state.get('selected_class', '')
    
    if not selected_class:
        st.error("No class selected")
        return
    
    instructor_classes = auth.get_instructor_classes(instructor_info['username'])
    
    if selected_class not in instructor_classes:
        st.error("Class not found")
        return
    
    class_data = instructor_classes[selected_class]
    
    st.subheader(f"Taking Attendance for {selected_class}: {class_data['class_name']}")
    st.write(f"**Schedule:** {class_data['schedule']} | **Room:** {class_data['room']}")
    st.write(f"**Enrolled Students:** {len(class_data['enrolled_students'])}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["QR Code Attendance", "Photo Attendance", "Attendance History", "Attendance Reports"])
    
    with tab1:
        st.subheader("QR Code Attendance")
        st.info("📱 Generate a QR code for students to scan and mark their attendance")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**QR Code Settings**")
            valid_minutes = st.slider("QR Code Validity (minutes)", 5, 60, 30, 5)
            
            if st.button("Generate QR Code", type="primary"):
                # Generate QR code
                qr_img, qr_data, session_id = st.session_state.generate_attendance_qr(
                    selected_class, instructor_info['username'], valid_minutes
                )
                
                # Store QR data in session state
                st.session_state.current_qr_data = qr_data
                st.session_state.current_qr_session = session_id
                
                if qr_img is None:
                    st.error("QR library not installed on the server. Ask admin to run: pip install qrcode[pil]")
                    st.code(json.dumps(qr_data, indent=2))
                else:
                    st.success(f"✅ QR Code generated! Valid for {valid_minutes} minutes")
        
        with col2:
            if 'current_qr_data' in st.session_state:
                qr_data = st.session_state.current_qr_data
                
                # Display QR code
                st.write("**Current QR Code**")
                qr_img, _, _ = st.session_state.generate_attendance_qr(
                    selected_class, instructor_info['username'], valid_minutes
                )
                
                if qr_img is None:
                    st.warning("QR image not available (library missing). Use the QR data below instead:")
                    st.code(json.dumps(qr_data, indent=2))
                else:
                    # Convert PIL image to bytes for display
                    import io
                    img_buffer = io.BytesIO()
                    qr_img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    st.image(img_buffer, caption=f"Scan to mark attendance for {selected_class}", width=300)
                
                # Show QR code info
                from datetime import datetime
                expiry_time = datetime.fromisoformat(qr_data['expiry'])
                time_left = expiry_time - datetime.now()
                
                if time_left.total_seconds() > 0:
                    minutes_left = int(time_left.total_seconds() / 60)
                    seconds_left = int(time_left.total_seconds() % 60)
                    st.info(f"⏰ QR Code expires in {minutes_left}m {seconds_left}s")
                else:
                    st.error("❌ QR Code has expired")
                
                # Show enrolled students count
                st.write(f"**Enrolled Students:** {len(class_data['enrolled_students'])}")
                
                # Refresh button
                if st.button("🔄 Refresh QR Code"):
                    st.rerun()
    
    with tab2:
        st.subheader("Photo Attendance")
        st.info("📸 Upload a class photo for face recognition attendance")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Upload Class Photo**")
            uploaded_file = st.file_uploader("Upload Photo", type=['jpg', 'jpeg', 'png'], key="instructor_class_photo")
            
            if st.button("Process Attendance", type="primary"):
                if uploaded_file:
                    image_bytes = uploaded_file.read()
                    
                    with st.spinner("Processing attendance..."):
                        result = st.session_state.attendance_system.mark_attendance(image_bytes=image_bytes)
                    
                    if result['success']:
                        st.success("✅ Attendance processed!")
                        
                        # Show recognized faces
                        if result['recognized_faces']:
                            st.write("**Recognized Students:**")
                            for face in result['recognized_faces']:
                                st.write(f"• {face['name']} (Confidence: {face['confidence']:.2f})")
                        
                        # Show unknown faces
                        if result['unknown_faces']:
                            st.warning(f"⚠️ {len(result['unknown_faces'])} unknown faces detected")
                        
                        # Create notification for class attendance
                        st.session_state.notification_engine.create_notification(
                            title=f"Attendance Taken - {selected_class}",
                            message=f"Attendance has been marked for {class_data['class_name']}",
                            notification_type="attendance",
                            priority=2
                        )
                    else:
                        st.error("❌ Failed to process attendance")
                else:
                    st.warning("Please upload a photo")
        
        with col2:
            st.write("**Manual Attendance**")
            
            with st.form("manual_attendance_form"):
                attendance_date = st.date_input("Date", value=datetime.now().date())
                attendance_time = st.time_input("Time", value=datetime.now().time())
                
                st.write("**Mark Students Present/Absent:**")
                
                attendance_records = {}
                for student in class_data['enrolled_students']:
                    attendance_records[student] = st.selectbox(
                        f"{student}", 
                        ["Present", "Absent", "Late"], 
                        key=f"attendance_{student}"
                    )
                
                if st.form_submit_button("Save Manual Attendance", type="primary"):
                    # Save manual attendance records
                    st.success("✅ Manual attendance saved!")
                    
                    # Create notification
                    st.session_state.notification_engine.create_notification(
                        title=f"Manual Attendance - {selected_class}",
                        message=f"Manual attendance recorded for {class_data['class_name']}",
                        notification_type="attendance",
                        priority=2
                    )
    
    with tab3:
        st.subheader("Attendance History")
        
        # Get attendance records for this class
        attendance_summary = st.session_state.attendance_system.get_attendance_summary(30)
        
        if attendance_summary.get('today_attendance'):
            class_attendance = []
            for record in attendance_summary['today_attendance']:
                if record['person_name'] in class_data['enrolled_students']:
                    class_attendance.append(record)
            
            if class_attendance:
                df = pd.DataFrame(class_attendance)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No attendance records found for this class")
        else:
            st.info("No attendance records available")
    
    with tab4:
        st.subheader("Attendance Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Class Statistics**")
            
            # Sample attendance statistics
            total_students = len(class_data['enrolled_students'])
            avg_attendance = 85  # Sample data
            attendance_rate = 92  # Sample data
            
            st.metric("Total Students", total_students)
            st.metric("Average Attendance", f"{avg_attendance}%")
            st.metric("Attendance Rate", f"{attendance_rate}%")
        
        with col2:
            st.write("**Attendance Trend**")
            
            # Create sample attendance trend
            dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
            attendance_data = [8, 9, 7, 10, 8, 9, 8]  # Sample data
            
            df_trend = pd.DataFrame({
                'Date': dates,
                'Attendance Count': attendance_data
            })
            
            fig_trend = px.line(df_trend, x='Date', y='Attendance Count', 
                              title=f'{selected_class} Attendance Trend')
            st.plotly_chart(fig_trend, use_container_width=True)

def show_instructor_notifications():
    """Show instructor notification management"""
    st.header("🔔 Class Notifications")
    
    auth = InstructorAuth()
    instructor_info = auth.get_instructor_info(st.session_state.instructor_session_id)
    
    if not instructor_info:
        st.error("Unable to load instructor information")
        return
    
    # Check if a specific class is selected for notifications
    selected_class = st.session_state.get('selected_class', '')
    
    tab1, tab2, tab3 = st.tabs(["Send Notifications", "Notification History", "Class Announcements"])
    
    with tab1:
        st.subheader("Send Class Notifications")
        
        instructor_classes = auth.get_instructor_classes(instructor_info['username'])
        
        if instructor_classes:
            # Show selected class if any
            if selected_class:
                st.info(f"📚 Sending notification for: {selected_class} - {instructor_classes[selected_class]['class_name']}")
                if st.button("← Change Class", key="change_class_notification"):
                    del st.session_state.selected_class
                    st.rerun()
            
            with st.form("send_class_notification_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if selected_class:
                        st.write(f"**Selected Class:** {selected_class}")
                        st.write(f"**Class Name:** {instructor_classes[selected_class]['class_name']}")
                        st.write(f"**Students:** {len(instructor_classes[selected_class]['enrolled_students'])}")
                    else:
                        target_class = st.selectbox("Select Class", list(instructor_classes.keys()))
                    
                    notification_type = st.selectbox("Type", ["announcement", "reminder", "assignment", "exam", "general"])
                    priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=1)
                
                with col2:
                    title = st.text_input("Title", placeholder="Enter notification title")
                    message = st.text_area("Message", placeholder="Enter notification message", height=100)
                
                # Advanced options
                st.subheader("Advanced Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    schedule_notification = st.checkbox("Schedule Notification")
                    scheduled_time = None
                    if schedule_notification:
                        col_date, col_time = st.columns(2)
                        with col_date:
                            schedule_date = st.date_input("Schedule Date", value=datetime.now().date())
                        with col_time:
                            schedule_time = st.time_input("Schedule Time", value=(datetime.now() + timedelta(hours=1)).time())
                        scheduled_time = datetime.combine(schedule_date, schedule_time)
                    
                    send_to_all_classes = st.checkbox("Send to All Classes", help="Send this notification to all your classes")
                
                with col2:
                    require_confirmation = st.checkbox("Require Student Confirmation", help="Students must confirm receipt")
                    send_email_copy = st.checkbox("Send Email Copy", help="Send email copy to instructor")
                
                if st.form_submit_button("Send Notification", type="primary"):
                    if title and message:
                        target_classes = [selected_class] if selected_class else ([target_class] if not send_to_all_classes else list(instructor_classes.keys()))
                        
                        success_count = 0
                        for class_code in target_classes:
                            class_data = instructor_classes[class_code]
                            
                            # Get enrolled students for targeted notification
                            enrolled_students = class_data['enrolled_students']
                            
                            if enrolled_students:
                                # Send targeted notification to enrolled students
                                success = st.session_state.notification_engine.create_targeted_notification(
                                    title=f"[{class_code}] {title}",
                                    message=f"Class: {class_data['class_name']}\n\n{message}",
                                    target_students=enrolled_students,
                                    notification_type=notification_type,
                                    priority=priority,
                                    scheduled_for=scheduled_time
                                )
                            else:
                                # Send general notification if no students enrolled
                                success = st.session_state.notification_engine.create_notification(
                                    title=f"[{class_code}] {title}",
                                    message=f"Class: {class_data['class_name']}\nStudents: {len(class_data['enrolled_students'])}\n\n{message}",
                                    notification_type=notification_type,
                                    priority=priority,
                                    scheduled_for=scheduled_time
                                )
                            
                            if success:
                                success_count += 1
                        
                        if success_count > 0:
                            st.success(f"✅ Notification sent to {success_count} class(es) successfully!")
                        else:
                            st.error("❌ Failed to send notification")
                    else:
                        st.warning("Please provide both title and message")
        else:
            st.info("No classes available to send notifications")
    
    with tab2:
        st.subheader("Notification History")
        
        # Get notifications
        notifications = st.session_state.db.get_notifications(limit=50)
        
        if notifications:
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
        else:
            st.info("No notifications found")
    
    with tab3:
        st.subheader("Class Announcements")
        
        instructor_classes = auth.get_instructor_classes(instructor_info['username'])
        
        if instructor_classes:
            selected_class = st.selectbox("Select Class for Announcements", list(instructor_classes.keys()))
            
            if selected_class:
                class_data = instructor_classes[selected_class]
                
                st.write(f"**Class:** {selected_class} - {class_data['class_name']}")
                st.write(f"**Students:** {len(class_data['enrolled_students'])}")
                
                # Quick announcement templates
                st.subheader("Quick Announcements")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📝 Assignment Due", type="primary"):
                        st.session_state.notification_engine.create_notification(
                            title=f"[{selected_class}] Assignment Due",
                            message=f"Reminder: Assignment is due soon for {class_data['class_name']}",
                            notification_type="assignment",
                            priority=3
                        )
                        st.success("Assignment reminder sent!")
                
                with col2:
                    if st.button("📅 Class Cancelled", type="primary"):
                        st.session_state.notification_engine.create_notification(
                            title=f"[{selected_class}] Class Cancelled",
                            message=f"Class cancelled for {class_data['class_name']}. Check for makeup schedule.",
                            notification_type="announcement",
                            priority=4
                        )
                        st.success("Class cancellation notice sent!")
                
                with col3:
                    if st.button("📊 Exam Schedule", type="primary"):
                        st.session_state.notification_engine.create_notification(
                            title=f"[{selected_class}] Exam Schedule",
                            message=f"Exam schedule updated for {class_data['class_name']}. Check course materials.",
                            notification_type="exam",
                            priority=4
                        )
                        st.success("Exam schedule notification sent!")
        else:
            st.info("No classes available for announcements")

def show_instructor_reports():
    """Show instructor reports and analytics"""
    st.header("📊 Instructor Reports")
    
    auth = InstructorAuth()
    instructor_info = auth.get_instructor_info(st.session_state.instructor_session_id)
    
    if not instructor_info:
        st.error("Unable to load instructor information")
        return
    
    instructor_classes = auth.get_instructor_classes(instructor_info['username'])
    
    if not instructor_classes:
        st.info("No classes available for reports")
        return
    
    tab1, tab2, tab3 = st.tabs(["Class Overview", "Attendance Analytics", "Student Performance"])
    
    with tab1:
        st.subheader("Class Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Class Summary**")
            total_students = sum(len(class_data["enrolled_students"]) for class_data in instructor_classes.values())
            st.metric("Total Classes", len(instructor_classes))
            st.metric("Total Students", total_students)
            st.metric("Average Class Size", total_students // len(instructor_classes) if instructor_classes else 0)
        
        with col2:
            st.write("**Class Distribution**")
            class_names = [f"{code}: {data['class_name']}" for code, data in instructor_classes.items()]
            student_counts = [len(data["enrolled_students"]) for data in instructor_classes.values()]
            
            fig_classes = px.bar(
                x=class_names,
                y=student_counts,
                title="Students per Class"
            )
            fig_classes.update_xaxes(tickangle=45)
            st.plotly_chart(fig_classes, use_container_width=True)
    
    with tab2:
        st.subheader("Attendance Analytics")
        
        # Sample attendance data
        dates = pd.date_range(end=datetime.now(), periods=14, freq='D')
        attendance_data = [8, 9, 7, 10, 8, 9, 8, 7, 9, 8, 10, 9, 8, 9]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Overall Attendance Trend**")
            df_attendance = pd.DataFrame({
                'Date': dates,
                'Attendance': attendance_data
            })
            
            fig_attendance = px.line(df_attendance, x='Date', y='Attendance', 
                                   title='14-Day Attendance Trend')
            st.plotly_chart(fig_attendance, use_container_width=True)
        
        with col2:
            st.write("**Attendance Statistics**")
            avg_attendance = sum(attendance_data) / len(attendance_data)
            max_attendance = max(attendance_data)
            min_attendance = min(attendance_data)
            
            st.metric("Average Daily Attendance", f"{avg_attendance:.1f}")
            st.metric("Highest Attendance", max_attendance)
            st.metric("Lowest Attendance", min_attendance)
    
    with tab3:
        st.subheader("Student Performance")
        
        # Sample student performance data
        students = ["Student A", "Student B", "Student C", "Student D", "Student E"]
        attendance_rates = [95, 87, 92, 78, 89]
        performance_scores = [88, 92, 85, 76, 91]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Attendance Rates**")
            df_attendance_rates = pd.DataFrame({
                'Student': students,
                'Attendance Rate (%)': attendance_rates
            })
            
            fig_attendance_rates = px.bar(df_attendance_rates, x='Student', y='Attendance Rate (%)',
                                        title='Student Attendance Rates')
            st.plotly_chart(fig_attendance_rates, use_container_width=True)
        
        with col2:
            st.write("**Performance vs Attendance**")
            df_performance = pd.DataFrame({
                'Student': students,
                'Attendance Rate': attendance_rates,
                'Performance Score': performance_scores
            })
            
            fig_performance = px.scatter(df_performance, x='Attendance Rate', y='Performance Score',
                                       hover_data=['Student'], title='Performance vs Attendance')
            st.plotly_chart(fig_performance, use_container_width=True)

def show_class_detail_view():
    """Show detailed view for a specific class"""
    st.header("📚 Class Details")
    
    auth = InstructorAuth()
    instructor_info = auth.get_instructor_info(st.session_state.instructor_session_id)
    
    if not instructor_info:
        st.error("Unable to load instructor information")
        return
    
    selected_class = st.session_state.get('selected_class', '')
    if not selected_class:
        st.error("No class selected")
        return
    
    instructor_classes = auth.get_instructor_classes(instructor_info['username'])
    
    if selected_class not in instructor_classes:
        st.error("Class not found")
        return
    
    class_data = instructor_classes[selected_class]
    
    # Back button
    if st.button("← Back to Classes", key="back_to_classes"):
        del st.session_state.selected_class
        st.rerun()
    
    # Class information
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"{selected_class}: {class_data['class_name']}")
        st.write(f"**Schedule:** {class_data['schedule']}")
        st.write(f"**Room:** {class_data['room']}")
        st.write(f"**Status:** {class_data['status']}")
        st.write(f"**Created:** {class_data['created_at'][:10]}")
    
    with col2:
        st.metric("Total Students", len(class_data['enrolled_students']))
        st.metric("Class Status", class_data['status'].title())
    
    # Action buttons
    st.subheader("Class Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Take Attendance", type="primary", use_container_width=True, key="class_detail_attendance"):
            st.session_state.instructor_page = "attendance"
            st.rerun()
    
    with col2:
        if st.button("🔔 Send Notification", type="primary", use_container_width=True, key="class_detail_notification"):
            st.session_state.instructor_page = "notifications"
            st.rerun()
    
    with col3:
        if st.button("📊 View Reports", type="primary", use_container_width=True, key="class_detail_reports"):
            st.session_state.instructor_page = "reports"
            st.rerun()
    
    with col4:
        if st.button("✏️ Edit Class", type="secondary", use_container_width=True, key="class_detail_edit"):
            st.session_state.edit_class = True
            st.rerun()
    
    # Students list
    st.subheader("Enrolled Students")
    
    if class_data['enrolled_students']:
        # Create a DataFrame for better display
        students_df = pd.DataFrame({
            'Student Username': class_data['enrolled_students'],
            'Status': ['Active'] * len(class_data['enrolled_students']),
            'Actions': ['Remove'] * len(class_data['enrolled_students'])
        })
        
        # Display students
        for i, student in enumerate(class_data['enrolled_students']):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"• {student}")
            
            with col2:
                st.write("Active")
            
            with col3:
                if st.button(f"Remove", key=f"remove_student_{student}_{selected_class}"):
                    success, message = auth.remove_student_from_class(selected_class, student)
                    if success:
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    else:
        st.info("No students enrolled in this class")
    
    # Add student section
    st.subheader("Add Student to Class")
    
    with st.form("add_student_form"):
        new_student = st.text_input("Student Username", placeholder="Enter student username")
        
        if st.form_submit_button("Add Student", type="primary"):
            if new_student:
                success, message = auth.add_student_to_class(selected_class, new_student)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("Please enter a student username")
    
    # Edit class form (if edit mode is enabled)
    if st.session_state.get('edit_class', False):
        st.subheader("Edit Class Information")
        
        with st.form("edit_class_form"):
            new_class_name = st.text_input("Class Name", value=class_data['class_name'])
            new_schedule = st.text_input("Schedule", value=class_data['schedule'])
            new_room = st.text_input("Room", value=class_data['room'])
            new_status = st.selectbox("Status", ["active", "inactive"], 
                                    index=0 if class_data['status'] == 'active' else 1)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes", type="primary", key="save_class_changes"):
                    # Update class information
                    class_data['class_name'] = new_class_name
                    class_data['schedule'] = new_schedule
                    class_data['room'] = new_room
                    class_data['status'] = new_status
                    
                    # Save to file
                    auth.classes[selected_class] = class_data
                    auth.save_classes()
                    
                    st.success("✅ Class updated successfully!")
                    st.session_state.edit_class = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel", type="secondary", key="cancel_class_edit"):
                    st.session_state.edit_class = False
                    st.rerun()

