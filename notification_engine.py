import smtplib
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import DatabaseManager
from ai_features import AIFeatures
from config import NOTIFICATION_API_KEY, NOTIFICATION_ENABLED

# Optional import: streamlit for secrets access (do not hard-require)
try:
    import streamlit as st  # type: ignore
except Exception:
    st = None

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

class NotificationEngine:
    def __init__(self):
        self.db = DatabaseManager()
        self.ai = AIFeatures()
        self.notification_queue = []
        self.sent_notifications = []
        self.last_email_error = ""
    
    def _get_all_student_usernames(self) -> List[str]:
        """Read all student usernames from students.json."""
        try:
            students_file = "students.json"
            if os.path.exists(students_file):
                with open(students_file, 'r') as f:
                    students = json.load(f)
                    return list(students.keys())
        except Exception as e:
            print(f"Error loading students list: {e}")
        return []

    def broadcast_notification(self, title: str, message: str, notification_type: str = 'info',
                               priority: int = 1, scheduled_for: datetime = None,
                               ai_enhanced: bool = False) -> bool:
        """Broadcast a notification to all students and email them."""
        try:
            usernames = self._get_all_student_usernames()
            if not usernames:
                # If no list available, create a general notification as fallback
                print("No students.json found or empty. Creating general notification only.")
                return self.create_notification(
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    scheduled_for=scheduled_for,
                    ai_enhanced=ai_enhanced
                )
            # Send as targeted notifications so each student has a personal record and email
            return self.create_targeted_notification(
                title=title,
                message=message,
                target_students=usernames,
                notification_type=notification_type,
                priority=priority,
                scheduled_for=scheduled_for,
                ai_enhanced=ai_enhanced
            )
        except Exception as e:
            print(f"Error broadcasting notification: {e}")
            return False
        
    def create_notification(self, title: str, message: str, notification_type: str = 'info', 
                          priority: int = 1, scheduled_for: datetime = None, 
                          ai_enhanced: bool = False) -> bool:
        """Create a new notification"""
        try:
            # AI enhancement if requested
            if ai_enhanced:
                ai_result = self.ai.generate_smart_notification(message, notification_type)
                title = ai_result['title']
                message = ai_result['message']
                priority = ai_result['priority']
                sentiment_score = ai_result['sentiment_confidence']
            else:
                # Basic sentiment analysis
                sentiment_analysis = self.ai.analyze_sentiment(message)
                sentiment_score = sentiment_analysis['confidence']
            
            # Add to database
            success = self.db.add_notification(
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                scheduled_for=scheduled_for,
                sentiment_score=sentiment_score,
                ai_generated=ai_enhanced
            )
            
            if success:
                # Add to queue for immediate sending if no schedule
                if not scheduled_for or scheduled_for <= datetime.now():
                    self.notification_queue.append({
                        'title': title,
                        'message': message,
                        'type': notification_type,
                        'priority': priority,
                        'timestamp': datetime.now()
                    })
                
                return True
            else:
                print("Failed to save notification to database")
                return False
                
        except Exception as e:
            print(f"Error creating notification: {e}")
            return False
    
    def create_targeted_notification(self, title: str, message: str, target_students: list, 
                                   notification_type: str = 'info', priority: int = 1, 
                                   scheduled_for: datetime = None, ai_enhanced: bool = False) -> bool:
        """Create a targeted notification for specific students"""
        try:
            success_count = 0
            
            for student_username in target_students:
                # Create personalized notification for each student
                personalized_title = f"[Personal] {title}"
                personalized_message = f"Hello {student_username},\n\n{message}"
                
                # AI enhancement if requested
                if ai_enhanced:
                    ai_result = self.ai.generate_smart_notification(personalized_message, notification_type)
                    personalized_title = ai_result['title']
                    personalized_message = ai_result['message']
                    priority = ai_result['priority']
                    sentiment_score = ai_result['sentiment_confidence']
                else:
                    # Basic sentiment analysis
                    sentiment_analysis = self.ai.analyze_sentiment(personalized_message)
                    sentiment_score = sentiment_analysis['confidence']
                
                # Create notification dict for email and database
                notification_dict = {
                    'title': personalized_title,
                    'message': personalized_message,
                    'notification_type': notification_type,
                    'priority': priority,
                    'target_student': student_username
                }
                
                # Add to database with student targeting
                success = self.db.add_notification(
                    title=personalized_title,
                    message=personalized_message,
                    notification_type=notification_type,
                    priority=priority,
                    scheduled_for=scheduled_for,
                    sentiment_score=sentiment_score,
                    ai_generated=ai_enhanced,
                    target_student=student_username
                )
                
                if success:
                    success_count += 1
                    
                    # Send email notification immediately if not scheduled
                    if not scheduled_for or scheduled_for <= datetime.now():
                        # Get student email and send
                        student_email = self.get_student_email(student_username)
                        if student_email:
                            self.send_email_notification(notification_dict, student_email)
                        
                        # Add to queue for immediate sending
                        self.notification_queue.append({
                            'title': personalized_title,
                            'message': personalized_message,
                            'type': notification_type,
                            'priority': priority,
                            'timestamp': datetime.now(),
                            'target_student': student_username
                        })
            
            return success_count > 0
                
        except Exception as e:
            print(f"Error creating targeted notification: {e}")
            return False
    
    def send_notification(self, notification_id: int, method: str = 'all') -> bool:
        """Send a specific notification"""
        try:
            # Get notification from database
            notifications = self.db.get_notifications(limit=1000)
            notification = None
            
            for n in notifications:
                if n['id'] == notification_id:
                    notification = n
                    break
            
            if not notification:
                print(f"Notification {notification_id} not found")
                return False
            
            success = False
            
            # Send via different methods
            if method in ['email', 'all']:
                if self.send_email_notification(notification):
                    success = True
            
            if method in ['push', 'all']:
                if self.send_push_notification(notification):
                    success = True
            
            if method in ['webhook', 'all']:
                if self.send_webhook_notification(notification):
                    success = True
            
            # Update status in database
            if success:
                self.db.update_notification_status(notification_id, 'sent')
                self.sent_notifications.append(notification)
            
            return success
            
        except Exception as e:
            print(f"Error sending notification {notification_id}: {e}")
            return False
    
    def get_student_email(self, student_username: str) -> Optional[str]:
        """Get student email from students.json"""
        try:
            students_file = "students.json"
            if os.path.exists(students_file):
                with open(students_file, 'r') as f:
                    students = json.load(f)
                    if student_username in students:
                        return students[student_username].get('email')
            return None
        except Exception as e:
            print(f"Error getting student email: {e}")
            return None
    
    def send_email_notification(self, notification: Dict, student_email: str = None) -> bool:
        """Send notification via email"""
        try:
            # Resolve SMTP configuration (env first, then Streamlit secrets if available)
            smtp_server = os.getenv('SMTP_SERVER') or (st.secrets.get('SMTP_SERVER') if st and hasattr(st, 'secrets') else None) or 'smtp.gmail.com'
            smtp_port = int(os.getenv('SMTP_PORT') or ((st.secrets.get('SMTP_PORT') if st and hasattr(st, 'secrets') else 587)) or 587)
            sender_email = os.getenv('EMAIL_USERNAME') or (st.secrets.get('EMAIL_USERNAME') if st and hasattr(st, 'secrets') else '')
            sender_password = os.getenv('EMAIL_PASSWORD') or (st.secrets.get('EMAIL_PASSWORD') if st and hasattr(st, 'secrets') else '')
            from_name = os.getenv('EMAIL_FROM_NAME') or (st.secrets.get('EMAIL_FROM_NAME') if st and hasattr(st, 'secrets') else 'Smart Notification App')
            reply_to = os.getenv('EMAIL_REPLY_TO') or (st.secrets.get('EMAIL_REPLY_TO') if st and hasattr(st, 'secrets') else None)
            use_ssl = (os.getenv('SMTP_USE_SSL') or (st.secrets.get('SMTP_USE_SSL') if st and hasattr(st, 'secrets') else '')).lower() in ['1', 'true', 'yes']
            timeout_s = int(os.getenv('SMTP_TIMEOUT') or (st.secrets.get('SMTP_TIMEOUT') if st and hasattr(st, 'secrets') else 20) or 20)
            
            # If no email configured, just log it
            if not sender_email or not sender_password:
                self.last_email_error = "SMTP not configured: set EMAIL_USERNAME and EMAIL_PASSWORD (and optionally SMTP_SERVER/SMTP_PORT)."
                print(self.last_email_error)
                return False
            
            # Get target student email if not provided
            target_email = student_email
            if not target_email and notification.get('target_student'):
                target_email = self.get_student_email(notification['target_student'])
            
            if not target_email:
                self.last_email_error = "No email found for notification target"
                print(self.last_email_error)
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = f"{from_name} <{sender_email}>" if from_name else sender_email
            msg["To"] = target_email
            msg["Subject"] = f"🔔 {notification['title']}"
            if reply_to:
                msg.add_header('Reply-To', reply_to)
            
            # Create email body
            email_body = f"""
Dear Student,

You have received a new notification:

{notification['message']}

Notification Details:
- Type: {notification.get('notification_type', 'info')}
- Priority: {notification.get('priority', 1)}
- Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Smart Notification App
            """
            
            msg.attach(MIMEText(email_body, "plain", "utf-8"))
            
            # Send email
            if use_ssl or smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=timeout_s)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [target_email], msg.as_string())
                server.quit()
            else:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=timeout_s)
                server.ehlo()
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [target_email], msg.as_string())
                server.quit()
            
            print(f"✅ Email sent successfully to {target_email}")
            return True
            
        except Exception as e:
            self.last_email_error = f"Error sending email notification: {e}"
            print(f"❌ {self.last_email_error}")
            # Don't fail the entire notification if email fails
            return False
    
    def send_push_notification(self, notification: Dict) -> bool:
        """Send push notification"""
        try:
            # This is a placeholder for push notification service
            # You could integrate with services like Firebase, OneSignal, etc.
            
            push_data = {
                'title': notification['title'],
                'body': notification['message'],
                'priority': notification['priority'],
                'type': notification['notification_type'],
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"PUSH NOTIFICATION SENT:")
            print(json.dumps(push_data, indent=2))
            print("-" * 50)
            
            # Example Firebase implementation:
            # if NOTIFICATION_API_KEY:
            #     url = 'https://fcm.googleapis.com/fcm/send'
            #     headers = {
            #         'Authorization': f'key={NOTIFICATION_API_KEY}',
            #         'Content-Type': 'application/json'
            #     }
            #     response = requests.post(url, headers=headers, json=push_data)
            #     return response.status_code == 200
            
            return True
            
        except Exception as e:
            print(f"Error sending push notification: {e}")
            return False
    
    def send_webhook_notification(self, notification: Dict) -> bool:
        """Send notification via webhook"""
        try:
            webhook_data = {
                'title': notification['title'],
                'message': notification['message'],
                'type': notification['notification_type'],
                'priority': notification['priority'],
                'timestamp': datetime.now().isoformat(),
                'sentiment_score': notification.get('sentiment_score'),
                'ai_generated': notification.get('ai_generated', False)
            }
            
            print(f"WEBHOOK NOTIFICATION SENT:")
            print(json.dumps(webhook_data, indent=2))
            print("-" * 50)
            
            # In a real implementation, you would send to your webhook URL:
            # webhook_url = "https://your-webhook-url.com/notifications"
            # response = requests.post(webhook_url, json=webhook_data)
            # return response.status_code == 200
            
            return True
            
        except Exception as e:
            print(f"Error sending webhook notification: {e}")
            return False
    
    def process_notification_queue(self) -> int:
        """Process all pending notifications in the queue"""
        try:
            sent_count = 0
            
            # Get pending notifications from database
            pending_notifications = self.db.get_notifications(status='pending', limit=100)
            
            for notification in pending_notifications:
                # Check if it's time to send
                if notification['scheduled_for']:
                    scheduled_time = datetime.fromisoformat(notification['scheduled_for'])
                    if scheduled_time > datetime.now():
                        continue  # Not time yet
                
                # Send notification
                if self.send_notification(notification['id']):
                    sent_count += 1
            
            return sent_count
            
        except Exception as e:
            print(f"Error processing notification queue: {e}")
            return 0
    
    def create_attendance_notification(self, attendance_data: Dict) -> bool:
        """Create notification based on attendance data"""
        try:
            if not attendance_data.get('success', False):
                return False
            
            recognized_faces = attendance_data.get('recognized_faces', [])
            unknown_faces = attendance_data.get('unknown_faces', [])
            
            if recognized_faces:
                names = [face['name'] for face in recognized_faces]
                title = "Attendance Recorded"
                message = f"Attendance successfully recorded for: {', '.join(names)}"
                notification_type = 'attendance'
                priority = 2
            else:
                title = "Attendance Alert"
                message = f"No recognized faces found. {len(unknown_faces)} unknown faces detected."
                notification_type = 'alert'
                priority = 3
            
            return self.create_notification(
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                ai_enhanced=True
            )
            
        except Exception as e:
            print(f"Error creating attendance notification: {e}")
            return False
    
    def create_system_notification(self, system_event: str, details: str = "") -> bool:
        """Create system notification"""
        try:
            title = f"System Event: {system_event}"
            message = f"System event occurred: {system_event}. {details}"
            
            return self.create_notification(
                title=title,
                message=message,
                notification_type='system',
                priority=4,
                ai_enhanced=True
            )
            
        except Exception as e:
            print(f"Error creating system notification: {e}")
            return False
    
    def create_meeting_reminder(self, meeting_title: str, meeting_time: datetime, 
                              attendees: List[str] = None) -> bool:
        """Create meeting reminder notification"""
        try:
            title = f"Meeting Reminder: {meeting_title}"
            
            attendees_text = ""
            if attendees:
                attendees_text = f" Attendees: {', '.join(attendees)}"
            
            message = f"Meeting '{meeting_title}' is scheduled for {meeting_time.strftime('%Y-%m-%d %H:%M')}.{attendees_text}"
            
            # Schedule notification for 15 minutes before meeting
            reminder_time = meeting_time - timedelta(minutes=15)
            
            return self.create_notification(
                title=title,
                message=message,
                notification_type='meeting',
                priority=3,
                scheduled_for=reminder_time,
                ai_enhanced=True
            )
            
        except Exception as e:
            print(f"Error creating meeting reminder: {e}")
            return False
    
    def get_notification_analytics(self, days: int = 30) -> Dict:
        """Get notification analytics"""
        try:
            notifications = self.db.get_notifications(limit=1000)
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_notifications = [
                n for n in notifications 
                if datetime.fromisoformat(n['created_at']) >= cutoff_date
            ]
            
            # Analyze patterns
            patterns = self.ai.analyze_notification_patterns(recent_notifications)
            
            # Calculate delivery rates
            sent_count = len([n for n in recent_notifications if n['status'] == 'sent'])
            total_count = len(recent_notifications)
            delivery_rate = (sent_count / total_count * 100) if total_count > 0 else 0
            
            # Priority distribution
            priority_dist = {}
            for n in recent_notifications:
                priority = n['priority']
                priority_dist[priority] = priority_dist.get(priority, 0) + 1
            
            return {
                'total_notifications': total_count,
                'sent_notifications': sent_count,
                'delivery_rate': round(delivery_rate, 2),
                'patterns': patterns,
                'priority_distribution': priority_dist,
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error getting notification analytics: {e}")
            return {}
    
    def cleanup_old_notifications(self, days: int = 30) -> int:
        """Clean up old notifications"""
        try:
            # This would require adding a cleanup method to DatabaseManager
            # For now, we'll just return 0
            print(f"Cleanup would remove notifications older than {days} days")
            return 0
            
        except Exception as e:
            print(f"Error cleaning up notifications: {e}")
            return 0
    
    def test_notification_system(self) -> Dict:
        """Test the notification system"""
        try:
            test_results = {
                'email': False,
                'push': False,
                'webhook': False,
                'ai_features': False,
                'database': False
            }
            
            # Test AI features
            try:
                test_sentiment = self.ai.analyze_sentiment("This is a test message")
                test_results['ai_features'] = 'sentiment' in test_sentiment
            except:
                pass
            
            # Test database
            try:
                test_notification = self.db.add_notification(
                    "Test Notification",
                    "This is a test notification",
                    "test",
                    1
                )
                test_results['database'] = test_notification
            except:
                pass
            
            # Test notification methods
            test_notification = {
                'title': 'Test Notification',
                'message': 'This is a test notification',
                'notification_type': 'test',
                'priority': 1
            }
            
            test_results['email'] = self.send_email_notification(test_notification)
            test_results['push'] = self.send_push_notification(test_notification)
            test_results['webhook'] = self.send_webhook_notification(test_notification)
            
            return test_results
            
        except Exception as e:
            print(f"Error testing notification system: {e}")
            return {}
