import csv
import os
from typing import List, Tuple

class FileHandler:
    """Handle file I/O operations for password files"""
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
    def load_file(self, file_path: str) -> List[Tuple[str, str]]:
        """Load email:password pairs from text file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Try different encodings
        for encoding in self.supported_encodings:
            try:
                return self._load_with_encoding(file_path, encoding)
            except UnicodeDecodeError:
                continue
                
        raise ValueError("Unable to decode file with any supported encoding")
        
    def _load_with_encoding(self, file_path: str, encoding: str) -> List[Tuple[str, str]]:
        """Load file with specific encoding"""
        data = []
        line_number = 0
        
        with open(file_path, 'r', encoding=encoding) as file:
            for line in file:
                line_number += 1
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Parse email:password format
                if ':' not in line:
                    raise ValueError(
                        f"Invalid format on line {line_number}: '{line[:50]}...'\n"
                        f"Expected format: 'email:password'"
                    )
                    
                # Split only on first colon to handle passwords with colons
                colon_pos = line.find(':')
                email = line[:colon_pos].strip()
                password = line[colon_pos + 1:].strip()
                
                # Validation
                if not email:
                    raise ValueError(f"Empty email on line {line_number}")
                if not password:
                    raise ValueError(f"Empty password on line {line_number}")
                    
                # Basic email format validation
                if '@' not in email or '.' not in email:
                    print(f"Warning: Email format may be invalid on line {line_number}: {email}")
                    
                data.append((email, password))
                
        if not data:
            raise ValueError("No valid email:password pairs found in file")
            
        return data
        
    def save_file(self, file_path: str, data: List[Tuple[str, str]]):
        """Save email:password pairs to text file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                # Add header comment
                file.write(f"# Password Transformer Output\n")
                file.write(f"# Generated: {self._get_timestamp()}\n")
                file.write(f"# Total entries: {len(data)}\n")
                file.write(f"# Format: email:password\n\n")
                
                # Write data
                for email, password in data:
                    file.write(f"{email}:{password}\n")
                    
        except Exception as e:
            raise ValueError(f"Error saving file: {str(e)}")
            
    def save_csv(self, file_path: str, data: List[Tuple[str, str]]):
        """Save data to CSV file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow(['Email', 'Password'])
                
                # Write data
                writer.writerows(data)
                
        except Exception as e:
            raise ValueError(f"Error saving CSV file: {str(e)}")
            
    def validate_file_format(self, file_path: str) -> dict:
        """Validate file format and return statistics"""
        try:
            data = self.load_file(file_path)
            
            # Calculate statistics
            email_domains = {}
            password_lengths = []
            char_types = {'digits': 0, 'uppercase': 0, 'lowercase': 0, 'special': 0}
            
            for email, password in data:
                # Email domain analysis
                domain = email.split('@')[1] if '@' in email else 'unknown'
                email_domains[domain] = email_domains.get(domain, 0) + 1
                
                # Password analysis
                password_lengths.append(len(password))
                if any(c.isdigit() for c in password):
                    char_types['digits'] += 1
                if any(c.isupper() for c in password):
                    char_types['uppercase'] += 1
                if any(c.islower() for c in password):
                    char_types['lowercase'] += 1
                if any(not c.isalnum() for c in password):
                    char_types['special'] += 1
            
            stats = {
                'total_entries': len(data),
                'unique_emails': len(set(email for email, _ in data)),
                'unique_passwords': len(set(password for _, password in data)),
                'avg_password_length': round(sum(password_lengths) / len(password_lengths), 1),
                'min_password_length': min(password_lengths),
                'max_password_length': max(password_lengths),
                'top_domains': sorted(email_domains.items(), key=lambda x: x[1], reverse=True)[:5],
                'password_characteristics': char_types
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
            
    def create_backup(self, original_path: str) -> str:
        """Create a backup of the original file"""
        if not os.path.exists(original_path):
            raise FileNotFoundError(f"Original file not found: {original_path}")
            
        # Generate backup filename
        base_name = os.path.splitext(original_path)[0]
        extension = os.path.splitext(original_path)[1]
        timestamp = self._get_timestamp().replace(':', '-').replace(' ', '_')
        backup_path = f"{base_name}_backup_{timestamp}{extension}"
        
        # Copy file
        import shutil
        shutil.copy2(original_path, backup_path)
        
        return backup_path
        
    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
