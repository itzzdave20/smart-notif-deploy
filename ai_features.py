import re
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
# from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
# import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import schedule
import time
from config import SENTIMENT_ANALYSIS_MODEL, MAX_NOTIFICATION_LENGTH

# Try to import torch, fall back if not available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    print("WARNING: PyTorch not available. Some AI features may be limited.")
    TORCH_AVAILABLE = False

# Try to import transformers, fall back to simple implementation if not available
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    print("SUCCESS: Transformers library loaded successfully")
except ImportError:
    print("WARNING: Transformers library not available. Using simple sentiment analysis.")
    print("   To enable advanced AI features, install transformers:")
    print("   pip install transformers torch")
    TRANSFORMERS_AVAILABLE = False

class AIFeatures:
    def __init__(self):
        self.sentiment_analyzer = None
        self.tokenizer = None
        self.model = None
        self.load_sentiment_model()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.notification_patterns = []
        
    def load_sentiment_model(self):
        """Load sentiment analysis model"""
        try:
            if not TRANSFORMERS_AVAILABLE:
                print("Using simple sentiment analysis (transformers not available)")
                self.sentiment_analyzer = None
                return
            
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=SENTIMENT_ANALYSIS_MODEL,
                return_all_scores=True
            )
            print("Sentiment analysis model loaded successfully")
        except Exception as e:
            print(f"Error loading sentiment model: {e}")
            # Fallback to a simpler approach
            self.sentiment_analyzer = None
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        try:
            if self.sentiment_analyzer:
                results = self.sentiment_analyzer(text)
                
                # Extract sentiment scores
                sentiment_scores = {}
                for result in results[0]:
                    sentiment_scores[result['label']] = result['score']
                
                # Determine overall sentiment
                if 'POSITIVE' in sentiment_scores and 'NEGATIVE' in sentiment_scores:
                    if sentiment_scores['POSITIVE'] > sentiment_scores['NEGATIVE']:
                        overall_sentiment = 'positive'
                        confidence = sentiment_scores['POSITIVE']
                    else:
                        overall_sentiment = 'negative'
                        confidence = sentiment_scores['NEGATIVE']
                elif 'LABEL_1' in sentiment_scores and 'LABEL_0' in sentiment_scores:
                    if sentiment_scores['LABEL_1'] > sentiment_scores['LABEL_0']:
                        overall_sentiment = 'positive'
                        confidence = sentiment_scores['LABEL_1']
                    else:
                        overall_sentiment = 'negative'
                        confidence = sentiment_scores['LABEL_0']
                else:
                    overall_sentiment = 'neutral'
                    confidence = 0.5
                
                return {
                    'sentiment': overall_sentiment,
                    'confidence': confidence,
                    'scores': sentiment_scores
                }
            else:
                # Simple keyword-based sentiment analysis
                return self.simple_sentiment_analysis(text)
                
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': {},
                'error': str(e)
            }
    
    def simple_sentiment_analysis(self, text: str) -> Dict:
        """Simple keyword-based sentiment analysis fallback"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'happy', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry', 'sad', 'disappointed']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return {'sentiment': 'neutral', 'confidence': 0.5, 'scores': {}}
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        if positive_ratio > negative_ratio:
            sentiment = 'positive'
            confidence = min(positive_ratio * 2, 1.0)
        elif negative_ratio > positive_ratio:
            sentiment = 'negative'
            confidence = min(negative_ratio * 2, 1.0)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {'positive': positive_ratio, 'negative': negative_ratio}
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using TF-IDF"""
        try:
            if not text.strip():
                return []
            
            # Clean text
            text = re.sub(r'[^\w\s]', '', text.lower())
            
            # Fit vectorizer and transform text
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top keywords
            scores = tfidf_matrix.toarray()[0]
            keyword_indices = np.argsort(scores)[::-1][:max_keywords]
            
            keywords = [feature_names[i] for i in keyword_indices if scores[i] > 0]
            return keywords
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def categorize_notification(self, title: str, message: str) -> Dict:
        """Categorize notification based on content"""
        try:
            full_text = f"{title} {message}".lower()
            
            categories = {
                'attendance': ['attendance', 'check-in', 'check-out', 'present', 'absent', 'late'],
                'meeting': ['meeting', 'conference', 'call', 'discussion', 'agenda'],
                'reminder': ['reminder', 'don\'t forget', 'remember', 'deadline', 'due'],
                'alert': ['alert', 'urgent', 'important', 'critical', 'emergency'],
                'announcement': ['announcement', 'news', 'update', 'notice', 'information'],
                'system': ['system', 'maintenance', 'update', 'upgrade', 'technical']
            }
            
            category_scores = {}
            for category, keywords in categories.items():
                score = sum(1 for keyword in keywords if keyword in full_text)
                category_scores[category] = score
            
            # Determine best category
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                confidence = category_scores[best_category] / len(full_text.split())
            else:
                best_category = 'general'
                confidence = 0.1
            
            return {
                'category': best_category,
                'confidence': min(confidence, 1.0),
                'scores': category_scores
            }
            
        except Exception as e:
            print(f"Error categorizing notification: {e}")
            return {'category': 'general', 'confidence': 0.1, 'scores': {}}
    
    def calculate_priority(self, title: str, message: str, category: str, sentiment: str) -> int:
        """Calculate notification priority (1-5, where 5 is highest)"""
        try:
            priority = 1  # Base priority
            
            # Category-based priority
            category_priorities = {
                'alert': 5,
                'system': 4,
                'meeting': 3,
                'attendance': 2,
                'reminder': 2,
                'announcement': 1,
                'general': 1
            }
            priority = max(priority, category_priorities.get(category, 1))
            
            # Sentiment-based adjustment
            if sentiment == 'negative':
                priority += 1
            elif sentiment == 'positive':
                priority = max(1, priority - 1)
            
            # Keyword-based priority boost
            urgent_keywords = ['urgent', 'critical', 'emergency', 'immediately', 'asap']
            text_lower = f"{title} {message}".lower()
            if any(keyword in text_lower for keyword in urgent_keywords):
                priority = min(5, priority + 2)
            
            return min(5, max(1, priority))
            
        except Exception as e:
            print(f"Error calculating priority: {e}")
            return 1
    
    def suggest_optimal_time(self, notification_type: str, user_preferences: Dict = None) -> datetime:
        """Suggest optimal time for sending notification"""
        try:
            now = datetime.now()
            
            # Default optimal times based on notification type
            optimal_times = {
                'attendance': [9, 13, 17],  # Morning, lunch, evening
                'meeting': [9, 14, 16],     # Business hours
                'reminder': [10, 15],       # Mid-morning, mid-afternoon
                'alert': [0],               # Immediate
                'announcement': [9, 12, 17], # Morning, lunch, evening
                'system': [8, 20]           # Early morning, evening
            }
            
            if user_preferences and 'notification_times' in user_preferences:
                # Parse user preferences
                times_str = user_preferences['notification_times']
                if times_str:
                    try:
                        hours = [int(t.split(':')[0]) for t in times_str.split(',')]
                        optimal_times[notification_type] = hours
                    except:
                        pass
            
            # Get suggested hours for this notification type
            suggested_hours = optimal_times.get(notification_type, [9, 13, 17])
            
            # Find next optimal time
            for hour in suggested_hours:
                suggested_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
                if suggested_time > now:
                    return suggested_time
            
            # If no time today, use first time tomorrow
            tomorrow = now + timedelta(days=1)
            first_hour = min(suggested_hours)
            return tomorrow.replace(hour=first_hour, minute=0, second=0, microsecond=0)
            
        except Exception as e:
            print(f"Error suggesting optimal time: {e}")
            return datetime.now() + timedelta(minutes=5)
    
    def generate_smart_notification(self, context: str, notification_type: str = 'general') -> Dict:
        """Generate AI-powered notification content"""
        try:
            # Analyze context sentiment
            sentiment_analysis = self.analyze_sentiment(context)
            
            # Extract keywords
            keywords = self.extract_keywords(context)
            
            # Generate notification based on type and sentiment
            if notification_type == 'attendance':
                if sentiment_analysis['sentiment'] == 'positive':
                    title = "Attendance Update"
                    message = f"Great! Attendance has been recorded successfully. Keywords: {', '.join(keywords[:3])}"
                else:
                    title = "Attendance Alert"
                    message = f"Please check attendance records. Keywords: {', '.join(keywords[:3])}"
            
            elif notification_type == 'meeting':
                title = "Meeting Reminder"
                message = f"Upcoming meeting reminder. Context: {context[:100]}..."
            
            elif notification_type == 'system':
                title = "System Notification"
                message = f"System update: {context[:100]}..."
            
            else:
                title = "Smart Notification"
                message = f"AI-generated notification based on: {context[:100]}..."
            
            # Categorize notification
            category_info = self.categorize_notification(title, message)
            
            # Calculate priority
            priority = self.calculate_priority(title, message, category_info['category'], sentiment_analysis['sentiment'])
            
            # Suggest optimal time
            optimal_time = self.suggest_optimal_time(category_info['category'])
            
            return {
                'title': title,
                'message': message[:MAX_NOTIFICATION_LENGTH],
                'category': category_info['category'],
                'priority': priority,
                'sentiment': sentiment_analysis['sentiment'],
                'sentiment_confidence': sentiment_analysis['confidence'],
                'keywords': keywords,
                'suggested_time': optimal_time,
                'ai_generated': True
            }
            
        except Exception as e:
            print(f"Error generating smart notification: {e}")
            return {
                'title': 'AI Notification',
                'message': 'AI-generated notification',
                'category': 'general',
                'priority': 1,
                'sentiment': 'neutral',
                'sentiment_confidence': 0.5,
                'keywords': [],
                'suggested_time': datetime.now(),
                'ai_generated': True,
                'error': str(e)
            }
    
    def analyze_notification_patterns(self, notifications: List[Dict]) -> Dict:
        """Analyze patterns in notification data"""
        try:
            if not notifications:
                return {}
            
            # Analyze timing patterns
            hours = [datetime.fromisoformat(n['created_at']).hour for n in notifications]
            hour_counts = {}
            for hour in hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Analyze category distribution
            categories = [n.get('notification_type', 'unknown') for n in notifications]
            category_counts = {}
            for cat in categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Analyze sentiment trends
            sentiments = []
            for n in notifications:
                if 'sentiment_score' in n and n['sentiment_score'] is not None:
                    sentiments.append(n['sentiment_score'])
            
            avg_sentiment = np.mean(sentiments) if sentiments else 0.5
            
            return {
                'total_notifications': len(notifications),
                'hour_distribution': hour_counts,
                'category_distribution': category_counts,
                'average_sentiment': avg_sentiment,
                'peak_hour': max(hour_counts, key=hour_counts.get) if hour_counts else 9,
                'most_common_category': max(category_counts, key=category_counts.get) if category_counts else 'general'
            }
            
        except Exception as e:
            print(f"Error analyzing notification patterns: {e}")
            return {}
    
    def optimize_notification_schedule(self, user_behavior: Dict) -> List[str]:
        """Optimize notification schedule based on user behavior"""
        try:
            # Default schedule
            default_schedule = ['09:00', '13:00', '17:00']
            
            if not user_behavior or 'hour_distribution' not in user_behavior:
                return default_schedule
            
            # Find peak engagement hours
            hour_dist = user_behavior['hour_distribution']
            if not hour_dist:
                return default_schedule
            
            # Sort hours by engagement
            sorted_hours = sorted(hour_dist.items(), key=lambda x: x[1], reverse=True)
            
            # Take top 3 hours and format them
            optimal_hours = []
            for hour, count in sorted_hours[:3]:
                optimal_hours.append(f"{hour:02d}:00")
            
            return optimal_hours if optimal_hours else default_schedule
            
        except Exception as e:
            print(f"Error optimizing notification schedule: {e}")
            return ['09:00', '13:00', '17:00']
    
    def chat_with_ai(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """AI Chatbot - Answer questions, help with assignments, etc."""
        try:
            if conversation_history is None:
                conversation_history = []
            
            # Simple rule-based responses for common questions
            user_message_lower = user_message.lower()
            
            # Assignment help
            if any(word in user_message_lower for word in ['assignment', 'homework', 'project', 'essay']):
                response = self._handle_assignment_help(user_message)
            
            # Class-related questions
            elif any(word in user_message_lower for word in ['class', 'course', 'schedule', 'enroll']):
                response = self._handle_class_question(user_message)
            
            # Attendance questions
            elif any(word in user_message_lower for word in ['attendance', 'present', 'absent', 'mark']):
                response = self._handle_attendance_question(user_message)
            
            # General questions
            elif any(word in user_message_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
                response = self._handle_general_question(user_message)
            
            # Greetings
            elif any(word in user_message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
                response = "Hello! I'm your AI assistant. I can help you with assignments, classes, attendance, and more. How can I assist you today?"
            
            # Default response
            else:
                response = self._generate_contextual_response(user_message, conversation_history)
            
            return {
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.8
            }
            
        except Exception as e:
            print(f"Error in AI chat: {e}")
            return {
                'response': "I apologize, but I encountered an error. Please try rephrasing your question.",
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _handle_assignment_help(self, message: str) -> str:
        """Handle assignment-related questions"""
        responses = [
            "I can help you with your assignment! Here are some tips:\n"
            "1. Break down the assignment into smaller tasks\n"
            "2. Create a timeline for completion\n"
            "3. Research thoroughly before writing\n"
            "4. Review and edit your work before submitting\n\n"
            "What specific part of your assignment do you need help with?",
            
            "For assignment help, I recommend:\n"
            "• Understanding the requirements clearly\n"
            "• Organizing your thoughts before writing\n"
            "• Citing sources properly\n"
            "• Proofreading for errors\n\n"
            "Feel free to ask me about any specific aspect!",
            
            "I'm here to help with your assignment! Some strategies:\n"
            "• Start early to avoid last-minute stress\n"
            "• Create an outline first\n"
            "• Write a draft, then revise\n"
            "• Get feedback from peers or instructors\n\n"
            "What would you like help with specifically?"
        ]
        return responses[0]  # Return first response for now
    
    def _handle_class_question(self, message: str) -> str:
        """Handle class-related questions"""
        return ("I can help you with class-related questions! I can assist with:\n"
                "• Finding class schedules\n"
                "• Enrollment information\n"
                "• Class requirements\n"
                "• Instructor contact details\n\n"
                "What specific information do you need about your classes?")
    
    def _handle_attendance_question(self, message: str) -> str:
        """Handle attendance-related questions"""
        return ("For attendance questions, I can help you:\n"
                "• Check your attendance records\n"
                "• Understand attendance policies\n"
                "• Mark your attendance\n"
                "• View attendance history\n\n"
                "What would you like to know about attendance?")
    
    def _handle_general_question(self, message: str) -> str:
        """Handle general questions"""
        return ("I'm here to help! I can assist with:\n"
                "• Academic questions and assignments\n"
                "• Class and schedule information\n"
                "• Attendance tracking\n"
                "• General inquiries\n\n"
                "Could you provide more details about what you need help with?")
    
    def _generate_contextual_response(self, message: str, history: List[Dict]) -> str:
        """Generate contextual response based on conversation history"""
        # Extract keywords from message
        keywords = self.extract_keywords(message, max_keywords=5)
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(message)
        
        # Generate response based on context
        if sentiment['sentiment'] == 'positive':
            response = f"Great! I'm glad to help. Based on your message about {', '.join(keywords[:3]) if keywords else 'this topic'}, "
        elif sentiment['sentiment'] == 'negative':
            response = "I understand this might be challenging. Let me help you with "
        else:
            response = "I can help you with "
        
        response += f"your question. Could you provide more details so I can assist you better?"
        
        return response