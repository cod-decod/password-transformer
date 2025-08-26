"""
Analytics Module
Provides statistics, insights, and visualizations for password transformation analytics
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
from .pattern_learner import PatternLearner
from .behavior_tracker import BehaviorTracker


class Analytics:
    """Analytics and visualization for password transformation insights"""
    
    def __init__(self, model_dir: str = "data/models", db_path: str = "data/behavior.db"):
        self.pattern_learner = PatternLearner(model_dir)
        self.behavior_tracker = BehaviorTracker(db_path)
        
        # Set style for plots
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
    def generate_transformation_report(self) -> Dict[str, Any]:
        """Generate comprehensive transformation analytics report"""
        
        # Get base data
        ml_insights = self.pattern_learner.get_learning_insights()
        behavior_data = self.behavior_tracker.get_behavior_analysis()
        
        # Calculate trends
        trends = self._calculate_trends()
        
        # Pattern effectiveness analysis
        pattern_effectiveness = self._analyze_pattern_effectiveness()
        
        # Setting performance analysis
        setting_performance = self._analyze_setting_performance()
        
        report = {
            'summary': {
                'total_transformations': ml_insights.get('total_transformations', 0),
                'unique_patterns': ml_insights.get('patterns_learned', 0),
                'average_improvement': ml_insights.get('average_strength_improvement', 0),
                'overall_success_rate': ml_insights.get('average_success_rate', 0),
                'report_generated': datetime.now().isoformat()
            },
            'trends': trends,
            'pattern_effectiveness': pattern_effectiveness,
            'setting_performance': setting_performance,
            'user_behavior': behavior_data,
            'recommendations': self._generate_optimization_recommendations(
                pattern_effectiveness, setting_performance
            )
        }
        
        return report
        
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trend data over time"""
        history = self.pattern_learner.transformation_history
        
        if not history:
            return {'trend': 'No data available'}
            
        # Group by time periods
        daily_stats = {}
        for record in history:
            try:
                timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                date_key = timestamp.date().isoformat()
                
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        'count': 0,
                        'avg_improvement': 0,
                        'avg_success': 0,
                        'improvements': [],
                        'successes': []
                    }
                    
                daily_stats[date_key]['count'] += 1
                daily_stats[date_key]['improvements'].append(
                    record.get('strength_improvement', 0)
                )
                daily_stats[date_key]['successes'].append(
                    record.get('success_score', 0.5)
                )
                
            except Exception:
                continue
                
        # Calculate averages
        for date_key in daily_stats:
            stats = daily_stats[date_key]
            stats['avg_improvement'] = np.mean(stats['improvements'])
            stats['avg_success'] = np.mean(stats['successes'])
            
        # Analyze trends
        if len(daily_stats) > 1:
            dates = sorted(daily_stats.keys())
            recent_avg = np.mean([daily_stats[d]['avg_improvement'] for d in dates[-7:]])
            older_avg = np.mean([daily_stats[d]['avg_improvement'] for d in dates[:-7]])
            
            trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            trend = "insufficient data"
            
        return {
            'trend': trend,
            'daily_stats': daily_stats,
            'total_days': len(daily_stats)
        }
        
    def _analyze_pattern_effectiveness(self) -> Dict[str, Any]:
        """Analyze effectiveness of different password patterns"""
        ml_insights = self.pattern_learner.get_learning_insights()
        success_rates = ml_insights.get('success_rates_by_pattern', {})
        pattern_distribution = ml_insights.get('pattern_distribution', {})
        
        effectiveness = {}
        
        for pattern_type in pattern_distribution:
            count = pattern_distribution[pattern_type]
            success_rate = success_rates.get(pattern_type, 0.5)
            
            # Calculate average improvement for this pattern
            avg_improvement = 0
            improvements = []
            
            for record in self.pattern_learner.transformation_history:
                if record.get('pattern_type') == pattern_type:
                    improvements.append(record.get('strength_improvement', 0))
                    
            if improvements:
                avg_improvement = np.mean(improvements)
                std_improvement = np.std(improvements)
            else:
                avg_improvement = 0
                std_improvement = 0
                
            effectiveness[pattern_type] = {
                'count': count,
                'success_rate': success_rate,
                'average_improvement': round(avg_improvement, 2),
                'improvement_consistency': round(1 - (std_improvement / max(abs(avg_improvement), 1)), 2),
                'overall_score': round((success_rate * 0.5 + (avg_improvement / 50) * 0.3 + 
                                     (count / max(pattern_distribution.values())) * 0.2), 2)
            }
            
        return effectiveness
        
    def _analyze_setting_performance(self) -> Dict[str, Any]:
        """Analyze performance of different settings combinations"""
        setting_performance = {}
        
        # Analyze each setting individually
        settings_to_analyze = [
            'character_substitution', 'add_year', 'intelligent_patterns',
            'preserve_strong', 'increment_numbers'
        ]
        
        for setting in settings_to_analyze:
            true_improvements = []
            false_improvements = []
            
            for record in self.pattern_learner.transformation_history:
                settings_used = record.get('settings_used', {})
                improvement = record.get('strength_improvement', 0)
                
                if settings_used.get(setting) is True:
                    true_improvements.append(improvement)
                elif settings_used.get(setting) is False:
                    false_improvements.append(improvement)
                    
            setting_performance[setting] = {
                'enabled_avg': round(np.mean(true_improvements), 2) if true_improvements else 0,
                'disabled_avg': round(np.mean(false_improvements), 2) if false_improvements else 0,
                'enabled_count': len(true_improvements),
                'disabled_count': len(false_improvements),
                'effectiveness_ratio': (
                    (np.mean(true_improvements) / max(np.mean(false_improvements), 0.1))
                    if true_improvements and false_improvements else 1.0
                )
            }
            
        return setting_performance
        
    def _generate_optimization_recommendations(self, pattern_effectiveness: Dict,
                                             setting_performance: Dict) -> List[str]:
        """Generate optimization recommendations based on analytics"""
        recommendations = []
        
        # Pattern-based recommendations
        if pattern_effectiveness:
            best_patterns = sorted(pattern_effectiveness.items(), 
                                 key=lambda x: x[1]['overall_score'], reverse=True)
            
            if best_patterns:
                best_pattern = best_patterns[0]
                recommendations.append(
                    f"'{best_pattern[0]}' patterns show best results "
                    f"(success rate: {best_pattern[1]['success_rate']:.1%})"
                )
                
            worst_patterns = [p for p in best_patterns if p[1]['overall_score'] < 0.5]
            if worst_patterns:
                recommendations.append(
                    f"Consider improving handling of {len(worst_patterns)} pattern types "
                    "with below-average performance"
                )
                
        # Setting-based recommendations
        for setting, perf in setting_performance.items():
            if perf['effectiveness_ratio'] > 1.5:
                recommendations.append(
                    f"Enable '{setting}' more often - shows {perf['effectiveness_ratio']:.1f}x "
                    "better improvement when enabled"
                )
            elif perf['effectiveness_ratio'] < 0.7:
                recommendations.append(
                    f"Consider reducing use of '{setting}' - shows better results when disabled"
                )
                
        # General recommendations
        total_transformations = len(self.pattern_learner.transformation_history)
        if total_transformations < 50:
            recommendations.append(
                "Collect more transformation data to improve ML accuracy "
                f"(current: {total_transformations}, recommended: 50+)"
            )
            
        return recommendations[:5]  # Top 5 recommendations
        
    def create_visualizations(self, output_dir: str = "data/analytics") -> Dict[str, str]:
        """Create visualization plots and save them"""
        os.makedirs(output_dir, exist_ok=True)
        created_plots = {}
        
        try:
            # 1. Pattern effectiveness chart
            pattern_plot = self._create_pattern_effectiveness_plot(output_dir)
            if pattern_plot:
                created_plots['pattern_effectiveness'] = pattern_plot
                
            # 2. Improvement trends over time
            trends_plot = self._create_trends_plot(output_dir)
            if trends_plot:
                created_plots['improvement_trends'] = trends_plot
                
            # 3. Setting performance comparison
            settings_plot = self._create_settings_performance_plot(output_dir)
            if settings_plot:
                created_plots['settings_performance'] = settings_plot
                
            # 4. Success rate distribution
            success_plot = self._create_success_distribution_plot(output_dir)
            if success_plot:
                created_plots['success_distribution'] = success_plot
                
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            
        return created_plots
        
    def _create_pattern_effectiveness_plot(self, output_dir: str) -> Optional[str]:
        """Create pattern effectiveness visualization"""
        try:
            pattern_effectiveness = self._analyze_pattern_effectiveness()
            
            if not pattern_effectiveness:
                return None
                
            patterns = list(pattern_effectiveness.keys())
            success_rates = [pattern_effectiveness[p]['success_rate'] for p in patterns]
            improvements = [pattern_effectiveness[p]['average_improvement'] for p in patterns]
            counts = [pattern_effectiveness[p]['count'] for p in patterns]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Success rates bar chart
            bars1 = ax1.bar(patterns, success_rates, color='skyblue', alpha=0.7)
            ax1.set_title('Success Rate by Pattern Type')
            ax1.set_ylabel('Success Rate')
            ax1.set_xticklabels(patterns, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, value in zip(bars1, success_rates):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{value:.2f}', ha='center', va='bottom')
                        
            # Average improvement scatter plot
            scatter = ax2.scatter(improvements, success_rates, s=[c*20 for c in counts], 
                                alpha=0.6, c=range(len(patterns)), cmap='viridis')
            ax2.set_xlabel('Average Strength Improvement')
            ax2.set_ylabel('Success Rate')
            ax2.set_title('Pattern Performance: Improvement vs Success Rate')
            
            # Add pattern labels
            for i, pattern in enumerate(patterns):
                ax2.annotate(pattern, (improvements[i], success_rates[i]),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
                           
            plt.tight_layout()
            plot_path = os.path.join(output_dir, 'pattern_effectiveness.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return plot_path
            
        except Exception as e:
            print(f"Error creating pattern effectiveness plot: {e}")
            return None
            
    def _create_trends_plot(self, output_dir: str) -> Optional[str]:
        """Create trends over time plot"""
        try:
            trends = self._calculate_trends()
            daily_stats = trends.get('daily_stats', {})
            
            if not daily_stats:
                return None
                
            dates = sorted(daily_stats.keys())
            improvements = [daily_stats[d]['avg_improvement'] for d in dates]
            successes = [daily_stats[d]['avg_success'] for d in dates]
            counts = [daily_stats[d]['count'] for d in dates]
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
            
            # Improvement trends
            ax1.plot(dates, improvements, marker='o', color='lightgreen', linewidth=2)
            ax1.set_title('Average Strength Improvement Over Time')
            ax1.set_ylabel('Avg Improvement')
            ax1.grid(True, alpha=0.3)
            
            # Success rate trends
            ax2.plot(dates, successes, marker='s', color='orange', linewidth=2)
            ax2.set_title('Success Rate Over Time')
            ax2.set_ylabel('Success Rate')
            ax2.grid(True, alpha=0.3)
            
            # Activity volume
            ax3.bar(dates, counts, color='lightblue', alpha=0.7)
            ax3.set_title('Daily Transformation Count')
            ax3.set_ylabel('Count')
            ax3.set_xlabel('Date')
            
            # Rotate x-axis labels for better readability
            for ax in [ax1, ax2, ax3]:
                ax.tick_params(axis='x', rotation=45)
                
            plt.tight_layout()
            plot_path = os.path.join(output_dir, 'improvement_trends.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return plot_path
            
        except Exception as e:
            print(f"Error creating trends plot: {e}")
            return None
            
    def _create_settings_performance_plot(self, output_dir: str) -> Optional[str]:
        """Create settings performance comparison plot"""
        try:
            setting_performance = self._analyze_setting_performance()
            
            if not setting_performance:
                return None
                
            settings = list(setting_performance.keys())
            enabled_avgs = [setting_performance[s]['enabled_avg'] for s in settings]
            disabled_avgs = [setting_performance[s]['disabled_avg'] for s in settings]
            
            x = np.arange(len(settings))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            bars1 = ax.bar(x - width/2, enabled_avgs, width, label='Enabled', alpha=0.8)
            bars2 = ax.bar(x + width/2, disabled_avgs, width, label='Disabled', alpha=0.8)
            
            ax.set_xlabel('Settings')
            ax.set_ylabel('Average Strength Improvement')
            ax.set_title('Setting Performance: Enabled vs Disabled')
            ax.set_xticks(x)
            ax.set_xticklabels([s.replace('_', ' ').title() for s in settings], rotation=45, ha='right')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height,
                           f'{height:.1f}', ha='center', va='bottom')
                           
            plt.tight_layout()
            plot_path = os.path.join(output_dir, 'settings_performance.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return plot_path
            
        except Exception as e:
            print(f"Error creating settings performance plot: {e}")
            return None
            
    def _create_success_distribution_plot(self, output_dir: str) -> Optional[str]:
        """Create success rate distribution plot"""
        try:
            history = self.pattern_learner.transformation_history
            
            if not history:
                return None
                
            success_scores = [record.get('success_score', 0.5) for record in history]
            improvements = [record.get('strength_improvement', 0) for record in history]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Success score histogram
            ax1.hist(success_scores, bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
            ax1.set_title('Distribution of Success Scores')
            ax1.set_xlabel('Success Score')
            ax1.set_ylabel('Frequency')
            ax1.axvline(np.mean(success_scores), color='red', linestyle='--', 
                       label=f'Mean: {np.mean(success_scores):.2f}')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Improvement histogram
            ax2.hist(improvements, bins=20, alpha=0.7, color='lightsteelblue', edgecolor='black')
            ax2.set_title('Distribution of Strength Improvements')
            ax2.set_xlabel('Strength Improvement')
            ax2.set_ylabel('Frequency')
            ax2.axvline(np.mean(improvements), color='blue', linestyle='--',
                       label=f'Mean: {np.mean(improvements):.1f}')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plot_path = os.path.join(output_dir, 'success_distribution.png')
            plt.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return plot_path
            
        except Exception as e:
            print(f"Error creating success distribution plot: {e}")
            return None
            
    def export_analytics_data(self, file_path: str) -> bool:
        """Export analytics data to CSV for external analysis"""
        try:
            # Prepare data for export
            data_rows = []
            
            for record in self.pattern_learner.transformation_history:
                row = {
                    'timestamp': record.get('timestamp', ''),
                    'pattern_type': record.get('pattern_type', ''),
                    'strength_improvement': record.get('strength_improvement', 0),
                    'success_score': record.get('success_score', 0.5),
                    'settings_used': str(record.get('settings_used', {}))
                }
                
                # Add individual settings as columns
                settings = record.get('settings_used', {})
                for setting, value in settings.items():
                    row[f'setting_{setting}'] = value
                    
                data_rows.append(row)
                
            if data_rows:
                df = pd.DataFrame(data_rows)
                df.to_csv(file_path, index=False)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error exporting analytics data: {e}")
            return False
            
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary data for dashboard display"""
        ml_insights = self.pattern_learner.get_learning_insights()
        behavior_data = self.behavior_tracker.get_behavior_analysis()
        
        # Calculate some additional metrics
        history = self.pattern_learner.transformation_history
        recent_history = [r for r in history 
                         if datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) 
                         > datetime.now() - timedelta(days=7)]
        
        return {
            'overview': {
                'total_transformations': len(history),
                'recent_transformations': len(recent_history),
                'unique_patterns': ml_insights.get('patterns_learned', 0),
                'avg_improvement': ml_insights.get('average_strength_improvement', 0),
                'success_rate': ml_insights.get('average_success_rate', 0)
            },
            'recent_activity': {
                'transformations_last_7_days': len(recent_history),
                'avg_improvement_recent': (np.mean([r.get('strength_improvement', 0) 
                                                  for r in recent_history]) 
                                         if recent_history else 0),
                'patterns_this_week': len(set(r.get('pattern_type', 'unknown') 
                                            for r in recent_history))
            },
            'learning_status': {
                'model_trained': ml_insights.get('cluster_model_trained', False),
                'preferences_learned': behavior_data.get('total_preferences_learned', 0),
                'learning_quality': behavior_data.get('learning_quality', 'No data')
            }
        }