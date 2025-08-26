import re
import math
from collections import Counter
import string

class PasswordAnalyzer:
    """Intelligent password analysis engine"""
    
    def __init__(self):
        self.common_passwords = self._load_common_passwords()
        self.keyboard_patterns = self._load_keyboard_patterns()
        
    def _load_common_passwords(self):
        """Load common passwords database"""
        return {
            'password', '123456', 'password123', 'admin', 'qwerty', 'letmein',
            'welcome', 'monkey', '1234567890', 'abc123', 'password1', 'user',
            'login', 'master', 'hello', 'guest', 'administrator', 'root',
            '12345', 'qwerty123', 'Password1', 'superman', 'michael', 'jesus',
            'ninja', 'mustang', 'access', 'shadow', 'master', 'jennifer',
            'jordan', 'hunter', 'fuckyou', 'trustno1', 'ranger', 'buster'
        }
        
    def _load_keyboard_patterns(self):
        """Load keyboard pattern sequences"""
        return {
            'qwerty': 'qwertyuiopasdfghjklzxcvbnm',
            'numbers': '1234567890',
            'alphabet': 'abcdefghijklmnopqrstuvwxyz'
        }
        
    def analyze_password(self, password):
        """Comprehensive password analysis"""
        if not password:
            return self._empty_analysis()
            
        analysis = {
            'length': len(password),
            'has_digits': bool(re.search(r'\d', password)),
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]', password)),
            'digit_count': len(re.findall(r'\d', password)),
            'uppercase_count': len(re.findall(r'[A-Z]', password)),
            'lowercase_count': len(re.findall(r'[a-z]', password)),
            'special_count': len(re.findall(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]', password))
        }
        
        # Advanced analysis
        analysis.update({
            'entropy': self._calculate_entropy(password),
            'is_common': self._check_common_password(password),
            'has_keyboard_pattern': self._check_keyboard_patterns(password),
            'has_repeated_chars': self._check_repeated_characters(password),
            'has_sequential': self._check_sequential_patterns(password),
            'character_diversity': self._calculate_character_diversity(password),
            'pattern_type': self._identify_pattern_type(password),
            'has_dictionary_word': self._check_dictionary_words(password),
            'complexity_score': self._calculate_complexity_score(password)
        })
        
        # Calculate overall strength score
        analysis['strength_score'] = self._calculate_strength_score(analysis)
        analysis['strength_level'] = self._get_strength_level(analysis['strength_score'])
        
        return analysis
        
    def _empty_analysis(self):
        """Return empty analysis for empty passwords"""
        return {
            'length': 0, 'has_digits': False, 'has_uppercase': False,
            'has_lowercase': False, 'has_special': False, 'digit_count': 0,
            'uppercase_count': 0, 'lowercase_count': 0, 'special_count': 0,
            'entropy': 0, 'is_common': True, 'has_keyboard_pattern': False,
            'has_repeated_chars': False, 'has_sequential': False,
            'character_diversity': 0, 'pattern_type': 'empty',
            'has_dictionary_word': False, 'complexity_score': 0,
            'strength_score': 0, 'strength_level': 'very_weak'
        }
        
    def _calculate_entropy(self, password):
        """Calculate password entropy"""
        if not password:
            return 0
            
        # Character space estimation
        charset_size = 0
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]', password):
            charset_size += 32
            
        if charset_size == 0:
            return 0
            
        # Calculate entropy
        entropy = len(password) * math.log2(charset_size)
        return round(entropy, 2)
        
    def _check_common_password(self, password):
        """Check if password is in common passwords list"""
        return password.lower() in self.common_passwords
        
    def _check_keyboard_patterns(self, password):
        """Check for keyboard patterns"""
        password_lower = password.lower()
        
        patterns_to_check = [
            'qwerty', 'qwertyui', 'asdf', 'asdfgh', 'zxcv', 'zxcvbn',
            '1234', '12345', '123456', '1234567890'
        ]
        
        for pattern in patterns_to_check:
            if pattern in password_lower or pattern[::-1] in password_lower:
                return True
                
        return False
        
    def _check_repeated_characters(self, password):
        """Check for repeated characters (3+ in a row)"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
        
    def _check_sequential_patterns(self, password):
        """Check for sequential patterns"""
        # Check for sequential numbers
        for i in range(len(password) - 2):
            try:
                if (password[i:i+3].isdigit() and 
                    int(password[i+1]) == int(password[i]) + 1 and
                    int(password[i+2]) == int(password[i+1]) + 1):
                    return True
            except ValueError:
                pass
                
        # Check for sequential letters
        password_lower = password.lower()
        for i in range(len(password_lower) - 2):
            try:
                if (ord(password_lower[i+1]) == ord(password_lower[i]) + 1 and
                    ord(password_lower[i+2]) == ord(password_lower[i+1]) + 1):
                    return True
            except:
                pass
                
        return False
        
    def _calculate_character_diversity(self, password):
        """Calculate character diversity ratio"""
        if not password:
            return 0
        return len(set(password)) / len(password)
        
    def _identify_pattern_type(self, password):
        """Identify the primary pattern type"""
        if not password:
            return "empty"
        elif self._check_common_password(password):
            return "common"
        elif password.isdigit():
            return "numeric"
        elif password.isalpha():
            return "alphabetic"
        elif re.match(r'^[a-zA-Z]+\d+$', password):
            return "word_with_numbers"
        elif re.match(r'^\d+[a-zA-Z]+$', password):
            return "numbers_with_word"
        elif self._check_keyboard_patterns(password):
            return "keyboard_pattern"
        elif re.match(r'^[a-zA-Z]+[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]+$', password):
            return "word_with_symbols"
        else:
            return "mixed"
            
    def _check_dictionary_words(self, password):
        """Check for common dictionary words"""
        common_words = {
            'password', 'admin', 'user', 'guest', 'login', 'welcome', 'hello',
            'world', 'love', 'money', 'home', 'time', 'people', 'water',
            'day', 'man', 'woman', 'child', 'life', 'work', 'school', 'year'
        }
        
        password_lower = password.lower()
        for word in common_words:
            if word in password_lower:
                return True
        return False
        
    def _calculate_complexity_score(self, password):
        """Calculate complexity score based on character types and length"""
        score = 0
        
        # Length bonus
        score += min(len(password) * 4, 25)
        
        # Character type bonuses
        if re.search(r'[a-z]', password):
            score += 2
        if re.search(r'[A-Z]', password):
            score += 2  
        if re.search(r'\d', password):
            score += 4
        if re.search(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]', password):
            score += 6
            
        # Middle number/symbol bonus
        middle_chars = password[1:-1] if len(password) > 2 else ""
        score += len(re.findall(r'\d', middle_chars)) * 2
        score += len(re.findall(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;\'\/~`]', middle_chars)) * 2
        
        return min(score, 100)
        
    def _calculate_strength_score(self, analysis):
        """Calculate overall password strength score (0-100)"""
        score = 0
        
        # Base score from complexity
        score += analysis['complexity_score'] * 0.4
        
        # Length scoring (0-20 points)
        length_score = min(analysis['length'] * 2.5, 20)
        score += length_score
        
        # Character variety bonus (0-20 points)
        variety_score = 0
        if analysis['has_lowercase']:
            variety_score += 5
        if analysis['has_uppercase']:
            variety_score += 5
        if analysis['has_digits']:
            variety_score += 5
        if analysis['has_special']:
            variety_score += 5
        score += variety_score
        
        # Entropy bonus (0-15 points)
        entropy_score = min(analysis['entropy'] / 4, 15)
        score += entropy_score
        
        # Character diversity bonus (0-10 points)
        diversity_score = analysis['character_diversity'] * 10
        score += diversity_score
        
        # Apply penalties
        penalties = 0
        if analysis['is_common']:
            penalties += 30
        if analysis['has_keyboard_pattern']:
            penalties += 15
        if analysis['has_repeated_chars']:
            penalties += 10
        if analysis['has_sequential']:
            penalties += 10
        if analysis['has_dictionary_word']:
            penalties += 10
        if analysis['length'] < 8:
            penalties += 15
            
        # Apply penalties
        score -= penalties
        
        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        return round(score, 1)
        
    def _get_strength_level(self, score):
        """Convert score to strength level"""
        if score >= 80:
            return "very_strong"
        elif score >= 60:
            return "strong"
        elif score >= 40:
            return "moderate"
        elif score >= 20:
            return "weak"
        else:
            return "very_weak"
