"""
User Behavior Tracking Module
Tracks user preferences and choices to build personalized profiles
"""
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional
import sqlite3


class BehaviorTracker:
    """Track and analyze user behavior patterns"""
    
    def __init__(self, db_path: str = "data/behavior.db"):
        self.db_path = db_path
        self.session_data = defaultdict(list)
        self.user_preferences = defaultdict(dict)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load existing preferences
        self._load_preferences()
        
    def _init_database(self):
        """Initialize SQLite database for behavior tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    context TEXT,
                    settings_used TEXT,
                    password_pattern TEXT,
                    success_rating INTEGER,
                    session_id TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transformation_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    original_strength TEXT,
                    transformed_strength TEXT,
                    user_rating INTEGER,
                    accepted BOOLEAN,
                    pattern_type TEXT,
                    settings_json TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE,
                    preference_value TEXT,
                    confidence_score REAL,
                    last_updated TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing behavior database: {e}")
            
    def track_transformation_attempt(self, settings: Dict, password_pattern: str, 
                                   original_strength: str, session_id: str = None):
        """Track when user attempts a transformation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_actions 
                (timestamp, action_type, context, settings_used, password_pattern, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                'transformation_attempt',
                original_strength,
                json.dumps(settings),
                password_pattern,
                session_id or 'default'
            ))
            
            conn.commit()
            conn.close()
            
            # Update session data
            self.session_data[session_id or 'default'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'transformation_attempt',
                'settings': settings.copy(),
                'pattern': password_pattern
            })
            
        except Exception as e:
            print(f"Error tracking transformation attempt: {e}")
            
    def track_transformation_feedback(self, original_strength: str, transformed_strength: str,
                                    user_rating: int, accepted: bool, pattern_type: str,
                                    settings: Dict):
        """Track user feedback on transformation results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transformation_feedback
                (timestamp, original_strength, transformed_strength, user_rating, 
                 accepted, pattern_type, settings_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                original_strength,
                transformed_strength,
                user_rating,
                accepted,
                pattern_type,
                json.dumps(settings)
            ))
            
            conn.commit()
            conn.close()
            
            # Update preferences based on feedback
            self._update_preferences_from_feedback(settings, user_rating, accepted, pattern_type)
            
        except Exception as e:
            print(f"Error tracking transformation feedback: {e}")
            
    def track_settings_change(self, setting_name: str, old_value: Any, new_value: Any,
                            session_id: str = None):
        """Track when user changes settings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_actions
                (timestamp, action_type, context, settings_used, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                'settings_change',
                f"{setting_name}: {old_value} -> {new_value}",
                json.dumps({setting_name: new_value}),
                session_id or 'default'
            ))
            
            conn.commit()
            conn.close()
            
            # Update preferences
            self._learn_setting_preference(setting_name, new_value)
            
        except Exception as e:
            print(f"Error tracking settings change: {e}")
            
    def _update_preferences_from_feedback(self, settings: Dict, rating: int, 
                                        accepted: bool, pattern_type: str):
        """Update user preferences based on feedback"""
        # Weight positive feedback more heavily
        weight = max(0.1, rating / 10.0) if accepted else 0.05
        
        for setting_key, setting_value in settings.items():
            pref_key = f"{pattern_type}_{setting_key}"
            
            current_pref = self.user_preferences[pref_key]
            current_value = current_pref.get('value', setting_value)
            current_confidence = current_pref.get('confidence', 0.5)
            current_count = current_pref.get('count', 0)
            
            # Update preference using weighted average
            if isinstance(setting_value, bool):
                if setting_value == current_value:
                    new_confidence = min(0.95, current_confidence + weight)
                else:
                    new_confidence = max(0.05, current_confidence - weight)
                    if new_confidence < 0.3:  # Switch preference
                        current_value = setting_value
                        new_confidence = 0.6
            else:
                # For non-boolean values, track frequency
                new_confidence = min(0.95, current_confidence + weight)
                current_value = setting_value
                
            self.user_preferences[pref_key] = {
                'value': current_value,
                'confidence': new_confidence,
                'count': current_count + 1,
                'last_updated': datetime.now().isoformat()
            }
            
        # Save preferences
        self._save_preferences()
        
    def _learn_setting_preference(self, setting_name: str, value: Any):
        """Learn user preference for a specific setting"""
        current_pref = self.user_preferences.get(setting_name, {})
        current_count = current_pref.get('count', 0)
        
        # Simple frequency-based learning
        self.user_preferences[setting_name] = {
            'value': value,
            'confidence': min(0.9, 0.5 + (current_count * 0.05)),
            'count': current_count + 1,
            'last_updated': datetime.now().isoformat()
        }
        
        self._save_preferences()
        
    def get_user_preferences(self, pattern_type: str = None) -> Dict[str, Any]:
        """Get learned user preferences, optionally filtered by pattern type"""
        if pattern_type:
            # Return preferences specific to this pattern type
            pattern_prefs = {}
            for key, pref in self.user_preferences.items():
                if key.startswith(f"{pattern_type}_"):
                    setting_name = key.replace(f"{pattern_type}_", "")
                    if pref.get('confidence', 0) > 0.6:  # Only confident preferences
                        pattern_prefs[setting_name] = pref['value']
            return pattern_prefs
        else:
            # Return general preferences
            general_prefs = {}
            for key, pref in self.user_preferences.items():
                if '_' not in key and pref.get('confidence', 0) > 0.6:
                    general_prefs[key] = pref['value']
            return general_prefs
            
    def get_behavior_analysis(self) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent activity (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            cursor.execute('''
                SELECT action_type, COUNT(*) 
                FROM user_actions 
                WHERE timestamp > ? 
                GROUP BY action_type
            ''', (thirty_days_ago,))
            
            activity_counts = dict(cursor.fetchall())
            
            # Get transformation success rates
            cursor.execute('''
                SELECT pattern_type, AVG(user_rating), COUNT(*)
                FROM transformation_feedback
                WHERE timestamp > ?
                GROUP BY pattern_type
            ''', (thirty_days_ago,))
            
            success_by_pattern = {}
            for pattern, avg_rating, count in cursor.fetchall():
                success_by_pattern[pattern] = {
                    'average_rating': round(avg_rating, 2),
                    'total_transformations': count
                }
                
            # Get most used settings
            cursor.execute('''
                SELECT settings_used, COUNT(*)
                FROM user_actions
                WHERE action_type = 'transformation_attempt' AND timestamp > ?
                GROUP BY settings_used
                ORDER BY COUNT(*) DESC
                LIMIT 5
            ''', (thirty_days_ago,))
            
            popular_settings = []
            for settings_json, count in cursor.fetchall():
                try:
                    settings = json.loads(settings_json)
                    popular_settings.append({'settings': settings, 'usage_count': count})
                except:
                    pass
                    
            conn.close()
            
            # Calculate preference confidence
            avg_confidence = 0
            confident_prefs = 0
            for pref in self.user_preferences.values():
                confidence = pref.get('confidence', 0)
                avg_confidence += confidence
                if confidence > 0.7:
                    confident_prefs += 1
                    
            if self.user_preferences:
                avg_confidence /= len(self.user_preferences)
                
            return {
                'total_preferences_learned': len(self.user_preferences),
                'confident_preferences': confident_prefs,
                'average_preference_confidence': round(avg_confidence, 3),
                'recent_activity': activity_counts,
                'success_rates_by_pattern': success_by_pattern,
                'popular_settings': popular_settings,
                'learning_quality': self._assess_learning_quality()
            }
            
        except Exception as e:
            print(f"Error analyzing behavior: {e}")
            return {'error': str(e)}
            
    def _assess_learning_quality(self) -> str:
        """Assess the quality of behavior learning"""
        if not self.user_preferences:
            return "No learning data available"
            
        high_confidence = sum(1 for p in self.user_preferences.values() 
                            if p.get('confidence', 0) > 0.8)
        total_prefs = len(self.user_preferences)
        
        quality_ratio = high_confidence / total_prefs if total_prefs > 0 else 0
        
        if quality_ratio > 0.7:
            return "High quality - confident in most preferences"
        elif quality_ratio > 0.4:
            return "Moderate quality - learning user patterns"
        else:
            return "Low quality - need more user interaction data"
            
    def get_personalized_recommendations(self, pattern_type: str, 
                                       base_settings: Dict) -> Dict[str, Any]:
        """Get personalized recommendations based on learned behavior"""
        # Start with base settings
        recommendations = base_settings.copy()
        
        # Apply learned preferences
        user_prefs = self.get_user_preferences(pattern_type)
        general_prefs = self.get_user_preferences()
        
        confidence_scores = {}
        
        # Apply pattern-specific preferences first
        for setting, value in user_prefs.items():
            if setting in recommendations:
                recommendations[setting] = value
                pref_key = f"{pattern_type}_{setting}"
                confidence_scores[setting] = self.user_preferences[pref_key]['confidence']
                
        # Apply general preferences for settings not covered by pattern-specific ones
        for setting, value in general_prefs.items():
            if setting in recommendations and setting not in user_prefs:
                recommendations[setting] = value
                confidence_scores[setting] = self.user_preferences[setting]['confidence']
                
        # Calculate overall confidence
        overall_confidence = 0.6  # Base confidence
        if confidence_scores:
            overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)
            
        return {
            'settings': recommendations,
            'confidence': round(overall_confidence, 3),
            'personalization_applied': bool(user_prefs or general_prefs),
            'adapted_settings': list(user_prefs.keys()) + list(general_prefs.keys())
        }
        
    def _save_preferences(self):
        """Save preferences to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for key, pref in self.user_preferences.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences
                    (preference_key, preference_value, confidence_score, last_updated)
                    VALUES (?, ?, ?, ?)
                ''', (
                    key,
                    json.dumps(pref),
                    pref.get('confidence', 0.5),
                    pref.get('last_updated', datetime.now().isoformat())
                ))
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving preferences: {e}")
            
    def _load_preferences(self):
        """Load preferences from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preference_key, preference_value
                FROM user_preferences
            ''')
            
            for key, value_json in cursor.fetchall():
                try:
                    self.user_preferences[key] = json.loads(value_json)
                except:
                    pass
                    
            conn.close()
            
        except Exception as e:
            print(f"Error loading preferences: {e}")
            
    def reset_learning_data(self):
        """Reset all learning data (useful for testing or fresh start)"""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self._init_database()
            self.user_preferences.clear()
            self.session_data.clear()
            return True
        except Exception as e:
            print(f"Error resetting learning data: {e}")
            return False