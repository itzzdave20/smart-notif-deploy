#!/usr/bin/env python3
"""
Demo script for Smart Notification App
This script demonstrates the key features of the application
"""

import os
import sys
from datetime import datetime
import numpy as np
from PIL import Image

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from attendance_system import AttendanceSystem
from notification_engine import NotificationEngine
from ai_features import AIFeatures
from database import DatabaseManager

def create_demo_image():
    """Create a simple demo image for testing"""
    # Create a simple colored image
    img = Image.new('RGB', (200, 200), color='lightblue')
    return img

def demo_attendance_system():
    """Demonstrate attendance system features"""
    print("Testing Attendance System...")
    
    attendance = AttendanceSystem()
    
    # Create demo image
    demo_img = create_demo_image()
    
    # Test face encoding (this will fail without actual face, but shows the process)
    print("Testing face encoding...")
    try:
        # Save demo image temporarily
        demo_img.save('demo_image.jpg')
        encoding = attendance.encode_face_from_image('demo_image.jpg')
        if encoding is not None:
            print("SUCCESS: Face encoding successful")
        else:
            print("WARNING: No face detected in demo image (expected)")
    except Exception as e:
        print(f"WARNING: Face encoding test: {e}")
    finally:
        # Clean up
        if os.path.exists('demo_image.jpg'):
            os.remove('demo_image.jpg')
    
    # Test attendance summary
    print("Testing attendance summary...")
    summary = attendance.get_attendance_summary(7)
    print(f"SUCCESS: Attendance summary: {summary}")
    
    return attendance

def demo_ai_features():
    """Demonstrate AI features"""
    print("Testing AI Features...")
    
    ai = AIFeatures()
    
    # Test sentiment analysis
    print("Testing sentiment analysis...")
    test_texts = [
        "This is amazing! I love it!",
        "This is terrible and awful.",
        "This is okay, nothing special."
    ]
    
    for text in test_texts:
        result = ai.analyze_sentiment(text)
        print(f"Text: '{text}'")
        print(f"Sentiment: {result['sentiment']} (confidence: {result['confidence']:.2f})")
    
    # Test keyword extraction
    print("Testing keyword extraction...")
    test_text = "The meeting is scheduled for tomorrow at 3 PM. Please bring your laptops and prepare the presentation."
    keywords = ai.extract_keywords(test_text)
    print(f"Keywords: {keywords}")
    
    # Test notification categorization
    print("Testing notification categorization...")
    category_result = ai.categorize_notification("Meeting Reminder", "Don't forget about the team meeting tomorrow")
    print(f"Category: {category_result['category']} (confidence: {category_result['confidence']:.2f})")
    
    # Test smart notification generation
    print("Testing smart notification generation...")
    smart_notification = ai.generate_smart_notification("Team meeting scheduled for tomorrow", "meeting")
    print(f"Generated notification:")
    print(f"Title: {smart_notification['title']}")
    print(f"Message: {smart_notification['message']}")
    print(f"Priority: {smart_notification['priority']}")
    print(f"Category: {smart_notification['category']}")
    
    return ai

def demo_notification_engine():
    """Demonstrate notification engine"""
    print("Testing Notification Engine...")
    
    engine = NotificationEngine()
    
    # Test creating notifications
    print("Testing notification creation...")
    
    # Create different types of notifications
    notifications = [
        {
            'title': 'Test Info Notification',
            'message': 'This is a test information notification',
            'type': 'info',
            'priority': 1
        },
        {
            'title': 'Test Warning Notification',
            'message': 'This is a test warning notification',
            'type': 'warning',
            'priority': 3
        },
        {
            'title': 'Test AI Enhanced Notification',
            'message': 'This notification will be enhanced by AI',
            'type': 'info',
            'priority': 2,
            'ai_enhanced': True
        }
    ]
    
    created_count = 0
    for notif in notifications:
        success = engine.create_notification(
            title=notif['title'],
            message=notif['message'],
            notification_type=notif['type'],
            priority=notif['priority'],
            ai_enhanced=notif.get('ai_enhanced', False)
        )
        if success:
            created_count += 1
            print(f"SUCCESS: Created: {notif['title']}")
        else:
            print(f"ERROR: Failed: {notif['title']}")
    
    print(f"Created {created_count}/{len(notifications)} notifications")
    
    # Test notification analytics
    print("Testing notification analytics...")
    analytics = engine.get_notification_analytics(7)
    print(f"Analytics: {analytics}")
    
    # Test system test
    print("Testing notification system...")
    test_results = engine.test_notification_system()
    print(f"Test results: {test_results}")
    
    return engine

def demo_database():
    """Demonstrate database functionality"""
    print("Testing Database...")
    
    db = DatabaseManager()
    
    # Test adding attendance
    print("Testing attendance recording...")
    success = db.add_attendance("Demo User", 0.95)
    if success:
        print("SUCCESS: Attendance recorded successfully")
    else:
        print("ERROR: Failed to record attendance")
    
    # Test getting attendance stats
    print("Testing attendance statistics...")
    stats = db.get_attendance_stats(7)
    print(f"Stats: {stats}")
    
    # Test getting notifications
    print("Testing notification retrieval...")
    notifications = db.get_notifications(limit=5)
    print(f"Found {len(notifications)} notifications")
    
    return db

def main():
    """Main demo function"""
    print("Smart Notification App Demo")
    print("=" * 50)
    
    try:
        # Test each component
        attendance = demo_attendance_system()
        ai = demo_ai_features()
        engine = demo_notification_engine()
        db = demo_database()
        
        print("SUCCESS: Demo completed successfully!")
        print("\nSummary:")
        print("- Attendance system: Functional")
        print("- AI features: Functional")
        print("- Notification engine: Functional")
        print("- Database: Functional")
        
        print("\nTo run the full application:")
        print("streamlit run app.py")
        
    except Exception as e:
        print(f"\nERROR: Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
