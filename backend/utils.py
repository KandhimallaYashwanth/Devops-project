import jwt
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash

def generate_jwt_token(user_id: str, user_type: str, secret_key: str, expiration_hours: int = 24) -> str:
    """Generate JWT token for user authentication"""
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_jwt_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password: str) -> str:
    """Hash a password using Werkzeug's security functions"""
    return generate_password_hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return check_password_hash(hashed_password, password)

def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format (10 digits)"""
    phone_pattern = r'^[0-9]{10}$'
    return re.match(phone_pattern, phone) is not None

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength and return detailed feedback"""
    feedback = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    if len(password) < 8:
        feedback['valid'] = False
        feedback['errors'].append('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        feedback['warnings'].append('Consider adding uppercase letters')
    
    if not re.search(r'[a-z]', password):
        feedback['warnings'].append('Consider adding lowercase letters')
    
    if not re.search(r'[0-9]', password):
        feedback['warnings'].append('Consider adding numbers')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        feedback['warnings'].append('Consider adding special characters')
    
    return feedback

def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def validate_post_data(data: Dict[str, Any], user_type: str) -> Dict[str, Any]:
    """Validate marketplace post data"""
    errors = []
    warnings = []
    
    if user_type == 'farmer':
        required_fields = ['crop_name', 'crop_details', 'quantity', 'location']
        field_names = {
            'crop_name': 'Crop Name',
            'crop_details': 'Crop Details',
            'quantity': 'Quantity',
            'location': 'Location'
        }
    else:  # buyer
        required_fields = ['name', 'organization', 'requirements', 'location']
        field_names = {
            'name': 'Organization Name',
            'organization': 'Organization Type',
            'requirements': 'Requirements',
            'location': 'Location'
        }
    
    # Check required fields
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field_names[field]} is required")
        elif isinstance(data[field], str) and len(data[field].strip()) == 0:
            errors.append(f"{field_names[field]} cannot be empty")
    
    # Validate specific fields
    if 'location' in data and data['location']:
        if len(data['location'].strip()) < 3:
            warnings.append('Location should be more specific')
    
    if 'quantity' in data and data['quantity']:
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                errors.append('Quantity must be a positive number')
        except ValueError:
            errors.append('Quantity must be a valid number')
    
    if 'requirements' in data and data['requirements']:
        if len(data['requirements'].strip()) < 10:
            warnings.append('Requirements should be more detailed')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.utcnow()
        diff = now - dt.replace(tzinfo=None)
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    except:
        return timestamp

def create_error_response(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        'error': True,
        'message': message,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return response

def create_success_response(message: str, data: Optional[Dict[str, Any]] = None, status_code: int = 200) -> Dict[str, Any]:
    """Create standardized success response"""
    response = {
        'error': False,
        'message': message,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data:
        response['data'] = data
    
    return response

def paginate_results(results: list, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Paginate a list of results"""
    total = len(results)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_results = results[start_idx:end_idx]
    
    return {
        'results': paginated_results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_next': end_idx < total,
            'has_prev': page > 1
        }
    }

def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user registration/login data"""
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['username', 'email', 'password', 'user_type', 'contact']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field.title()} is required")
    
    # Email validation
    if 'email' in data and data['email']:
        if not validate_email(data['email']):
            errors.append('Invalid email format')
    
    # Phone validation
    if 'contact' in data and data['contact']:
        if not validate_phone(data['contact']):
            errors.append('Phone number must be 10 digits')
    
    # Password validation
    if 'password' in data and data['password']:
        password_feedback = validate_password_strength(data['password'])
        if not password_feedback['valid']:
            errors.extend(password_feedback['errors'])
        warnings.extend(password_feedback['warnings'])
    
    # Username validation
    if 'username' in data and data['username']:
        username = data['username'].strip()
        if len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        if len(username) > 50:
            errors.append('Username must be less than 50 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores')
    
    # User type validation
    if 'user_type' in data and data['user_type']:
        valid_types = ['farmer', 'buyer']
        if data['user_type'] not in valid_types:
            errors.append('User type must be either "farmer" or "buyer"')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

