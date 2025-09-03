from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Initialize CORS
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:8000",
    "https://farmlinkk.netlify.app",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:8000"
])

# In-memory storage for demo purposes
users_db = {}
posts_db = {}
chats_db = {}
messages_db = {}

# Helper functions
def generate_jwt_token(user_id, user_type):
    """Generate a simple token (in production, use proper JWT)"""
    return f"demo_token_{user_id}_{user_type}_{datetime.datetime.now().timestamp()}"

def verify_token(token):
    """Verify demo token"""
    try:
        parts = token.split('_')
        if len(parts) >= 4 and parts[0] == 'demo' and parts[1] == 'token':
            return {'user_id': parts[2], 'user_type': parts[3]}
    except:
        pass
    return None

def get_user_from_token():
    """Get user info from token in request headers"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    return verify_token(token)

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'user_type', 'contact']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        if data['email'] in [user['email'] for user in users_db.values()]:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create user
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'username': data['username'],
            'email': data['email'],
            'password_hash': generate_password_hash(data['password']),
            'user_type': data['user_type'],
            'contact': data['contact'],
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        users_db[user_id] = user_data
        
        # Generate token
        token = generate_jwt_token(user_id, data['user_type'])
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'username': data['username'],
                'email': data['email'],
                'user_type': data['user_type'],
                'contact': data['contact']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = None
        for u in users_db.values():
            if u['email'] == data['email']:
                user = u
                break
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_jwt_token(user['id'], user['user_type'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'user_type': user['user_type'],
                'contact': user['contact']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Marketplace Routes
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get marketplace posts with optional filtering"""
    try:
        user_type = request.args.get('user_type')
        location = request.args.get('location')
        search = request.args.get('search')
        
        posts = list(posts_db.values())
        
        # Apply filters
        if user_type:
            posts = [p for p in posts if p['user_type'] == user_type]
        
        if location:
            posts = [p for p in posts if location.lower() in p['location'].lower()]
        
        if search:
            search_lower = search.lower()
            posts = [p for p in posts if (
                (p.get('crop_name', '').lower().find(search_lower) != -1) or
                (p.get('crop_details', '').lower().find(search_lower) != -1) or
                (p.get('requirements', '').lower().find(search_lower) != -1) or
                (p.get('organization', '').lower().find(search_lower) != -1)
            )]
        
        # Sort by creation date
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'posts': posts,
            'count': len(posts)
        }), 200
        
    except Exception as e:
        logger.error(f"Get posts error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new marketplace post"""
    try:
        # Check authentication
        user_info = get_user_from_token()
        if not user_info:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields based on user type
        if user_info['user_type'] == 'farmer':
            required_fields = ['crop_name', 'crop_details', 'quantity', 'location']
        else:  # buyer
            required_fields = ['name', 'organization', 'requirements', 'location']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        post_data = {
            'id': str(uuid.uuid4()),
            'user_type': user_info['user_type'],
            'author_id': user_info['user_id'],
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        # Add fields based on user type
        if user_info['user_type'] == 'farmer':
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
        
        posts_db[post_data['id']] = post_data
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post_data
        }), 201
        
    except Exception as e:
        logger.error(f"Create post error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Chat Routes
@app.route('/api/chats', methods=['GET'])
def get_user_chats():
    """Get all chats for the authenticated user"""
    try:
        # Check authentication
        user_info = get_user_from_token()
        if not user_info:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_chats = []
        
        for chat_id, chat in chats_db.items():
            if chat['user1_id'] == user_info['user_id'] or chat['user2_id'] == user_info['user_id']:
                other_user_id = chat['user1_id'] if chat['user2_id'] == user_info['user_id'] else chat['user2_id']
                
                # Get other user info
                other_user = users_db.get(other_user_id, {})
                
                # Get last message
                last_message = None
                for msg in messages_db.values():
                    if msg['chat_id'] == chat_id:
                        if not last_message or msg['created_at'] > last_message['created_at']:
                            last_message = msg
                
                chat_detail = {
                    'chat_id': chat_id,
                    'other_user': {
                        'id': other_user_id,
                        'name': other_user.get('username', 'Unknown'),
                        'user_type': other_user.get('user_type', 'Unknown')
                    },
                    'last_message': last_message,
                    'created_at': chat['created_at']
                }
                user_chats.append(chat_detail)
        
        return jsonify({
            'chats': user_chats,
            'count': len(user_chats)
        }), 200
        
    except Exception as e:
        logger.error(f"Get user chats error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chats/<chat_id>/messages', methods=['POST'])
def send_message(chat_id):
    """Send a message in a chat"""
    try:
        # Check authentication
        user_info = get_user_from_token()
        if not user_info:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        message_text = data.get('message')
        
        if not message_text:
            return jsonify({'error': 'Message text is required'}), 400
        
        # Verify the user is a participant in this chat
        chat = chats_db.get(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        if chat['user1_id'] != user_info['user_id'] and chat['user2_id'] != user_info['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Create message
        message_data = {
            'id': str(uuid.uuid4()),
            'chat_id': chat_id,
            'sender_id': user_info['user_id'],
            'message': message_text,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        messages_db[message_data['id']] = message_data
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_data': message_data
        }), 201
        
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Profile Routes
@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        # Check authentication
        user_info = get_user_from_token()
        if not user_info:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = users_db.get(user_info['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile = {
            'id': str(uuid.uuid4()),
            'user_id': user['id'],
            'name': user['username'],
            'email': user['email'],
            'contact': user['contact'],
            'user_type': user['user_type'],
            'created_at': user['created_at']
        }
        
        return jsonify({
            'profile': profile
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Health Check
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'in-memory (demo mode)',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'message': 'Backend running in demo mode without external database'
    }), 200

# Demo data endpoint
@app.route('/api/demo/setup', methods=['POST'])
def setup_demo_data():
    """Setup demo data for testing"""
    try:
        # Create demo users
        farmer_id = str(uuid.uuid4())
        buyer_id = str(uuid.uuid4())
        
        users_db[farmer_id] = {
            'id': farmer_id,
            'username': 'Demo Farmer',
            'email': 'farmer@demo.com',
            'password_hash': generate_password_hash('demo123'),
            'user_type': 'farmer',
            'contact': '9876543210',
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        users_db[buyer_id] = {
            'id': buyer_id,
            'username': 'Demo Buyer',
            'email': 'buyer@demo.com',
            'password_hash': generate_password_hash('demo123'),
            'user_type': 'buyer',
            'contact': '9876543211',
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        # Create demo posts
        farmer_post_id = str(uuid.uuid4())
        buyer_post_id = str(uuid.uuid4())
        
        posts_db[farmer_post_id] = {
            'id': farmer_post_id,
            'user_type': 'farmer',
            'author_id': farmer_id,
            'crop_name': 'Organic Tomatoes',
            'crop_details': 'Fresh organic tomatoes, pesticide-free, harvested yesterday',
            'quantity': '50 kg',
            'location': 'Mumbai, Maharashtra',
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        posts_db[buyer_post_id] = {
            'id': buyer_post_id,
            'user_type': 'buyer',
            'author_id': buyer_id,
            'name': 'Green Restaurant',
            'organization': 'Restaurant',
            'requirements': 'Need fresh vegetables daily for our restaurant kitchen',
            'location': 'Mumbai, Maharashtra',
            'created_at': datetime.datetime.utcnow().isoformat(),
            'updated_at': datetime.datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'message': 'Demo data created successfully',
            'users': {
                'farmer': {'email': 'farmer@demo.com', 'password': 'demo123'},
                'buyer': {'email': 'buyer@demo.com', 'password': 'demo123'}
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Demo setup error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = 5000
    debug = True
    
    logger.info(f"Starting FarmLink backend (DEMO MODE) on port {port}")
    logger.info("This is a simplified version for testing without external database")
    logger.info("Use /api/demo/setup to create demo data")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
