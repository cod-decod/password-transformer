"""
Recommendation Engine Module
Provides smart recommendations based on ML insights and user behavior
"""
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from .pattern_learner import PatternLearner
from .behavior_tracker import BehaviorTracker
from datetime import datetime
import re


class RecommendationEngine:
    """Smart recommendations combining ML patterns and user behavior"""
    
    def __init__(self, model_dir: str = "data/models", db_path: str = "data/behavior.db"):
        self.pattern_learner = PatternLearner(model_dir)
        self.behavior_tracker = BehaviorTracker(db_path)
        
        # Domain-specific knowledge
        self.domain_patterns = {
            'gmail.com': {'conservative': True, 'common_patterns': ['word_with_numbers']},
            'yahoo.com': {'conservative': True, 'common_patterns': ['alphabetic', 'word_with_numbers']},
            'hotmail.com': {'conservative': True, 'common_patterns': ['word_with_numbers']},
            'outlook.com': {'conservative': True, 'common_patterns': ['mixed']},
            'corporate': {'conservative': False, 'common_patterns': ['mixed', 'alphabetic']},
            'edu': {'conservative': False, 'common_patterns': ['word_with_numbers', 'mixed']}
        }
        
    def get_smart_recommendations(self, password: str, analysis: Dict, 
                                email: str = None, context: Dict = None) -> Dict[str, Any]:
        """Get comprehensive smart recommendations"""
        
        # Get ML-based predictions
        ml_recommendations = self.pattern_learner.predict_best_settings(password, analysis)
        
        # Get user behavior recommendations
        pattern_type = analysis.get('pattern_type', 'unknown')
        behavior_recommendations = self.behavior_tracker.get_personalized_recommendations(
            pattern_type, ml_recommendations['settings']
        )
        
        # Apply context-aware adjustments
        context_adjustments = self._get_context_adjustments(email, analysis, context)
        
        # Combine all recommendations
        final_settings = self._combine_recommendations(
            ml_recommendations['settings'],
            behavior_recommendations['settings'],
            context_adjustments['settings']
        )
        
        # Calculate confidence score
        confidence = self._calculate_combined_confidence(
            ml_recommendations['confidence_score'],
            behavior_recommendations['confidence'],
            context_adjustments['confidence']
        )
        
        # Generate adaptive intensity
        adaptive_intensity = self._determine_adaptive_intensity(
            analysis, final_settings, context
        )
        
        # Create comprehensive recommendation
        recommendation = {
            'settings': final_settings,
            'intensity': adaptive_intensity,
            'confidence': confidence,
            'reasoning': self._generate_comprehensive_reasoning(
                analysis, ml_recommendations, behavior_recommendations, 
                context_adjustments, email
            ),
            'effectiveness_prediction': self._predict_effectiveness(
                password, analysis, final_settings
            ),
            'alternative_approaches': self._suggest_alternatives(analysis, final_settings),
            'personalization_level': behavior_recommendations.get('personalization_applied', False)
        }
        
        return recommendation
        
    def _get_context_adjustments(self, email: str, analysis: Dict, 
                               context: Dict = None) -> Dict[str, Any]:
        """Get context-aware adjustments based on email domain and other factors"""
        adjustments = {
            'settings': {},
            'confidence': 0.7,
            'reasoning': []
        }
        
        if not email:
            return adjustments
            
        # Extract domain
        domain = email.split('@')[1].lower() if '@' in email else ''
        
        # Check for known domain patterns
        domain_config = None
        if domain in self.domain_patterns:
            domain_config = self.domain_patterns[domain]
        elif any(edu_domain in domain for edu_domain in ['.edu', 'university', 'college']):
            domain_config = self.domain_patterns['edu']
        elif any(corp_domain in domain for corp_domain in ['corp', 'company', '.org']):
            domain_config = self.domain_patterns['corporate']
        else:
            # Check for popular email providers
            for provider in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                if provider in domain:
                    domain_config = self.domain_patterns[provider]
                    break
                    
        if domain_config:
            if domain_config.get('conservative', False):
                # Conservative approach for consumer email providers
                adjustments['settings'].update({
                    'preserve_strong': True,
                    'character_substitution': analysis.get('strength_level') not in ['strong', 'very_strong']
                })
                adjustments['reasoning'].append(f"Conservative approach recommended for {domain}")
                
            # Adjust based on common patterns for this domain
            common_patterns = domain_config.get('common_patterns', [])
            if analysis.get('pattern_type') in common_patterns:
                adjustments['settings']['intelligent_patterns'] = True
                adjustments['reasoning'].append(f"Pattern '{analysis.get('pattern_type')}' is common for {domain}")
                
        # Context-specific adjustments
        if context:
            if context.get('high_security', False):
                adjustments['settings'].update({
                    'character_substitution': True,
                    'add_year': True,
                    'intelligent_patterns': True
                })
                adjustments['reasoning'].append("High security context detected")
                
            if context.get('batch_processing', False):
                adjustments['settings']['preserve_strong'] = True
                adjustments['reasoning'].append("Batch processing mode - being conservative")
                
        return adjustments
        
    def _combine_recommendations(self, ml_settings: Dict, behavior_settings: Dict, 
                               context_settings: Dict) -> Dict[str, Any]:
        """Combine recommendations from different sources with priority"""
        # Start with ML recommendations as base
        combined = ml_settings.copy()
        
        # Apply user behavior preferences (high priority)
        for key, value in behavior_settings.items():
            combined[key] = value
            
        # Apply context adjustments (highest priority)
        for key, value in context_settings.items():
            combined[key] = value
            
        return combined
        
    def _calculate_combined_confidence(self, ml_confidence: float, 
                                     behavior_confidence: float,
                                     context_confidence: float) -> float:
        """Calculate combined confidence score"""
        # Weighted average with behavior having highest weight
        weights = [0.3, 0.5, 0.2]  # ML, Behavior, Context
        confidences = [ml_confidence, behavior_confidence, context_confidence]
        
        combined = sum(w * c for w, c in zip(weights, confidences))
        return round(combined, 3)
        
    def _determine_adaptive_intensity(self, analysis: Dict, settings: Dict, 
                                    context: Dict = None) -> str:
        """Determine adaptive transformation intensity"""
        strength_level = analysis.get('strength_level', 'unknown')
        
        # Base intensity on current strength
        if strength_level == 'very_weak':
            base_intensity = 'aggressive'
        elif strength_level == 'weak':
            base_intensity = 'moderate'
        elif strength_level == 'moderate':
            base_intensity = 'light'
        else:  # strong or very_strong
            base_intensity = 'light'
            
        # Adjust based on settings
        if settings.get('preserve_strong', False) and strength_level in ['strong', 'very_strong']:
            return 'light'
            
        if (settings.get('character_substitution', False) and 
            settings.get('add_year', False) and 
            settings.get('intelligent_patterns', False)):
            # All aggressive settings enabled
            if base_intensity == 'light':
                return 'moderate'
            elif base_intensity == 'moderate':
                return 'aggressive'
                
        # Context adjustments
        if context and context.get('high_security', False):
            intensity_levels = ['light', 'moderate', 'aggressive']
            current_idx = intensity_levels.index(base_intensity)
            return intensity_levels[min(current_idx + 1, 2)]
            
        return base_intensity
        
    def _generate_comprehensive_reasoning(self, analysis: Dict, ml_rec: Dict,
                                        behavior_rec: Dict, context_adj: Dict,
                                        email: str = None) -> List[str]:
        """Generate comprehensive reasoning for recommendations"""
        reasoning = []
        
        # Start with basic analysis
        strength = analysis.get('strength_level', 'unknown')
        pattern = analysis.get('pattern_type', 'unknown')
        reasoning.append(f"Password strength: {strength}, Pattern: {pattern}")
        
        # Add ML insights
        ml_reasoning = ml_rec.get('reasoning', [])
        reasoning.extend(ml_reasoning)
        
        # Add behavior insights
        if behavior_rec.get('personalization_applied', False):
            adapted = behavior_rec.get('adapted_settings', [])
            reasoning.append(f"Personalized {len(adapted)} settings based on your preferences")
            
        # Add context insights
        context_reasoning = context_adj.get('reasoning', [])
        reasoning.extend(context_reasoning)
        
        # Add domain-specific insights
        if email and '@' in email:
            domain = email.split('@')[1]
            reasoning.append(f"Optimized for {domain} domain patterns")
            
        return reasoning
        
    def _predict_effectiveness(self, password: str, analysis: Dict, 
                             settings: Dict) -> Dict[str, Any]:
        """Predict the effectiveness of recommended settings"""
        
        # Base prediction on current strength and pattern type
        current_score = analysis.get('strength_score', 0)
        pattern_type = analysis.get('pattern_type', 'unknown')
        
        # Get historical success rates
        pattern_success = self.pattern_learner.success_rates.get(pattern_type, 0.6)
        
        # Estimate improvement based on settings
        improvement_factor = 1.0
        
        if settings.get('character_substitution', False):
            improvement_factor += 0.15
        if settings.get('add_year', False):
            improvement_factor += 0.10
        if settings.get('intelligent_patterns', False):
            improvement_factor += 0.20
        if settings.get('increment_numbers', False):
            improvement_factor += 0.05
            
        # Predict new strength score
        predicted_score = min(100, current_score * improvement_factor)
        predicted_improvement = predicted_score - current_score
        
        # Calculate success probability
        success_probability = pattern_success * 0.7 + improvement_factor * 0.3
        success_probability = min(0.95, success_probability)
        
        return {
            'current_strength_score': current_score,
            'predicted_strength_score': round(predicted_score, 1),
            'predicted_improvement': round(predicted_improvement, 1),
            'success_probability': round(success_probability, 3),
            'confidence_level': self._get_confidence_level(success_probability)
        }
        
    def _get_confidence_level(self, probability: float) -> str:
        """Convert probability to confidence level"""
        if probability >= 0.9:
            return "Very High"
        elif probability >= 0.75:
            return "High"
        elif probability >= 0.6:
            return "Moderate"
        elif probability >= 0.4:
            return "Low"
        else:
            return "Very Low"
            
    def _suggest_alternatives(self, analysis: Dict, settings: Dict) -> List[Dict[str, Any]]:
        """Suggest alternative approaches"""
        alternatives = []
        
        current_strength = analysis.get('strength_level', 'unknown')
        pattern_type = analysis.get('pattern_type', 'unknown')
        
        # Conservative alternative
        if not settings.get('preserve_strong', False):
            alternatives.append({
                'name': 'Conservative Approach',
                'description': 'Minimal changes, preserve existing structure',
                'settings': {**settings, 'preserve_strong': True, 'character_substitution': False},
                'pros': ['Maintains password familiarity', 'Lower risk of user confusion'],
                'cons': ['May result in smaller strength improvement']
            })
            
        # Aggressive alternative  
        if current_strength in ['very_weak', 'weak']:
            alternatives.append({
                'name': 'Aggressive Enhancement',
                'description': 'Maximum security improvements',
                'settings': {
                    **settings, 
                    'character_substitution': True,
                    'add_year': True,
                    'intelligent_patterns': True,
                    'increment_numbers': True
                },
                'pros': ['Maximum security improvement', 'Addresses all weaknesses'],
                'cons': ['May significantly change password structure']
            })
            
        # Pattern-specific alternative
        if pattern_type in ['word_with_numbers', 'alphabetic']:
            alternatives.append({
                'name': 'Pattern-Optimized',
                'description': f'Specialized approach for {pattern_type} patterns',
                'settings': {
                    **settings,
                    'intelligent_patterns': True,
                    'character_substitution': pattern_type == 'alphabetic'
                },
                'pros': ['Tailored to your password pattern', 'Balanced approach'],
                'cons': ['May not address all potential weaknesses']
            })
            
        return alternatives[:3]  # Return top 3 alternatives
        
    def learn_from_user_feedback(self, password: str, analysis: Dict, settings: Dict,
                               transformed_password: str, transformed_analysis: Dict,
                               user_rating: int, accepted: bool, email: str = None):
        """Learn from user feedback to improve future recommendations"""
        
        # Calculate success score based on rating and acceptance
        success_score = 0.5  # Base score
        if accepted:
            success_score += 0.3
        success_score += (user_rating / 10.0) * 0.2  # Rating contributes up to 0.2
        success_score = min(1.0, success_score)
        
        # Learn pattern
        self.pattern_learner.learn_transformation_pattern(
            password, transformed_password, analysis, transformed_analysis,
            settings, success_score
        )
        
        # Track behavior
        self.behavior_tracker.track_transformation_feedback(
            analysis.get('strength_level', 'unknown'),
            transformed_analysis.get('strength_level', 'unknown'),
            user_rating, accepted, analysis.get('pattern_type', 'unknown'),
            settings
        )
        
        # Save learning
        self.pattern_learner.save_models()
        
    def get_learning_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for analytics dashboard"""
        ml_insights = self.pattern_learner.get_learning_insights()
        behavior_analysis = self.behavior_tracker.get_behavior_analysis()
        
        # Combine insights
        dashboard_data = {
            'learning_overview': {
                'total_transformations': ml_insights.get('total_transformations', 0),
                'patterns_learned': ml_insights.get('patterns_learned', 0),
                'user_preferences_learned': behavior_analysis.get('total_preferences_learned', 0),
                'learning_quality': behavior_analysis.get('learning_quality', 'No data'),
                'last_updated': datetime.now().isoformat()
            },
            'effectiveness_metrics': {
                'average_improvement': ml_insights.get('average_strength_improvement', 0),
                'success_rate': ml_insights.get('average_success_rate', 0),
                'success_by_pattern': ml_insights.get('success_rates_by_pattern', {}),
                'user_satisfaction': behavior_analysis.get('success_rates_by_pattern', {})
            },
            'personalization_insights': {
                'confident_preferences': behavior_analysis.get('confident_preferences', 0),
                'average_confidence': behavior_analysis.get('average_preference_confidence', 0),
                'popular_settings': behavior_analysis.get('popular_settings', [])
            },
            'recommendations_quality': {
                'ml_model_trained': ml_insights.get('cluster_model_trained', False),
                'best_settings': ml_insights.get('best_performing_settings', []),
                'pattern_distribution': ml_insights.get('pattern_distribution', {})
            }
        }
        
        return dashboard_data
        
    def export_learning_data(self, file_path: str) -> bool:
        """Export learning data for backup or analysis"""
        try:
            dashboard_data = self.get_learning_dashboard_data()
            
            import json
            with open(file_path, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error exporting learning data: {e}")
            return False
            
    def import_learning_data(self, file_path: str) -> bool:
        """Import learning data (useful for migration)"""
        try:
            import json
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # This would require more complex logic to rebuild models
            # For now, just return success
            print(f"Learning data imported from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error importing learning data: {e}")
            return False