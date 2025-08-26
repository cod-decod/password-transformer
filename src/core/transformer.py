import random
import re
from datetime import datetime
from .strategies import TransformationStrategies

class PasswordTransformer:
    """Intelligent password transformation engine"""
    
    def __init__(self):
        self.strategies = TransformationStrategies()
        self.current_year = datetime.now().year
        
    def transform_password(self, password, analysis, settings):
        """Transform password based on analysis and settings"""
        if not password:
            return password
            
        # Determine transformation strategy based on strength level
        strength_level = analysis['strength_level']
        
        if settings.get('preserve_strong', True) and strength_level in ['very_strong']:
            return self._minimal_optimization(password, analysis, settings)
        elif strength_level in ['very_weak', 'weak']:
            return self._enhance_weak_password(password, analysis, settings)
        elif strength_level == 'moderate':
            return self._improve_moderate_password(password, analysis, settings)
        elif strength_level == 'strong':
            return self._optimize_strong_password(password, analysis, settings)
        else:
            return self._apply_default_transformation(password, settings)
            
    def _minimal_optimization(self, password, analysis, settings):
        """Minimal changes to very strong passwords"""
        transformed = password
        
        # Only update years if present and old
        if settings.get('add_year', True):
            year_match = re.search(r'(19|20)\d{2}', transformed)
            if year_match:
                old_year = int(year_match.group())
                if old_year < self.current_year - 1:  # Only if year is old
                    transformed = transformed.replace(str(old_year), str(self.current_year))
                    
        return transformed
            
    def _enhance_weak_password(self, password, analysis, settings):
        """Significantly enhance weak passwords"""
        transformed = password
        
        # Apply intelligent pattern-based enhancement
        if settings.get('intelligent_patterns', True):
            transformed = self.strategies.apply_intelligent_enhancement(transformed, analysis)
            
        # Character substitution for weak passwords
        if settings.get('character_substitution', True):
            intensity = settings.get('intensity', 'moderate')
            if intensity in ['moderate', 'aggressive']:
                transformed = self.strategies.apply_character_substitution(transformed, intensity)
                
        # Add missing complexity elements
        if not analysis['has_uppercase']:
            transformed = self._add_uppercase(transformed)
            
        # Add numbers strategically
        if not analysis['has_digits']:
            if settings.get('add_year', True):
                if settings.get('intensity', 'moderate') == 'aggressive':
                    transformed += str(self.current_year)
                else:
                    transformed += str(self.current_year)[-2:]  # Just last 2 digits
            else:
                transformed += str(random.randint(10, 99))
                
        # Add special characters
        if not analysis['has_special'] and settings.get('intensity', 'moderate') != 'conservative':
            special_chars = ['!', '@', '#', '$', '%']
            if settings.get('intensity', 'moderate') == 'aggressive':
                transformed += random.choice(special_chars)
            else:
                transformed += '!'  # Most common choice
                
        return transformed
        
    def _improve_moderate_password(self, password, analysis, settings):
        """Improve moderate strength passwords"""
        transformed = password
        
        # Apply intelligent improvements
        if settings.get('intelligent_patterns', True):
            transformed = self.strategies.apply_pattern_improvements(transformed, analysis)
            
        # Selective character substitution
        if settings.get('character_substitution', True):
            intensity = settings.get('intensity', 'moderate')
            if intensity == 'aggressive':
                transformed = self.strategies.apply_selective_substitution(transformed)
                
        # Smart number incrementing
        if settings.get('increment_numbers', True):
            transformed = self.strategies.increment_numbers(transformed)
            
        # Add year if beneficial and not present
        if settings.get('add_year', True) and not re.search(r'\d{4}', transformed):
            if settings.get('intensity', 'moderate') in ['moderate', 'aggressive']:
                if len(transformed) < 12:  # Only if password isn't too long
                    transformed += str(self.current_year)
                    
        return transformed
        
    def _optimize_strong_password(self, password, analysis, settings):
        """Light optimization for strong passwords"""
        transformed = password
        
        # Apply light optimizations
        if settings.get('intelligent_patterns', True):
            transformed = self.strategies.apply_light_optimization(transformed, analysis)
            
        # Conservative improvements only
        intensity = settings.get('intensity', 'moderate')
        if intensity == 'conservative':
            # Only increment numbers if present
            if settings.get('increment_numbers', True):
                transformed = self.strategies.increment_numbers(transformed)
        elif intensity in ['moderate', 'aggressive']:
            # Update year if present and old
            if settings.get('add_year', True):
                year_match = re.search(r'(19|20)\d{2}', transformed)
                if year_match:
                    old_year = int(year_match.group())
                    if old_year < self.current_year:
                        transformed = transformed.replace(str(old_year), str(self.current_year))
                        
        return transformed
        
    def _apply_default_transformation(self, password, settings):
        """Apply default transformation when strength is unclear"""
        transformed = password
        
        # Basic improvements
        if settings.get('character_substitution', True):
            transformed = self.strategies.apply_basic_substitution(transformed)
            
        # Add year if requested
        if settings.get('add_year', True) and not re.search(r'\d{4}', transformed):
            transformed += str(self.current_year)
            
        # Ensure uppercase
        if not re.search(r'[A-Z]', transformed):
            transformed = self._add_uppercase(transformed)
            
        return transformed
        
    def _add_uppercase(self, password):
        """Add uppercase letter intelligently"""
        if not password:
            return password
            
        # Strategy 1: Capitalize first letter if it's alphabetic
        if password[0].isalpha() and password[0].islower():
            return password[0].upper() + password[1:]
            
        # Strategy 2: Find first lowercase letter and capitalize it
        for i, char in enumerate(password):
            if char.isalpha() and char.islower():
                return password[:i] + char.upper() + password[i+1:]
                
        # Strategy 3: If no lowercase letters, just return as is
        return password
        
    def get_transformation_summary(self, original, transformed, analysis):
        """Get summary of what transformations were applied"""
        changes = []
        
        if original != transformed:
            if len(transformed) > len(original):
                changes.append(f"Length increased: {len(original)} → {len(transformed)}")
                
            # Check for character substitutions
            subs_found = []
            substitutions = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
            for orig, sub in substitutions.items():
                if orig in original.lower() and sub in transformed:
                    subs_found.append(f"{orig}→{sub}")
            if subs_found:
                changes.append(f"Character substitutions: {', '.join(subs_found)}")
                
            # Check for case changes
            if not re.search(r'[A-Z]', original) and re.search(r'[A-Z]', transformed):
                changes.append("Added uppercase letters")
                
            # Check for added numbers
            orig_digits = len(re.findall(r'\d', original))
            new_digits = len(re.findall(r'\d', transformed))
            if new_digits > orig_digits:
                changes.append(f"Added {new_digits - orig_digits} digits")
                
            # Check for added special characters
            orig_special = len(re.findall(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]', original))
            new_special = len(re.findall(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]', transformed))
            if new_special > orig_special:
                changes.append(f"Added {new_special - orig_special} special characters")
                
        return changes if changes else ["No changes applied"]
