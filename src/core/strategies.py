import re
import random
from datetime import datetime

class TransformationStrategies:
    """Advanced password transformation strategies"""
    
    def __init__(self):
        self.char_substitutions = {
            'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'], 's': ['$', '5'],
            'l': ['1'], 't': ['7'], 'g': ['9'], 'b': ['6'], 'z': ['2']
        }
        
        self.common_patterns = {
            'password': ['P@ssw0rd', 'Passw0rd!', 'P4ssw0rd'],
            'admin': ['Adm1n', '@dmin', 'Admin123'],
            'user': ['Us3r', 'User!', 'U$er'],
            'qwerty': ['Qw3rty', 'Qwerty!', 'QW3RTY'],
            'welcome': ['W3lcome', 'Welcome!', 'W3lc0me!'],
            'hello': ['H3llo', 'Hello!', 'H3ll0!'],
            'letmein': ['L3tme1n', 'LetMe1n!', 'L3tm31n']
        }
        
    def apply_intelligent_enhancement(self, password, analysis):
        """Apply intelligent enhancement based on password analysis"""
        enhanced = password
        
        # Handle common passwords with smart replacements
        if analysis['is_common']:
            enhanced = self._transform_common_password(enhanced)
            
        # Handle different pattern types
        pattern_type = analysis['pattern_type']
        
        if pattern_type == 'word_with_numbers':
            enhanced = self._enhance_word_with_numbers(enhanced)
        elif pattern_type == 'numeric':
            enhanced = self._enhance_numeric_password(enhanced)
        elif pattern_type == 'alphabetic':
            enhanced = self._enhance_alphabetic_password(enhanced)
        elif pattern_type == 'keyboard_pattern':
            enhanced = self._transform_keyboard_pattern(enhanced)
            
        return enhanced
        
    def apply_pattern_improvements(self, password, analysis):
        """Apply pattern-based improvements for moderate passwords"""
        improved = password
        
        # Increment sequential numbers intelligently
        improved = self.increment_numbers(improved)
        
        # Add strategic special characters if missing
        if not analysis['has_special']:
            improved = self._add_strategic_special_chars(improved)
            
        # Fix common weaknesses
        if analysis['has_repeated_chars']:
            improved = self._fix_repeated_characters(improved)
            
        return improved
        
    def apply_light_optimization(self, password, analysis):
        """Apply light optimizations for strong passwords"""
        optimized = password
        
        # Only make minimal changes
        if re.search(r'\d+', optimized):
            # Light number incrementing
            optimized = self._light_number_increment(optimized)
            
        # Update old years only
        year_match = re.search(r'(19|20)\d{2}', optimized)
        if year_match:
            old_year = int(year_match.group())
            current_year = datetime.now().year
            if old_year < current_year - 1:  # Only if year is more than 1 year old
                optimized = optimized.replace(str(old_year), str(current_year))
                
        return optimized
        
    def apply_character_substitution(self, password, intensity='moderate'):
        """Apply character substitution with varying intensity"""
        substituted = list(password.lower())
        
        # Determine how aggressive to be
        if intensity == 'conservative':
            max_subs = 1
            sub_chance = 0.3
        elif intensity == 'moderate':
            max_subs = len(password) // 4
            sub_chance = 0.5
        else:  # aggressive
            max_subs = len(password) // 2
            sub_chance = 0.7
            
        substitution_count = 0
        
        for i, char in enumerate(substituted):
            if char in self.char_substitutions and substitution_count < max_subs:
                if random.random() < sub_chance:
                    # Preserve original case for some characters
                    original_was_upper = password[i].isupper()
                    new_char = random.choice(self.char_substitutions[char])
                    
                    # Some substitutions can be uppercase
                    if original_was_upper and new_char.isalpha():
                        new_char = new_char.upper()
                        
                    substituted[i] = new_char
                    substitution_count += 1
                    
        return ''.join(substituted)
        
    def apply_selective_substitution(self, password):
        """Apply selective character substitution (1-2 chars max)"""
        substitutable_positions = [
            i for i, c in enumerate(password.lower()) 
            if c in self.char_substitutions
        ]
        
        if not substitutable_positions:
            return password
            
        # Select 1-2 positions to substitute
        num_to_substitute = min(2, len(substitutable_positions))
        positions = random.sample(substitutable_positions, num_to_substitute)
        
        result = list(password)
        for pos in positions:
            char = password[pos].lower()
            if char in self.char_substitutions:
                new_char = random.choice(self.char_substitutions[char])
                # Preserve case if original was uppercase
                if password[pos].isupper() and new_char.isalpha():
                    new_char = new_char.upper()
                result[pos] = new_char
                
        return ''.join(result)
        
    def apply_basic_substitution(self, password):
        """Apply basic character substitution (minimal changes)"""
        basic_subs = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
        
        # Only substitute the first occurrence of one character
        for original, replacement in basic_subs.items():
            if original in password.lower():
                # Find first occurrence
                for i, char in enumerate(password):
                    if char.lower() == original:
                        return password[:i] + replacement + password[i+1:]
                        
        return password
        
    def increment_numbers(self, password):
        """Intelligently increment numbers in password"""
        # Find all number sequences
        number_matches = list(re.finditer(r'\d+', password))
        
        if not number_matches:
            return password
            
        result = password
        # Work backwards to avoid index shifting
        for match in reversed(number_matches):
            number = int(match.group())
            start, end = match.span()
            
            # Smart increment logic
            new_number = self._smart_increment(number)
            
            # Preserve leading zeros if present
            original_str = match.group()
            if original_str.startswith('0') and len(original_str) > 1:
                new_str = str(new_number).zfill(len(original_str))
            else:
                new_str = str(new_number)
                
            result = result[:start] + new_str + result[end:]
            
        return result
        
    def _smart_increment(self, number):
        """Smart number incrementing logic"""
        current_year = datetime.now().year
        
        if number == 0:
            return 1
        elif 1900 <= number <= 2030:  # Likely a year
            return current_year
        elif number < 10:
            return (number + 1) % 10 if number == 9 else number + 1
        elif number < 100:
            return number + 1 if number < 99 else number + 10
        elif number == 123:
            return 124
        elif str(number) == str(number)[::-1]:  # Palindrome like 121, 131
            return number + 10
        else:
            return number + 1
            
    def _light_number_increment(self, password):
        """Light number incrementing (only small numbers)"""
        result = password
        
        # Only increment single digits and small numbers
        for match in reversed(list(re.finditer(r'\d{1,2}', password))):
            number = int(match.group())
            if number < 50:  # Only increment small numbers
                new_number = number + 1 if number < 99 else number
                result = result[:match.start()] + str(new_number) + result[match.end():]
                
        return result
        
    def _transform_common_password(self, password):
        """Transform common passwords intelligently"""
        lower_pass = password.lower()
        
        if lower_pass in self.common_patterns:
            # Choose a random transformation from available options
            return random.choice(self.common_patterns[lower_pass])
            
        # Generic transformations for other common passwords
        generic_transforms = [
            lambda p: p.capitalize() + '123!',
            lambda p: p.upper()[:3] + p.lower()[3:] + '2024',
            lambda p: p.replace('a', '@').replace('o', '0') + '!',
            lambda p: p.title() + str(datetime.now().year)
        ]
        
        return random.choice(generic_transforms)(password)
        
    def _enhance_word_with_numbers(self, password):
        """Enhance passwords that are words with numbers"""
        # Pattern: letters followed by numbers
        match = re.match(r'([a-zA-Z]+)(\d+)$', password)
        if match:
            word_part, num_part = match.groups()
            
            # Enhance the word part
            enhanced_word = word_part.capitalize()
            if 'a' in word_part.lower():
                enhanced_word = enhanced_word.replace('a', '@', 1)
                
            # Increment the number
            enhanced_num = str(int(num_part) + 1)
            
            # Add special character
            return enhanced_word + enhanced_num + '!'
            
        return password
        
    def _enhance_numeric_password(self, password):
        """Enhance purely numeric passwords"""
        # Convert to a word-number combination
        if len(password) <= 6:
            return 'Pass' + password + '!'
        else:
            # For longer numeric passwords, add letters at strategic points
            mid_point = len(password) // 2
            return password[:mid_point] + 'Pass' + password[mid_point:] + '!'
            
    def _enhance_alphabetic_password(self, password):
        """Enhance purely alphabetic passwords"""
        enhanced = password.capitalize()
        
        # Add some character substitutions
        enhanced = enhanced.replace('a', '@', 1).replace('o', '0', 1)
        
        # Add year and special character
        enhanced += str(datetime.now().year) + '!'
        
        return enhanced
        
    def _transform_keyboard_pattern(self, password):
        """Transform keyboard patterns into stronger passwords"""
        transformations = {
            'qwerty': 'Qw3rty!',
            'asdf': '@sdf123',
            'zxcv': 'Zxcv2024!',
            '1234': 'Pass1234!',
            '12345': 'Secure12345'
        }
        
        lower_pass = password.lower()
        for pattern, replacement in transformations.items():
            if pattern in lower_pass:
                return replacement
                
        # Generic keyboard pattern transformation
        return password.capitalize() + '2024!'
        
    def _add_strategic_special_chars(self, password):
        """Add special characters strategically"""
        special_chars = ['!', '@', '#', '$', '%', '&', '*']
        
        # Most common user behavior: add at the end
        if random.random() < 0.8:
            return password + random.choice(['!', '@', '#'])
        else:
            # Less common: replace a character or add in middle
            if len(password) > 4:
                pos = random.randint(1, len(password) - 2)
                return password[:pos] + random.choice(special_chars) + password[pos+1:]
            else:
                return password + '!'
                
    def _fix_repeated_characters(self, password):
        """Fix repeated characters while maintaining readability"""
        result = password
        
        # Find repeated sequences (3+ same characters)
        i = 0
        while i < len(result) - 2:
            if result[i] == result[i+1] == result[i+2]:
                # Replace the middle character with something similar
                char = result[i]
                if char.isdigit():
                    replacement = str((int(char) + 1) % 10)
                elif char.lower() in self.char_substitutions:
                    replacement = self.char_substitutions[char.lower()][0]
                else:
                    replacement = char.upper() if char.islower() else char.lower()
                    
                result = result[:i+1] + replacement + result[i+2:]
                i += 3
            else:
                i += 1
                
        return result
