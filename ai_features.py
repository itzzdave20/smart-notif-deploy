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
            user_message_lower = user_message.lower().strip()
            
            # Greetings (check first)
            if any(word in user_message_lower for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
                response = "Hello! I'm your AI assistant. I can help you with assignments, classes, attendance, and more. How can I assist you today?"
            
            # Computer Science / Programming questions
            elif any(word in user_message_lower for word in ['computer science', 'programming', 'code', 'coding', 'algorithm', 'software', 'developer', 'python', 'java', 'javascript', 'html', 'css', 'database', 'data structure']):
                response = self._handle_computer_science_question(user_message)
            
            # Assignment help
            elif any(word in user_message_lower for word in ['assignment', 'homework', 'project', 'essay', 'paper', 'thesis']):
                response = self._handle_assignment_help(user_message)
            
            # Class-related questions
            elif any(word in user_message_lower for word in ['class', 'course', 'schedule', 'enroll', 'enrollment', 'syllabus']):
                response = self._handle_class_question(user_message)
            
            # Attendance questions
            elif any(word in user_message_lower for word in ['attendance', 'present', 'absent', 'mark attendance', 'check attendance']):
                response = self._handle_attendance_question(user_message)
            
            # What/How/Why questions (educational)
            elif user_message_lower.startswith(('what is', 'what are', 'what does', 'what do', 'what was', 'what were')):
                response = self._handle_what_question(user_message)
            
            elif user_message_lower.startswith(('how to', 'how do', 'how does', 'how can', 'how should')):
                response = self._handle_how_question(user_message)
            
            elif user_message_lower.startswith(('why', 'why is', 'why are', 'why do', 'why does')):
                response = self._handle_why_question(user_message)
            
            # General questions
            elif any(word in user_message_lower for word in ['tell me', 'explain', 'describe', 'define', 'meaning']):
                response = self._handle_explain_question(user_message)
            
            # Default response with better context
            else:
                response = self._generate_contextual_response(user_message, conversation_history)
            
            return {
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.8
            }
            
        except Exception as e:
            print(f"Error in AI chat: {e}")
            import traceback
            print(traceback.format_exc())
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
    
    def _handle_computer_science_question(self, message: str) -> str:
        """Handle computer science and programming questions"""
        message_lower = message.lower()
        
        if 'programming' in message_lower or 'what is programming' in message_lower:
            return ("Programming is the process of creating instructions for computers to follow. It involves:\n\n"
                    "• Writing code in programming languages (like Python, Java, JavaScript)\n"
                    "• Solving problems using algorithms and data structures\n"
                    "• Building software applications, websites, and systems\n"
                    "• Debugging and testing code to ensure it works correctly\n\n"
                    "Programming is a fundamental skill in computer science that allows you to create software, automate tasks, and solve complex problems. Would you like to know more about a specific programming language or concept?")
        
        elif 'computer science' in message_lower:
            return ("Computer Science is the study of computers and computational systems. It covers:\n\n"
                    "• **Programming & Software Development**: Writing code to create applications\n"
                    "• **Algorithms & Data Structures**: Efficient problem-solving methods\n"
                    "• **Computer Systems**: How hardware and software work together\n"
                    "• **Networks & Security**: Internet, cybersecurity, and data protection\n"
                    "• **Artificial Intelligence**: Machine learning and intelligent systems\n"
                    "• **Database Systems**: Storing and managing data\n\n"
                    "Computer Science combines theory and practice to solve real-world problems using technology. What specific area interests you?")
        
        elif any(word in message_lower for word in ['python', 'java', 'javascript', 'c++', 'html', 'css']):
            lang = next((word for word in ['python', 'java', 'javascript', 'c++', 'html', 'css'] if word in message_lower), 'programming')
            return f"I'd be happy to help you with {lang.title()}! {lang.title()} is a powerful programming language used for various applications. What specific aspect of {lang.title()} would you like to learn about?"
        
        elif 'algorithm' in message_lower:
            return ("An algorithm is a step-by-step procedure for solving a problem. Key concepts:\n\n"
                    "• **Efficiency**: How fast an algorithm runs (time complexity)\n"
                    "• **Correctness**: Does it solve the problem correctly?\n"
                    "• **Common Algorithms**: Sorting, searching, graph traversal\n"
                    "• **Design Patterns**: Divide and conquer, dynamic programming, greedy algorithms\n\n"
                    "Algorithms are the foundation of computer science. Would you like examples of specific algorithms?")
        
        elif 'data structure' in message_lower:
            return ("Data structures are ways of organizing and storing data in a computer. Common types:\n\n"
                    "• **Arrays & Lists**: Sequential data storage\n"
                    "• **Stacks & Queues**: LIFO and FIFO structures\n"
                    "• **Trees**: Hierarchical data (binary trees, BST)\n"
                    "• **Hash Tables**: Fast key-value lookups\n"
                    "• **Graphs**: Network relationships\n\n"
                    "Choosing the right data structure is crucial for efficient programming. What would you like to know more about?")
        
        else:
            return ("I can help you with computer science topics! I can explain:\n\n"
                    "• Programming concepts and languages\n"
                    "• Algorithms and data structures\n"
                    "• Software development practices\n"
                    "• Computer science fundamentals\n\n"
                    "What specific topic would you like to learn about?")
    
    def _handle_what_question(self, message: str) -> str:
        """Handle 'what is/are' questions"""
        message_lower = message.lower()
        
        # Extract the topic after "what is/are"
        if 'what is' in message_lower:
            topic = message_lower.split('what is', 1)[1].strip()
        elif 'what are' in message_lower:
            topic = message_lower.split('what are', 1)[1].strip()
        else:
            topic = message_lower.replace('what', '').strip()
        
        # Provide specific answers for common questions
        if 'programming' in topic:
            return self._handle_computer_science_question("what is programming")
        elif 'computer science' in topic or 'cs' in topic:
            return self._handle_computer_science_question("computer science")
        elif 'algorithm' in topic:
            return self._handle_computer_science_question("algorithm")
        elif 'data structure' in topic:
            return self._handle_computer_science_question("data structure")
        else:
            # Generic but helpful response
            keywords = self.extract_keywords(topic, max_keywords=3)
            return (f"Great question! '{topic.title()}' is an interesting topic. "
                   f"While I can provide general guidance, for detailed explanations about {', '.join(keywords) if keywords else 'this topic'}, "
                   f"I recommend:\n\n"
                   f"• Consulting your course materials and textbooks\n"
                   f"• Asking your instructor for clarification\n"
                   f"• Using online educational resources\n"
                   f"• Reviewing class notes and lecture recordings\n\n"
                   f"Would you like help with a specific aspect of this topic, or do you have questions about your assignments?")
    
    def _handle_how_question(self, message: str) -> str:
        """Handle 'how to/do/does' questions"""
        message_lower = message.lower()
        
        if 'program' in message_lower or 'code' in message_lower:
            return ("To start programming, here's a step-by-step guide:\n\n"
                    "1. **Choose a Language**: Start with Python (beginner-friendly) or JavaScript (web development)\n"
                    "2. **Set Up Environment**: Install a code editor (VS Code, PyCharm) and the language runtime\n"
                    "3. **Learn Basics**: Variables, data types, control structures (if/else, loops)\n"
                    "4. **Practice**: Write simple programs, solve coding challenges\n"
                    "5. **Build Projects**: Create small applications to apply what you learn\n"
                    "6. **Use Resources**: Online tutorials, documentation, coding communities\n\n"
                    "Would you like specific guidance on any of these steps?")
        
        elif 'mark attendance' in message_lower or 'attendance' in message_lower:
            return ("To mark your attendance:\n\n"
                    "1. Go to the **Attendance** page in your student dashboard\n"
                    "2. **Step 1**: Scan the QR code displayed by your instructor\n"
                    "3. **Step 2**: Take a selfie photo using your camera or upload a photo\n"
                    "4. Click **Mark Attendance** button\n"
                    "5. Wait for verification - you'll see a success message when done\n\n"
                    "Make sure you're enrolled in the class and the QR code hasn't expired!")
        
        else:
            keywords = self.extract_keywords(message, max_keywords=3)
            return (f"I can help you understand how to {message_lower.replace('how', '').replace('to', '').strip()}! "
                   f"For step-by-step instructions, I recommend:\n\n"
                   f"• Checking your course materials and assignments\n"
                   f"• Reviewing class notes and lecture slides\n"
                   f"• Asking your instructor for guidance\n"
                   f"• Using online tutorials and documentation\n\n"
                   f"Would you like help with a specific part of this process?")
    
    def _handle_why_question(self, message: str) -> str:
        """Handle 'why' questions"""
        message_lower = message.lower()
        
        keywords = self.extract_keywords(message, max_keywords=3)
        return (f"That's a great question! Understanding the 'why' behind concepts is important for learning. "
               f"For a detailed explanation about {', '.join(keywords) if keywords else 'this topic'}, I suggest:\n\n"
               f"• Reviewing your course materials and textbooks\n"
               f"• Asking your instructor during office hours\n"
               f"• Exploring academic resources and research papers\n"
               f"• Discussing with classmates in study groups\n\n"
               f"I can help you with practical aspects like assignments, but for deep conceptual understanding, "
               f"your course materials and instructors are the best resources. What specific aspect would you like help with?")
    
    def _handle_explain_question(self, message: str) -> str:
        """Handle 'explain', 'tell me', 'describe' questions"""
        message_lower = message.lower()
        
        # Extract topic
        topic = message_lower
        for word in ['explain', 'tell me about', 'describe', 'define', 'what is the meaning of']:
            if word in topic:
                topic = topic.split(word, 1)[1].strip()
                break
        
        # Check if it's a CS/programming topic
        if any(word in topic for word in ['programming', 'computer science', 'code', 'algorithm', 'data structure']):
            return self._handle_computer_science_question(topic)
        
        keywords = self.extract_keywords(topic, max_keywords=3)
        return (f"I'd be happy to help explain {topic if topic else 'this topic'}! "
               f"Here's what I can tell you:\n\n"
               f"• For academic concepts, check your course materials and textbooks\n"
               f"• For programming topics, I can provide general guidance\n"
               f"• For assignment help, I can give you tips and strategies\n\n"
               f"Could you be more specific about what aspect of {', '.join(keywords) if keywords else 'this topic'} you'd like me to explain?")
    
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
        
        # Check if message contains academic terms
        academic_terms = ['study', 'learn', 'teach', 'course', 'subject', 'topic', 'concept', 'theory', 'practice', 'exam', 'test', 'quiz']
        is_academic = any(term in message.lower() for term in academic_terms)
        
        # Generate response based on context
        if is_academic:
            response = (f"I can help you with {', '.join(keywords[:2]) if keywords else 'this academic topic'}! "
                       f"For detailed information, I recommend:\n\n"
                       f"• Reviewing your course materials and textbooks\n"
                       f"• Checking your class notes and lecture recordings\n"
                       f"• Asking your instructor for clarification\n"
                       f"• Using online educational resources\n\n"
                       f"What specific aspect would you like help with?")
        elif sentiment['sentiment'] == 'positive':
            response = f"Great! I'm glad to help. Based on your message about {', '.join(keywords[:3]) if keywords else 'this topic'}, I can assist you. Could you provide more details about what you need?"
        elif sentiment['sentiment'] == 'negative':
            response = "I understand this might be challenging. Let me help you with this. Could you provide more details about what you're struggling with?"
        else:
            response = (f"I can help you with {', '.join(keywords[:2]) if keywords else 'your question'}! "
                       f"To give you the best assistance, could you provide more details? For example:\n\n"
                       f"• What specific topic or concept?\n"
                       f"• Is this related to an assignment or class?\n"
                       f"• What would you like to know or accomplish?")
        
        return response