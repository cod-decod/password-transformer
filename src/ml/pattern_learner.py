"""
Pattern Learning Module
Implements machine learning algorithms for password transformation pattern recognition
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
import joblib
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


class PatternLearner:
    """Core ML logic for learning password transformation patterns"""
    
    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        self.cluster_model = None
        self.pattern_database = defaultdict(list)
        self.success_rates = defaultdict(float)
        self.transformation_history = []
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
        
        # Load existing models and data
        self.load_models()
        
    def extract_password_features(self, password: str, analysis: Dict) -> np.ndarray:
        """Extract numerical features from password for ML algorithms"""
        features = [
            analysis.get('length', 0),
            analysis.get('digit_count', 0),
            analysis.get('uppercase_count', 0), 
            analysis.get('lowercase_count', 0),
            analysis.get('special_count', 0),
            analysis.get('entropy', 0),
            analysis.get('character_diversity', 0),
            analysis.get('complexity_score', 0),
            analysis.get('strength_score', 0),
            # Binary features
            int(analysis.get('has_digits', False)),
            int(analysis.get('has_uppercase', False)),
            int(analysis.get('has_lowercase', False)),
            int(analysis.get('has_special', False)),
            int(analysis.get('is_common', False)),
            int(analysis.get('has_keyboard_pattern', False)),
            int(analysis.get('has_repeated_chars', False)),
            int(analysis.get('has_sequential', False)),
            int(analysis.get('has_dictionary_word', False)),
            # Pattern type encoding (one-hot style)
            int(analysis.get('pattern_type') == 'numeric'),
            int(analysis.get('pattern_type') == 'alphabetic'),
            int(analysis.get('pattern_type') == 'word_with_numbers'),
            int(analysis.get('pattern_type') == 'mixed'),
            int(analysis.get('pattern_type') == 'common'),
        ]
        return np.array(features)
        
    def learn_transformation_pattern(self, original: str, transformed: str, 
                                   original_analysis: Dict, transformed_analysis: Dict,
                                   settings: Dict, success_score: float = 0.8):
        """Learn from a successful transformation"""
        
        # Extract features from both passwords
        orig_features = self.extract_password_features(original, original_analysis)
        trans_features = self.extract_password_features(transformed, transformed_analysis)
        
        # Calculate improvement metrics
        strength_improvement = (transformed_analysis.get('strength_score', 0) - 
                              original_analysis.get('strength_score', 0))
        
        # Create pattern record
        pattern = {
            'timestamp': datetime.now().isoformat(),
            'original_features': orig_features.tolist(),
            'transformed_features': trans_features.tolist(),
            'strength_improvement': strength_improvement,
            'settings_used': settings.copy(),
            'success_score': success_score,
            'pattern_type': original_analysis.get('pattern_type', 'unknown'),
            'transformation_summary': self._get_transformation_summary(original, transformed)
        }
        
        # Store pattern
        pattern_key = original_analysis.get('pattern_type', 'unknown')
        self.pattern_database[pattern_key].append(pattern)
        self.transformation_history.append(pattern)
        
        # Update success rates
        self._update_success_rates(pattern_key, success_score, settings)
        
        # Retrain model if we have enough data
        if len(self.transformation_history) % 20 == 0:
            self._retrain_clustering_model()
            
    def _get_transformation_summary(self, original: str, transformed: str) -> Dict:
        """Extract what transformations were applied"""
        summary = {
            'length_change': len(transformed) - len(original),
            'chars_added': len(set(transformed) - set(original)),
            'chars_removed': len(set(original) - set(transformed)),
            'case_changes': sum(1 for i, c in enumerate(original) if i < len(transformed) and c != transformed[i] and c.swapcase() == transformed[i]),
            'substitutions': sum(1 for i, c in enumerate(original) if i < len(transformed) and c != transformed[i] and c.swapcase() != transformed[i])
        }
        return summary
        
    def _update_success_rates(self, pattern_type: str, success_score: float, settings: Dict):
        """Update success rates for different pattern types and settings"""
        # Update pattern-specific success rates
        current_rate = self.success_rates[pattern_type]
        count = len(self.pattern_database[pattern_type])
        
        # Weighted average with more weight to recent results
        self.success_rates[pattern_type] = (current_rate * 0.8 + success_score * 0.2)
        
        # Track setting-specific success rates
        intensity = settings.get('intensity', 'moderate')
        setting_key = f"{pattern_type}_{intensity}"
        self.success_rates[setting_key] = (self.success_rates.get(setting_key, 0.5) * 0.8 + 
                                         success_score * 0.2)
                                         
    def _retrain_clustering_model(self):
        """Retrain clustering model with new data"""
        if len(self.transformation_history) < 10:
            return
            
        try:
            # Prepare feature matrix
            features = []
            for pattern in self.transformation_history:
                features.append(pattern['original_features'])
                
            X = np.array(features)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Determine optimal number of clusters (between 2 and min(10, n_samples//2))
            n_clusters = min(10, max(2, len(features) // 5))
            
            # Train clustering model
            self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            self.cluster_model.fit(X_scaled)
            
            # Save updated model
            self.save_models()
            
        except Exception as e:
            print(f"Error retraining clustering model: {e}")
            
    def predict_best_settings(self, password: str, analysis: Dict) -> Dict[str, Any]:
        """Predict optimal transformation settings for a given password"""
        pattern_type = analysis.get('pattern_type', 'unknown')
        
        # Get historical success rates for this pattern type
        base_rate = self.success_rates.get(pattern_type, 0.6)
        
        # Check intensity success rates
        intensity_rates = {
            'light': self.success_rates.get(f"{pattern_type}_light", 0.5),
            'moderate': self.success_rates.get(f"{pattern_type}_moderate", 0.6), 
            'aggressive': self.success_rates.get(f"{pattern_type}_aggressive", 0.7)
        }
        
        # Find best intensity
        best_intensity = max(intensity_rates.items(), key=lambda x: x[1])[0]
        
        # Get similar patterns using clustering
        similar_patterns = self._find_similar_patterns(password, analysis)
        
        # Aggregate recommendations from similar patterns
        recommendations = self._aggregate_recommendations(similar_patterns, analysis)
        
        # Apply some heuristics based on password characteristics
        recommendations = self._apply_heuristics(recommendations, analysis)
        
        return {
            'recommended_intensity': best_intensity,
            'confidence_score': min(0.95, base_rate + 0.1),
            'settings': recommendations,
            'reasoning': self._generate_reasoning(analysis, similar_patterns, best_intensity)
        }
        
    def _find_similar_patterns(self, password: str, analysis: Dict, top_k: int = 5) -> List[Dict]:
        """Find similar password patterns using clustering or similarity"""
        if not self.transformation_history:
            return []
            
        try:
            # Extract features for current password
            current_features = self.extract_password_features(password, analysis)
            
            # Find most similar patterns
            similarities = []
            for pattern in self.transformation_history:
                orig_features = np.array(pattern['original_features'])
                similarity = cosine_similarity([current_features], [orig_features])[0][0]
                similarities.append((similarity, pattern))
                
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [pattern for _, pattern in similarities[:top_k]]
            
        except Exception as e:
            print(f"Error finding similar patterns: {e}")
            return []
            
    def _aggregate_recommendations(self, similar_patterns: List[Dict], analysis: Dict) -> Dict:
        """Aggregate settings recommendations from similar patterns"""
        if not similar_patterns:
            return self._get_default_settings(analysis)
            
        # Count setting preferences from successful patterns
        setting_counts = defaultdict(int)
        total_weight = 0
        
        for pattern in similar_patterns:
            weight = pattern.get('success_score', 0.5)
            total_weight += weight
            
            settings = pattern.get('settings_used', {})
            for key, value in settings.items():
                if isinstance(value, bool):
                    setting_counts[f"{key}_{value}"] += weight
                    
        # Generate recommendations based on weighted voting
        recommendations = {}
        for setting_key in ['character_substitution', 'add_year', 'intelligent_patterns', 
                          'preserve_strong', 'increment_numbers']:
            true_weight = setting_counts.get(f"{setting_key}_True", 0)
            false_weight = setting_counts.get(f"{setting_key}_False", 0)
            
            if total_weight > 0:
                recommendations[setting_key] = true_weight > false_weight
            else:
                recommendations[setting_key] = True  # Default to True
                
        return recommendations
        
    def _apply_heuristics(self, recommendations: Dict, analysis: Dict) -> Dict:
        """Apply rule-based heuristics to improve recommendations"""
        # For very weak passwords, be more aggressive
        if analysis.get('strength_level') == 'very_weak':
            recommendations['character_substitution'] = True
            recommendations['add_year'] = True
            
        # For already strong passwords, be more conservative
        elif analysis.get('strength_level') in ['strong', 'very_strong']:
            recommendations['preserve_strong'] = True
            
        # If password has no digits, likely need to add some
        if not analysis.get('has_digits', False):
            recommendations['increment_numbers'] = True
            
        # If password is common, definitely need intelligent patterns
        if analysis.get('is_common', False):
            recommendations['intelligent_patterns'] = True
            
        return recommendations
        
    def _get_default_settings(self, analysis: Dict) -> Dict:
        """Get default settings based on password analysis"""
        return {
            'character_substitution': not analysis.get('strength_level') in ['strong', 'very_strong'],
            'add_year': analysis.get('strength_level') in ['very_weak', 'weak'],
            'intelligent_patterns': True,
            'preserve_strong': analysis.get('strength_level') in ['very_strong'],
            'increment_numbers': not analysis.get('has_digits', False)
        }
        
    def _generate_reasoning(self, analysis: Dict, similar_patterns: List[Dict], 
                          best_intensity: str) -> List[str]:
        """Generate human-readable reasoning for recommendations"""
        reasoning = []
        
        pattern_type = analysis.get('pattern_type', 'unknown')
        strength = analysis.get('strength_level', 'unknown')
        
        reasoning.append(f"Password pattern identified as '{pattern_type}' with '{strength}' strength")
        
        if similar_patterns:
            avg_success = np.mean([p.get('success_score', 0.5) for p in similar_patterns])
            reasoning.append(f"Found {len(similar_patterns)} similar patterns with {avg_success:.1%} average success rate")
            
        reasoning.append(f"Recommended intensity: {best_intensity} based on historical success rates")
        
        if analysis.get('is_common'):
            reasoning.append("Common password detected - applying intelligent pattern transformation")
            
        if not analysis.get('has_special'):
            reasoning.append("No special characters detected - recommend adding some")
            
        return reasoning
        
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about what the system has learned"""
        if not self.transformation_history:
            return {'total_transformations': 0, 'patterns_learned': 0}
            
        # Calculate statistics
        total_transformations = len(self.transformation_history)
        pattern_types = Counter(p.get('pattern_type', 'unknown') for p in self.transformation_history)
        
        avg_improvement = np.mean([p.get('strength_improvement', 0) for p in self.transformation_history])
        avg_success = np.mean([p.get('success_score', 0.5) for p in self.transformation_history])
        
        # Best performing settings
        setting_success = defaultdict(list)
        for pattern in self.transformation_history:
            settings = pattern.get('settings_used', {})
            success = pattern.get('success_score', 0.5)
            for key, value in settings.items():
                setting_success[f"{key}={value}"].append(success)
                
        best_settings = {}
        for setting, scores in setting_success.items():
            if len(scores) >= 3:  # Only if we have enough data
                best_settings[setting] = np.mean(scores)
                
        return {
            'total_transformations': total_transformations,
            'patterns_learned': len(pattern_types),
            'pattern_distribution': dict(pattern_types),
            'average_strength_improvement': round(avg_improvement, 2),
            'average_success_rate': round(avg_success, 3),
            'success_rates_by_pattern': {k: round(v, 3) for k, v in self.success_rates.items()},
            'best_performing_settings': sorted(best_settings.items(), key=lambda x: x[1], reverse=True)[:5],
            'cluster_model_trained': self.cluster_model is not None
        }
        
    def save_models(self):
        """Save ML models and learning data to disk"""
        try:
            # Save clustering model
            if self.cluster_model:
                joblib.dump(self.cluster_model, os.path.join(self.model_dir, 'cluster_model.pkl'))
                joblib.dump(self.scaler, os.path.join(self.model_dir, 'scaler.pkl'))
                
            # Save pattern database and success rates
            data = {
                'pattern_database': dict(self.pattern_database),
                'success_rates': dict(self.success_rates),
                'transformation_history': self.transformation_history[-1000:]  # Keep last 1000
            }
            
            with open(os.path.join(self.model_dir, 'learning_data.json'), 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving models: {e}")
            
    def load_models(self):
        """Load existing ML models and learning data"""
        try:
            # Load clustering model
            cluster_path = os.path.join(self.model_dir, 'cluster_model.pkl')
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            
            if os.path.exists(cluster_path) and os.path.exists(scaler_path):
                self.cluster_model = joblib.load(cluster_path)
                self.scaler = joblib.load(scaler_path)
                
            # Load learning data
            data_path = os.path.join(self.model_dir, 'learning_data.json')
            if os.path.exists(data_path):
                with open(data_path, 'r') as f:
                    data = json.load(f)
                    
                self.pattern_database = defaultdict(list, data.get('pattern_database', {}))
                self.success_rates = defaultdict(float, data.get('success_rates', {}))
                self.transformation_history = data.get('transformation_history', [])
                
        except Exception as e:
            print(f"Error loading models: {e}")
            # Initialize with empty data if loading fails
            self.pattern_database = defaultdict(list)
            self.success_rates = defaultdict(float)
            self.transformation_history = []