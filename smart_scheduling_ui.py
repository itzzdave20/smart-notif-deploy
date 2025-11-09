import streamlit as st
from datetime import datetime, timedelta
from scheduling import SmartScheduler
import pandas as pd

def show_smart_scheduling(role: str = "student", username: str = None):
    """Show Smart Scheduling interface"""
    st.header("📅 Smart Scheduling")
    st.caption("Schedule meetings, classes, announcements, and reminders")
    
    # Initialize scheduler
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = SmartScheduler()
    
    scheduler = st.session_state.scheduler
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Create Schedule", "My Schedules", "Upcoming"])
    
    with tab1:
        st.subheader("Create New Schedule")
        
        with st.form("create_schedule_form"):
            schedule_type = st.selectbox(
                "Schedule Type",
                ["meeting", "class", "announcement", "reminder"],
                help="Select the type of schedule item"
            )
            
            title = st.text_input("Title", placeholder="Enter schedule title")
            description = st.text_area("Description", placeholder="Enter description (optional)", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                scheduled_date = st.date_input("Date", value=datetime.now().date())
            with col2:
                scheduled_time = st.time_input("Time", value=datetime.now().time())
            
            scheduled_datetime = datetime.combine(scheduled_date, scheduled_time).isoformat()
            
            location = st.text_input("Location", placeholder="Room, URL, or location (optional)")
            
            col3, col4 = st.columns(2)
            with col3:
                reminder_minutes = st.number_input("Reminder (minutes before)", min_value=0, max_value=1440, value=15)
            with col4:
                recurrence = st.selectbox(
                    "Recurrence",
                    [None, "daily", "weekly", "monthly"],
                    format_func=lambda x: "None" if x is None else x.capitalize()
                )
            
            participants_input = st.text_input(
                "Participants (comma-separated usernames)",
                placeholder="user1, user2, user3 (optional)",
                help="Leave empty for personal schedule"
            )
            
            participants = [p.strip() for p in participants_input.split(",") if p.strip()] if participants_input else []
            
            submitted = st.form_submit_button("Create Schedule", type="primary")
            
            if submitted:
                if not title:
                    st.error("Please enter a title")
                else:
                    schedule_item = scheduler.create_schedule(
                        schedule_type=schedule_type,
                        title=title,
                        description=description,
                        scheduled_datetime=scheduled_datetime,
                        created_by=username or "unknown",
                        participants=participants,
                        location=location,
                        reminder_minutes=reminder_minutes,
                        recurrence=recurrence
                    )
                    st.success(f"✅ Schedule '{title}' created successfully!")
                    st.rerun()
    
    with tab2:
        st.subheader("My Schedules")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "meeting", "class", "announcement", "reminder"],
                key="schedule_filter_type"
            )
        with col2:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All", "scheduled", "completed", "cancelled"],
                key="schedule_filter_status"
            )
        
        # Get schedules
        schedules = scheduler.get_schedules(user=username)
        
        # Apply filters
        if filter_type != "All":
            schedules = [s for s in schedules if s['type'] == filter_type]
        if filter_status != "All":
            schedules = [s for s in schedules if s['status'] == filter_status]
        
        if schedules:
            # Display schedules
            for schedule in schedules:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{schedule['title']}**")
                        st.caption(f"Type: {schedule['type'].capitalize()} | Status: {schedule['status'].capitalize()}")
                        if schedule.get('description'):
                            st.write(schedule['description'])
                        
                        scheduled_dt = datetime.fromisoformat(schedule['scheduled_datetime'])
                        st.write(f"📅 {scheduled_dt.strftime('%Y-%m-%d %H:%M')}")
                        
                        if schedule.get('location'):
                            st.write(f"📍 {schedule['location']}")
                        
                        if schedule.get('participants'):
                            st.write(f"👥 Participants: {', '.join(schedule['participants'])}")
                    
                    with col2:
                        if schedule['status'] == 'scheduled':
                            if st.button("✓ Complete", key=f"complete_{schedule['id']}"):
                                scheduler.mark_completed(schedule['id'])
                                st.rerun()
                            if st.button("✗ Cancel", key=f"cancel_{schedule['id']}"):
                                scheduler.cancel_schedule(schedule['id'])
                                st.rerun()
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{schedule['id']}"):
                            scheduler.delete_schedule(schedule['id'])
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No schedules found. Create a new schedule to get started!")
    
    with tab3:
        st.subheader("Upcoming Schedules")
        
        hours_ahead = st.slider("Show schedules within (hours)", min_value=1, max_value=168, value=24)
        
        upcoming = scheduler.get_upcoming_schedules(user=username, hours=hours_ahead)
        
        if upcoming:
            for schedule in upcoming:
                with st.container():
                    scheduled_dt = datetime.fromisoformat(schedule['scheduled_datetime'])
                    time_until = scheduled_dt - datetime.now()
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{schedule['title']}**")
                        st.caption(f"{schedule['type'].capitalize()} - {scheduled_dt.strftime('%Y-%m-%d %H:%M')}")
                        if schedule.get('location'):
                            st.write(f"📍 {schedule['location']}")
                    
                    with col2:
                        if time_until.total_seconds() > 0:
                            hours = int(time_until.total_seconds() // 3600)
                            minutes = int((time_until.total_seconds() % 3600) // 60)
                            st.metric("Time Until", f"{hours}h {minutes}m")
                        else:
                            st.warning("Overdue")
                    
                    st.markdown("---")
        else:
            st.info("No upcoming schedules in the next {} hours.".format(hours_ahead))
        
        # Check for reminders
        reminders = scheduler.check_reminders()
        if reminders and username:
            user_reminders = [r for r in reminders if username in r.get('participants', []) or r['created_by'] == username]
            if user_reminders:
                st.warning(f"🔔 You have {len(user_reminders)} reminder(s)!")
                for reminder in user_reminders:
                    st.info(f"**{reminder['title']}** - {datetime.fromisoformat(reminder['scheduled_datetime']).strftime('%Y-%m-%d %H:%M')}")

