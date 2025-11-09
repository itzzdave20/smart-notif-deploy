import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SmartScheduler:
    def __init__(self):
        self.schedules_file = "schedules.json"
        self.schedules = self.load_schedules()
    
    def load_schedules(self) -> Dict:
        """Load schedules from file"""
        if os.path.exists(self.schedules_file):
            try:
                with open(self.schedules_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_schedules(self):
        """Save schedules to file"""
        with open(self.schedules_file, 'w') as f:
            json.dump(self.schedules, f, indent=2)
    
    def create_schedule(self, schedule_type: str, title: str, description: str, 
                       scheduled_datetime: str, created_by: str, 
                       participants: List[str] = None, location: str = None,
                       reminder_minutes: int = 15, recurrence: str = None) -> Dict:
        """Create a new schedule item"""
        schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        schedule_item = {
            'id': schedule_id,
            'type': schedule_type,  # 'meeting', 'class', 'announcement', 'reminder'
            'title': title,
            'description': description,
            'scheduled_datetime': scheduled_datetime,
            'created_by': created_by,
            'created_at': datetime.now().isoformat(),
            'participants': participants or [],
            'location': location,
            'reminder_minutes': reminder_minutes,
            'recurrence': recurrence,  # 'daily', 'weekly', 'monthly', None
            'status': 'scheduled',
            'notified': False
        }
        
        self.schedules[schedule_id] = schedule_item
        self.save_schedules()
        
        return schedule_item
    
    def get_schedules(self, user: str = None, schedule_type: str = None, 
                     start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get schedules with optional filters"""
        schedules = list(self.schedules.values())
        
        # Filter by user
        if user:
            schedules = [s for s in schedules 
                        if s['created_by'] == user or user in s.get('participants', [])]
        
        # Filter by type
        if schedule_type:
            schedules = [s for s in schedules if s['type'] == schedule_type]
        
        # Filter by date range
        if start_date:
            start = datetime.fromisoformat(start_date)
            schedules = [s for s in schedules 
                        if datetime.fromisoformat(s['scheduled_datetime']) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            schedules = [s for s in schedules 
                        if datetime.fromisoformat(s['scheduled_datetime']) <= end]
        
        # Sort by scheduled datetime
        schedules.sort(key=lambda x: x['scheduled_datetime'])
        
        return schedules
    
    def get_upcoming_schedules(self, user: str = None, hours: int = 24) -> List[Dict]:
        """Get upcoming schedules within specified hours"""
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        
        schedules = self.get_schedules(user=user)
        upcoming = []
        
        for schedule in schedules:
            scheduled_time = datetime.fromisoformat(schedule['scheduled_datetime'])
            if now <= scheduled_time <= end_time and schedule['status'] == 'scheduled':
                upcoming.append(schedule)
        
        return upcoming
    
    def update_schedule(self, schedule_id: str, updates: Dict) -> bool:
        """Update a schedule item"""
        if schedule_id not in self.schedules:
            return False
        
        self.schedules[schedule_id].update(updates)
        self.schedules[schedule_id]['updated_at'] = datetime.now().isoformat()
        self.save_schedules()
        return True
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule item"""
        if schedule_id not in self.schedules:
            return False
        
        del self.schedules[schedule_id]
        self.save_schedules()
        return True
    
    def mark_completed(self, schedule_id: str) -> bool:
        """Mark a schedule as completed"""
        return self.update_schedule(schedule_id, {'status': 'completed'})
    
    def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a schedule"""
        return self.update_schedule(schedule_id, {'status': 'cancelled'})
    
    def get_schedules_by_date(self, date: str, user: str = None) -> List[Dict]:
        """Get all schedules for a specific date"""
        target_date = datetime.fromisoformat(date).date()
        schedules = self.get_schedules(user=user)
        
        result = []
        for schedule in schedules:
            schedule_date = datetime.fromisoformat(schedule['scheduled_datetime']).date()
            if schedule_date == target_date:
                result.append(schedule)
        
        return result
    
    def check_reminders(self) -> List[Dict]:
        """Check for schedules that need reminders"""
        now = datetime.now()
        reminders = []
        
        for schedule in self.schedules.values():
            if schedule['status'] != 'scheduled' or schedule.get('notified', False):
                continue
            
            scheduled_time = datetime.fromisoformat(schedule['scheduled_datetime'])
            reminder_time = scheduled_time - timedelta(minutes=schedule.get('reminder_minutes', 15))
            
            if now >= reminder_time:
                reminders.append(schedule)
                schedule['notified'] = True
        
        if reminders:
            self.save_schedules()
        
        return reminders

