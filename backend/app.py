from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from supabase import create_client, Client
import os
import jwt
import datetime
from functools import wraps
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from dotenv import load_dotenv
import requests
import re

# ------------------ Configure logging first ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ Load environment variables from .env ------------------
load_dotenv()

# ------------------ DEBUG: Check if .env variables loaded ------------------
logger.info(f"SUPABASE_URL: {os.environ.get('SUPABASE_URL')}")
logger.info(f"SUPABASE_SERVICE_KEY: {'SET' if os.environ.get('SUPABASE_SERVICE_KEY') else 'NOT SET'}")
logger.info(f"SUPABASE_ANON_KEY: {'SET' if os.environ.get('SUPABASE_ANON_KEY') else 'NOT SET'}")
logger.info(f"JWT_SECRET: {'SET' if os.environ.get('JWT_SECRET') else 'NOT SET'}")
logger.info(f"SECRET_KEY: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")

# ------------------ Google OAuth Configuration ------------------
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/google/callback')

# Log Google OAuth configuration
logger.info(f"GOOGLE_CLIENT_ID: {'SET' if GOOGLE_CLIENT_ID else 'NOT SET'}")
logger.info(f"GOOGLE_CLIENT_SECRET: {'SET' if GOOGLE_CLIENT_SECRET else 'NOT SET'}")


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize CORS
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:8000",
    "https://farmlinkk.netlify.app",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:8000"
])

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')  # Use service role key for server-side
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')  # optional, for frontend simulation

# Validate environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY not set in .env")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

# Database table names
TABLES = {
    'users': 'users',
    'posts': 'marketplace_posts',
    'chats': 'user_chats',
    'messages': 'chat_messages',
    'profiles': 'user_profiles'
}

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-jwt-secret-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def generate_jwt_token(user_id, user_type):
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ------------------ Google OAuth Helper Functions ------------------

def get_google_auth_url(user_type):
    """Generate Google OAuth authorization URL"""
    if not GOOGLE_CLIENT_ID:
        return None
        
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'state': f"user_type:{user_type}"
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
    
    return f"{auth_url}?{query_string}"

def exchange_google_code_for_tokens(authorization_code):
    """Exchange authorization code for access and refresh tokens"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return None
        
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': GOOGLE_REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Google token exchange failed: {e}")
        return None

def get_google_user_info(access_token):
    """Get user information from Google using access token"""
    userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to get Google user info: {e}")
        return None

def authenticate_google_user(google_user_info, user_type):
    """Authenticate or create user from Google OAuth"""
    try:
        # Check if user already exists
        existing_user = supabase.table(TABLES['users']).select('*').eq('email', google_user_info['email']).execute()
        
        if existing_user.data:
            # User exists, return user data
            user = existing_user.data[0]
            logger.info(f"Existing user logged in via Google: {user['email']}")
            return {
                'user': user,
                'is_new_user': False
            }
        else:
            # Create new user
            new_user_data = {
                'name': google_user_info.get('name', google_user_info.get('given_name', '')),
                'email': google_user_info['email'],
                'google_id': google_user_info['id'],
                'user_type': user_type,
                'mobile': '',  # Will be filled later
                'password_hash': '',  # No password for OAuth users
                'created_at': datetime.datetime.utcnow().isoformat(),
                'updated_at': datetime.datetime.utcnow().isoformat()
            }
            
            # Insert user
            result = supabase.table(TABLES['users']).insert(new_user_data).execute()
            
            if result.data:
                user = result.data[0]
                logger.info(f"New user created via Google OAuth: {user['email']}")
                return {
                    'user': user,
                    'is_new_user': True
                }
            else:
                logger.error("Failed to create new user via Google OAuth")
                return None
                
    except Exception as e:
        logger.error(f"Error in Google OAuth authentication: {e}")
        return None

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user_id = payload['user_id']
        request.user_type = payload['user_type']
        return f(*args, **kwargs)
    return decorated_function

# ------------------ Authentication Routes ------------------

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required_fields = ['username', 'email', 'password', 'user_type', 'contact']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        existing_user = supabase.table(TABLES['users']).select('id').eq('email', data['email']).execute()
        if existing_user.data:
            return jsonify({'error': 'User with this email already exists'}), 409
        # Check if mobile already exists (unique constraint)
        existing_mobile = supabase.table(TABLES['users']).select('id').eq('mobile', data['contact']).execute()
        if existing_mobile.data:
            return jsonify({'error': 'User with this contact number already exists'}), 409
        
        hashed_password = generate_password_hash(data['password'])
        
        user_data = {
            'id': str(uuid.uuid4()),
            'name': data['username'],
            'email': data['email'],
            'password_hash': hashed_password,
            'user_type': data['user_type'],
            'mobile': data['contact'],
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        result = supabase.table(TABLES['users']).insert(user_data).execute()
        
        if result.data:
            token = generate_jwt_token(user_data['id'], data['user_type'])
            return jsonify({
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'id': user_data['id'],
                    'username': user_data['name'],
                    'email': user_data['email'],
                    'user_type': data['user_type'],
                    'contact': data['contact']
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        # Attempt to map Supabase unique constraint error to 409
        try:
            err = str(e)
            if 'duplicate key value' in err and 'users_mobile_key' in err:
                logger.error(f"Registration error: {e}")
                return jsonify({'error': 'User with this contact number already exists'}), 409
            if 'duplicate key value' in err and 'users_email_key' in err:
                logger.error(f"Registration error: {e}")
                return jsonify({'error': 'User with this email already exists'}), 409
        except Exception:
            pass
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        result = supabase.table(TABLES['users']).select('*').eq('email', data['email']).execute()
        if not result.data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = result.data[0]
        if not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_jwt_token(user['id'], user['user_type'])
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['name'],
                'email': user['email'],
                'user_type': user['user_type'],
                'contact': user['mobile']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ------------------ User Info Route ------------------

@app.route('/api/users/<user_id>', methods=['GET'])
@require_auth
def get_user_info(user_id):
    """Get user information by ID"""
    try:
        # Only allow users to get their own info
        if request.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        result = supabase.table(TABLES['users']).select('id, name, email, user_type, mobile, created_at').eq('id', user_id).execute()
        
        if result.data:
            user = result.data[0]
            return jsonify({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'user_type': user['user_type'],
                'mobile': user['mobile'],
                'created_at': user['created_at']
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Public minimal user info (safe fields only)
@app.route('/api/users/<user_id>/public', methods=['GET'])
def get_user_public(user_id):
    """Return non-sensitive info for displaying on post cards (no auth required)."""
    try:
        # Limit fields to safe subset
        result = supabase.table(TABLES['users']).select('id, name, user_type').eq('id', user_id).limit(1).execute()
        if result.data:
            user = result.data[0]
            return jsonify({'id': user['id'], 'name': user.get('name', 'User'), 'user_type': user.get('user_type', '')}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Get public user info error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ------------------ Google OAuth Routes ------------------

@app.route('/api/auth/google/url', methods=['POST'])
def get_google_auth_url_route():
    """Get Google OAuth authorization URL"""
    try:
        data = request.get_json()
        user_type = data.get('user_type', 'farmer')
        
        if not user_type or user_type not in ['farmer', 'buyer']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        auth_url = get_google_auth_url(user_type)
        if auth_url:
            return jsonify({'auth_url': auth_url}), 200
        else:
            return jsonify({'error': 'Google OAuth not configured'}), 500
            
    except Exception as e:
        logger.error(f"Google OAuth URL error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/google/callback', methods=['GET'])
def google_oauth_callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code and state from query parameters
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({'error': 'Authorization code not provided'}), 400
        
        # Extract user type from state
        user_type = 'farmer'  # default
        if state and 'user_type:' in state:
            user_type = state.split('user_type:')[1]
        
        # Exchange code for tokens
        tokens = exchange_google_code_for_tokens(code)
        if not tokens:
            return jsonify({'error': 'Failed to exchange authorization code'}), 500
        
        # Get user information
        user_info = get_google_user_info(tokens['access_token'])
        if not user_info:
            return jsonify({'error': 'Failed to get user information'}), 500
        
        # Authenticate or create user
        auth_result = authenticate_google_user(user_info, user_type)
        if not auth_result:
            return jsonify({'error': 'Authentication failed'}), 500
        
        user = auth_result['user']
        is_new_user = auth_result['is_new_user']
        
        # Generate JWT token
        token = generate_jwt_token(user['id'], user['user_type'])
        
        # Redirect directly to the appropriate page with token and user info
        if user['user_type'] == 'farmer':
            redirect_url = f"http://localhost:8000/farmer.html?token={token}&is_new_user={is_new_user}&user_id={user['id']}&user_type={user['user_type']}"
        else:
            redirect_url = f"http://localhost:8000/buyer.html?token={token}&is_new_user={is_new_user}&user_id={user['id']}&user_type={user['user_type']}"
        
        return redirect(redirect_url)
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ------------------ Marketplace Routes ------------------

@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        user_type = request.args.get('user_type')
        location = request.args.get('location')
        search = request.args.get('search')
        author_id = request.args.get('author_id')
        
        query = supabase.table(TABLES['posts']).select('*').order('created_at', desc=True)
        
        if user_type:
            query = query.eq('user_type', user_type)
        if author_id:
            query = query.eq('author_id', author_id)
        if location:
            query = query.ilike('location', f'%{location}%')
        if search:
            query = query.or_(f"crop_name.ilike.%{search}%,crop_details.ilike.%{search}%,requirements.ilike.%{search}%,organization.ilike.%{search}%")
        
        result = query.execute()
        return jsonify({'posts': result.data, 'count': len(result.data)}), 200
        
    except Exception as e:
        logger.error(f"Get posts error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/posts', methods=['POST'])
@require_auth
def create_post():
    try:
        data = request.get_json()
        if request.user_type == 'farmer':
            required_fields = ['crop_name', 'crop_details', 'quantity', 'location']
        else:
            required_fields = ['name', 'organization', 'requirements', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        post_data = {
            'id': str(uuid.uuid4()),
            'user_type': request.user_type,
            'author_id': request.user_id,
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        if request.user_type == 'farmer':
            post_data.update({
                'crop_name': data['crop_name'],
                'crop_details': data['crop_details'],
                'quantity': data['quantity'],
                'location': data['location']
            })
        else:
            post_data.update({
                'name': data['name'],
                'organization': data['organization'],
                'requirements': data['requirements'],
                'location': data['location']
            })
        
        result = supabase.table(TABLES['posts']).insert(post_data).execute()
        if result.data:
            return jsonify({'message': 'Post created successfully', 'post': result.data[0]}), 201
        else:
            return jsonify({'error': 'Failed to create post'}), 500
        
    except Exception as e:
        logger.error(f"Create post error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Update a marketplace post
@app.route('/api/posts/<post_id>', methods=['PUT'])
@require_auth
def update_post(post_id):
    try:
        # Fetch the existing post
        existing = supabase.table(TABLES['posts']).select('*').eq('id', post_id).limit(1).execute()
        if not existing.data:
            return jsonify({'error': 'Post not found'}), 404
        post = existing.data[0]

        # Only the author can update
        if post.get('author_id') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json() or {}

        # Build allowed update fields based on post.user_type
        update_fields = {'location', 'price', 'unit', 'status'}
        if post.get('user_type') == 'farmer':
            update_fields.update({'crop_name', 'crop_details', 'quantity'})
        else:
            update_fields.update({'name', 'organization', 'requirements'})

        update_payload = {k: v for k, v in data.items() if k in update_fields and v is not None}
        if not update_payload:
            return jsonify({'error': 'No valid fields to update'}), 400

        update_payload['updated_at'] = datetime.datetime.utcnow().isoformat()

        result = supabase.table(TABLES['posts']).update(update_payload).eq('id', post_id).execute()
        if result.data:
            return jsonify({'message': 'Post updated successfully', 'post': result.data[0]}), 200
        else:
            return jsonify({'error': 'Failed to update post'}), 500
    except Exception as e:
        logger.error(f"Update post error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Delete a marketplace post
@app.route('/api/posts/<post_id>', methods=['DELETE'])
@require_auth
def delete_post(post_id):
    try:
        # Fetch the existing post
        existing = supabase.table(TABLES['posts']).select('id, author_id').eq('id', post_id).limit(1).execute()
        if not existing.data:
            return jsonify({'error': 'Post not found'}), 404
        post = existing.data[0]

        # Only the author can delete
        if post.get('author_id') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        result = supabase.table(TABLES['posts']).delete().eq('id', post_id).execute()
        if result.data is not None:
            return jsonify({'message': 'Post deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete post'}), 500
    except Exception as e:
        logger.error(f"Delete post error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ------------------ Chat Routes ------------------

@app.route('/api/chats', methods=['GET'])
@require_auth
def get_user_chats():
    try:
        result = supabase.table(TABLES['chats']).select('*').or_(f"user1_id.eq.{request.user_id},user2_id.eq.{request.user_id}").order('created_at', desc=True).execute()
        chats_with_details = []
        for chat in result.data:
            other_user_id = chat['user1_id'] if chat['user2_id'] == request.user_id else chat['user2_id']
            # Try to get name from users table first (more reliable)
            other_user_res = supabase.table(TABLES['users']).select('id, name, user_type').eq('id', other_user_id).limit(1).execute()
            other_user_profile = other_user_res.data[0] if other_user_res.data else {}
            message_result = supabase.table(TABLES['messages']).select('*').eq('chat_id', chat['id']).order('created_at', desc=True).limit(1).execute()
            last_message = message_result.data[0] if message_result.data else None
            chats_with_details.append({
                'chat_id': chat['id'],
                'other_user': {
                    'id': other_user_id,
                    'name': other_user_profile.get('name', 'Unknown'),
                    'user_type': other_user_profile.get('user_type', 'Unknown')
                },
                'last_message': last_message,
                'created_at': chat['created_at']
            })
        return jsonify({'chats': chats_with_details, 'count': len(chats_with_details)}), 200
    except Exception as e:
        logger.error(f"Get user chats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chats', methods=['POST'])
@require_auth
def create_or_get_chat():
    try:
        current_user_id = request.user_id
        data = request.get_json()
        other_user_id = data.get('other_user_id')

        if not other_user_id:
            return jsonify({'error': 'Missing other_user_id'}), 400

        # Check for existing chat in either direction
        chat_query = supabase.table(TABLES['chats']).select('*').or_(f'user1_id.eq.{current_user_id},user2_id.eq.{other_user_id}').or_(f'user1_id.eq.{other_user_id},user2_id.eq.{current_user_id}').limit(1).execute()
        
        if chat_query.data:
            return jsonify({'chat': chat_query.data[0]}), 200

        # Create new chat
        new_chat = {
            'id': str(uuid.uuid4()),
            'user1_id': current_user_id,
            'user2_id': other_user_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        insert_result = supabase.table(TABLES['chats']).insert(new_chat).execute()
        return jsonify({'chat': insert_result.data[0]}), 201

    except Exception as e:
        logger.error(f"Chat creation error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/chats/<chat_id>/messages', methods=['GET'])
@require_auth
def get_chat_messages(chat_id):
    try:
        chat_res = supabase.table(TABLES['chats']).select('id, user1_id, user2_id').eq('id', chat_id).limit(1).execute()
        if not chat_res.data:
            return jsonify({'error': 'Chat not found'}), 404
        chat = chat_res.data[0]
        if chat['user1_id'] != request.user_id and chat['user2_id'] != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        msgs = supabase.table(TABLES['messages']).select('*').eq('chat_id', chat_id).order('created_at', desc=False).execute()
        return jsonify({'messages': msgs.data or []}), 200
    except Exception as e:
        logger.error(f"Get chat messages error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
@app.route('/api/chats/<chat_id>/messages', methods=['POST'])
@require_auth
def send_message(chat_id):
    try:
        data = request.get_json()
        message_text = data.get('message')
        if not message_text:
            return jsonify({'error': 'Message text is required'}), 400
        
        chat_result = supabase.table(TABLES['chats']).select('*').eq('id', chat_id).execute()
        if not chat_result.data:
            return jsonify({'error': 'Chat not found'}), 404
        chat = chat_result.data[0]
        if chat['user1_id'] != request.user_id and chat['user2_id'] != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        message_data = {
            'id': str(uuid.uuid4()),
            'chat_id': chat_id,
            'sender_id': request.user_id,
            'message': message_text,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        result = supabase.table(TABLES['messages']).insert(message_data).execute()
        if result.data:
            return jsonify({'message': 'Message sent successfully', 'message_data': result.data[0]}), 201
        else:
            return jsonify({'error': 'Failed to send message'}), 500
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ------------------ Profile Routes ------------------

@app.route('/api/profile', methods=['GET'])
@require_auth
def get_profile():
    try:
        result = supabase.table(TABLES['profiles']).select('*').eq('user_id', request.user_id).execute()
        if result.data:
            return jsonify({'profile': result.data[0]}), 200
        else:
            return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# ------------------ Health Check ------------------

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        if supabase:
            supabase.table(TABLES['users']).select('id').limit(1).execute()
            return jsonify({'status': 'healthy', 'database': 'connected', 'timestamp': datetime.datetime.utcnow().isoformat()}), 200
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'timestamp': datetime.datetime.utcnow().isoformat()}), 503
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'error', 'error': str(e), 'timestamp': datetime.datetime.utcnow().isoformat()}), 503

# ------------------ Run Flask ------------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    logger.info(f"Starting FarmLink backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
