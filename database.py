import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional
import pandas as pd
from config import DATABASE_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                date DATE NOT NULL,
                status TEXT DEFAULT 'present',
                confidence REAL,
                image_path TEXT
            )
        ''')
        
        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT DEFAULT 'info',
                priority INTEGER DEFAULT 1,
                created_at DATETIME NOT NULL,
                scheduled_for DATETIME,
                sent_at DATETIME,
                status TEXT DEFAULT 'pending',
                sentiment_score REAL,
                ai_generated BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create face encodings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS face_encodings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT UNIQUE NOT NULL,
                encoding BLOB NOT NULL,
                created_at DATETIME NOT NULL,
                last_updated DATETIME NOT NULL
            )
        ''')
        
        # Create notification preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT UNIQUE NOT NULL,
                email_notifications BOOLEAN DEFAULT TRUE,
                push_notifications BOOLEAN DEFAULT TRUE,
                notification_times TEXT DEFAULT '09:00,13:00,17:00',
                priority_threshold INTEGER DEFAULT 2,
                created_at DATETIME NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_attendance(self, person_name: str, confidence: float = 1.0, image_path: str = None) -> bool:
        """Add attendance record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            today = date.today()
            
            cursor.execute('''
                INSERT INTO attendance (person_name, timestamp, date, confidence, image_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (person_name, now, today, confidence, image_path))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding attendance: {e}")
            return False
    
    def get_attendance_today(self) -> List[Dict]:
        """Get today's attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = date.today()
        cursor.execute('''
            SELECT person_name, timestamp, confidence, status
            FROM attendance
            WHERE date = ?
            ORDER BY timestamp DESC
        ''', (today,))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                'person_name': row[0],
                'timestamp': row[1],
                'confidence': row[2],
                'status': row[3]
            })
        
        conn.close()
        return records
    
    def get_attendance_stats(self, days: int = 30) -> Dict:
        """Get attendance statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total attendance count
        cursor.execute('''
            SELECT COUNT(*) FROM attendance
            WHERE date >= date('now', '-{} days')
        '''.format(days))
        total_count = cursor.fetchone()[0]
        
        # Get unique people count
        cursor.execute('''
            SELECT COUNT(DISTINCT person_name) FROM attendance
            WHERE date >= date('now', '-{} days')
        '''.format(days))
        unique_people = cursor.fetchone()[0]
        
        # Get today's attendance
        today = date.today()
        cursor.execute('''
            SELECT COUNT(DISTINCT person_name) FROM attendance
            WHERE date = ?
        ''', (today,))
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_attendance': total_count,
            'unique_people': unique_people,
            'today_attendance': today_count,
            'period_days': days
        }
    
    def add_notification(self, title: str, message: str, notification_type: str = 'info', 
                       priority: int = 1, scheduled_for: datetime = None, 
                       sentiment_score: float = None, ai_generated: bool = False) -> bool:
        """Add a new notification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute('''
                INSERT INTO notifications 
                (title, message, notification_type, priority, created_at, 
                 scheduled_for, sentiment_score, ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, message, notification_type, priority, now, 
                  scheduled_for, sentiment_score, ai_generated))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding notification: {e}")
            return False
    
    def get_notifications(self, limit: int = 50, status: str = None) -> List[Dict]:
        """Get notifications with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, title, message, notification_type, priority, 
                   created_at, scheduled_for, sent_at, status, sentiment_score, ai_generated
            FROM notifications
        '''
        
        params = []
        if status:
            query += ' WHERE status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row[0],
                'title': row[1],
                'message': row[2],
                'notification_type': row[3],
                'priority': row[4],
                'created_at': row[5],
                'scheduled_for': row[6],
                'sent_at': row[7],
                'status': row[8],
                'sentiment_score': row[9],
                'ai_generated': row[10]
            })
        
        conn.close()
        return notifications
    
    def update_notification_status(self, notification_id: int, status: str) -> bool:
        """Update notification status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sent_at = datetime.now() if status == 'sent' else None
            
            cursor.execute('''
                UPDATE notifications 
                SET status = ?, sent_at = ?
                WHERE id = ?
            ''', (status, sent_at, notification_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating notification status: {e}")
            return False
    
    def save_face_encoding(self, person_name: str, encoding: bytes) -> bool:
        """Save face encoding for a person"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now()
            
            # Check if person already exists
            cursor.execute('SELECT id FROM face_encodings WHERE person_name = ?', (person_name,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE face_encodings 
                    SET encoding = ?, last_updated = ?
                    WHERE person_name = ?
                ''', (encoding, now, person_name))
            else:
                cursor.execute('''
                    INSERT INTO face_encodings (person_name, encoding, created_at, last_updated)
                    VALUES (?, ?, ?, ?)
                ''', (person_name, encoding, now, now))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving face encoding: {e}")
            return False
    
    def get_face_encodings(self) -> Dict[str, bytes]:
        """Get all face encodings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT person_name, encoding FROM face_encodings')
        
        encodings = {}
        for row in cursor.fetchall():
            encodings[row[0]] = row[1]
        
        conn.close()
        return encodings
