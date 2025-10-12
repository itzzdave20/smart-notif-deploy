import cv2
# import face_recognition  # Requires CMake installation
import numpy as np
import os
import pickle
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import base64
from PIL import Image
import io
from database import DatabaseManager
from config import FACE_ENCODINGS_PATH, FACE_RECOGNITION_TOLERANCE, FACE_RECOGNITION_MODEL

# Mock face_recognition functions for demo purposes
def mock_face_encodings(image, model='hog'):
    """Mock face encodings function"""
    return []

def mock_face_locations(image, model='hog'):
    """Mock face locations function"""
    return []

def mock_compare_faces(known_encodings, face_encoding, tolerance=0.6):
    """Mock compare faces function"""
    return []

def mock_face_distance(known_encodings, face_encoding):
    """Mock face distance function"""
    return np.array([1.0])

# Try to import face_recognition, fall back to mocks if not available
try:
    import face_recognition
    face_encodings = face_recognition.face_encodings
    face_locations = face_recognition.face_locations
    compare_faces = face_recognition.compare_faces
    face_distance = face_recognition.face_distance
    FACE_RECOGNITION_AVAILABLE = True
    print("SUCCESS: Face recognition library loaded successfully")
except ImportError:
    print("WARNING: Face recognition library not available. Using mock functions.")
    print("   To enable face recognition, install CMake and face-recognition library:")
    print("   pip install cmake")
    print("   pip install face-recognition")
    face_encodings = mock_face_encodings
    face_locations = mock_face_locations
    compare_faces = mock_compare_faces
    face_distance = mock_face_distance
    FACE_RECOGNITION_AVAILABLE = False

class AttendanceSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.known_face_encodings = {}
        self.known_face_names = []
        self.load_face_encodings()
    
    def load_face_encodings(self):
        """Load face encodings from database"""
        try:
            encodings_data = self.db.get_face_encodings()
            self.known_face_encodings = {}
            self.known_face_names = []
            
            for name, encoding_bytes in encodings_data.items():
                encoding = pickle.loads(encoding_bytes)
                self.known_face_encodings[name] = encoding
                self.known_face_names.append(name)
            
            print(f"Loaded {len(self.known_face_names)} face encodings")
        except Exception as e:
            print(f"Error loading face encodings: {e}")
    
    def encode_face_from_image(self, image_path: str) -> Optional[np.ndarray]:
        """Encode face from image file"""
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                print("WARNING: Face recognition not available. Creating mock encoding.")
                return np.random.rand(128)  # Mock 128-dimensional encoding
            
            image = face_recognition.load_image_file(image_path)
            encodings = face_encodings(image, model=FACE_RECOGNITION_MODEL)
            
            if len(encodings) > 0:
                return encodings[0]
            else:
                print(f"No face found in {image_path}")
                return None
        except Exception as e:
            print(f"Error encoding face from {image_path}: {e}")
            return None
    
    def encode_face_from_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Encode face from image bytes"""
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                print("WARNING: Face recognition not available. Creating mock encoding.")
                return np.random.rand(128)  # Mock 128-dimensional encoding
            
            image = Image.open(io.BytesIO(image_bytes))
            image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
            
            encodings = face_encodings(image_rgb, model=FACE_RECOGNITION_MODEL)
            
            if len(encodings) > 0:
                return encodings[0]
            else:
                print("No face found in image bytes")
                return None
        except Exception as e:
            print(f"Error encoding face from bytes: {e}")
            return None
    
    def register_person(self, name: str, image_path: str = None, image_bytes: bytes = None) -> bool:
        """Register a new person for attendance tracking"""
        try:
            if image_path:
                encoding = self.encode_face_from_image(image_path)
            elif image_bytes:
                encoding = self.encode_face_from_bytes(image_bytes)
            else:
                print("Either image_path or image_bytes must be provided")
                return False
            
            if encoding is not None:
                # Save encoding to database
                encoding_bytes = pickle.dumps(encoding)
                success = self.db.save_face_encoding(name, encoding_bytes)
                
                if success:
                    # Update in-memory data
                    self.known_face_encodings[name] = encoding
                    self.known_face_names.append(name)
                    print(f"Successfully registered {name}")
                    return True
                else:
                    print(f"Failed to save encoding for {name}")
                    return False
            else:
                print(f"Failed to encode face for {name}")
                return False
                
        except Exception as e:
            print(f"Error registering person {name}: {e}")
            return False
    
    def recognize_faces_in_image(self, image_path: str = None, image_bytes: bytes = None) -> List[Dict]:
        """Recognize faces in an image and return results"""
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                print("WARNING: Face recognition not available. Creating mock results.")
                return [{
                    'name': 'Demo User',
                    'confidence': 0.95,
                    'face_location': (50, 150, 150, 50),
                    'recognized': True
                }]
            
            if image_path:
                image = face_recognition.load_image_file(image_path)
            elif image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                image = np.array(image)
            else:
                print("Either image_path or image_bytes must be provided")
                return []
            
            # Find face locations and encodings
            locations = face_locations(image, model=FACE_RECOGNITION_MODEL)
            encodings = face_encodings(image, locations, model=FACE_RECOGNITION_MODEL)
            
            results = []
            
            for i, face_encoding in enumerate(encodings):
                # Compare with known faces
                matches = compare_faces(
                    list(self.known_face_encodings.values()), 
                    face_encoding, 
                    tolerance=FACE_RECOGNITION_TOLERANCE
                )
                
                distances = face_distance(
                    list(self.known_face_encodings.values()), 
                    face_encoding
                )
                
                best_match_index = np.argmin(distances)
                
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    confidence = 1 - distances[best_match_index]
                    
                    results.append({
                        'name': name,
                        'confidence': confidence,
                        'face_location': locations[i],
                        'recognized': True
                    })
                else:
                    results.append({
                        'name': 'Unknown',
                        'confidence': 0,
                        'face_location': locations[i],
                        'recognized': False
                    })
            
            return results
            
        except Exception as e:
            print(f"Error recognizing faces: {e}")
            return []
    
    def mark_attendance(self, image_path: str = None, image_bytes: bytes = None) -> Dict:
        """Mark attendance based on face recognition"""
        try:
            results = self.recognize_faces_in_image(image_path, image_bytes)
            
            attendance_results = {
                'timestamp': datetime.now(),
                'recognized_faces': [],
                'unknown_faces': [],
                'total_faces': len(results),
                'success': False
            }
            
            for result in results:
                if result['recognized'] and result['confidence'] > 0.6:
                    # Mark attendance in database
                    success = self.db.add_attendance(
                        result['name'], 
                        result['confidence'],
                        image_path
                    )
                    
                    if success:
                        attendance_results['recognized_faces'].append({
                            'name': result['name'],
                            'confidence': result['confidence']
                        })
                        attendance_results['success'] = True
                else:
                    attendance_results['unknown_faces'].append({
                        'location': result['face_location'],
                        'confidence': result['confidence']
                    })
            
            return attendance_results
            
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return {
                'timestamp': datetime.now(),
                'recognized_faces': [],
                'unknown_faces': [],
                'total_faces': 0,
                'success': False,
                'error': str(e)
            }
    
    def get_attendance_summary(self, days: int = 7) -> Dict:
        """Get attendance summary for the last N days"""
        try:
            stats = self.db.get_attendance_stats(days)
            today_attendance = self.db.get_attendance_today()
            
            return {
                'stats': stats,
                'today_attendance': today_attendance,
                'registered_people': len(self.known_face_names),
                'people_list': self.known_face_names
            }
        except Exception as e:
            print(f"Error getting attendance summary: {e}")
            return {}
    
    def capture_from_camera(self) -> Optional[np.ndarray]:
        """Capture image from camera"""
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return frame
            else:
                print("Failed to capture from camera")
                return None
        except Exception as e:
            print(f"Error capturing from camera: {e}")
            return None
    
    def draw_face_boxes(self, image: np.ndarray, results: List[Dict]) -> np.ndarray:
        """Draw bounding boxes around recognized faces"""
        try:
            image_with_boxes = image.copy()
            
            for result in results:
                top, right, bottom, left = result['face_location']
                
                if result['recognized']:
                    color = (0, 255, 0)  # Green for recognized
                    label = f"{result['name']} ({result['confidence']:.2f})"
                else:
                    color = (0, 0, 255)  # Red for unknown
                    label = "Unknown"
                
                # Draw rectangle
                cv2.rectangle(image_with_boxes, (left, top), (right, bottom), color, 2)
                
                # Draw label
                cv2.rectangle(image_with_boxes, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(image_with_boxes, label, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            return image_with_boxes
            
        except Exception as e:
            print(f"Error drawing face boxes: {e}")
            return image
