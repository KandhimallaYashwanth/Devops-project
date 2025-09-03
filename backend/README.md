# FarmLink Backend

A Flask-based backend API for the FarmLink agricultural marketplace platform, providing user authentication, marketplace management, and real-time chat functionality.

## Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Marketplace API**: Create, read, update, and delete marketplace posts
- **Chat System**: Real-time messaging between farmers and buyers
- **User Profiles**: Manage user information and preferences
- **Database Integration**: Supabase PostgreSQL backend with automatic table creation
- **Input Validation**: Comprehensive data validation and sanitization
- **Error Handling**: Standardized error responses and logging

## Tech Stack

- **Framework**: Flask 2.3.3
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT (JSON Web Tokens)
- **CORS**: Flask-CORS for cross-origin requests
- **Validation**: Custom validation utilities
- **Security**: Werkzeug password hashing

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── models.py           # Data models and database operations
├── utils.py            # Utility functions and helpers
├── database.py         # Database initialization and management
├── requirements.txt    # Python dependencies
├── env_example.txt     # Environment variables template
└── README.md          # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Supabase account and project
- pip (Python package manager)

### 2. Installation

1. **Clone the repository and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Configuration

1. **Copy the environment template:**
   ```bash
   cp env_example.txt .env
   ```

2. **Edit `.env` file with your Supabase credentials:**
   ```env
   FLASK_ENV=development
   SECRET_KEY=your-super-secret-key
   JWT_SECRET=your-jwt-secret
   
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_KEY=your-supabase-service-key
   ```

### 4. Database Setup

1. **Initialize database tables:**
   ```bash
   python database.py
   ```

2. **Or run the main application (tables will be created automatically):**
   ```bash
   python app.py
   ```

### 5. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new user.

**Request Body:**
```json
{
  "username": "farmer_john",
  "email": "john@farm.com",
  "password": "securepassword123",
  "user_type": "farmer",
  "contact": "9876543210"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "token": "jwt_token_here",
  "user": {
    "id": "user_uuid",
    "username": "farmer_john",
    "email": "john@farm.com",
    "user_type": "farmer",
    "contact": "9876543210"
  }
}
```

#### POST `/api/auth/login`
Authenticate existing user.

**Request Body:**
```json
{
  "email": "john@farm.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "jwt_token_here",
  "user": {
    "id": "user_uuid",
    "username": "farmer_john",
    "email": "john@farm.com",
    "user_type": "farmer",
    "contact": "9876543210"
  }
}
```

### Marketplace Posts

#### GET `/api/posts`
Get marketplace posts with optional filtering.

**Query Parameters:**
- `user_type`: Filter by user type (`farmer` or `buyer`)
- `location`: Filter by location
- `search`: Search in post content

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "posts": [
    {
      "id": "post_uuid",
      "user_type": "farmer",
      "crop_name": "Organic Tomatoes",
      "crop_details": "Fresh organic tomatoes",
      "quantity": "50 kg",
      "location": "Mumbai, Maharashtra",
      "author_id": "user_uuid",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "count": 1
}
```

#### POST `/api/posts`
Create a new marketplace post.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body (Farmer):**
```json
{
  "crop_name": "Organic Tomatoes",
  "crop_details": "Fresh organic tomatoes, pesticide-free",
  "quantity": "50 kg",
  "location": "Mumbai, Maharashtra"
}
```

**Request Body (Buyer):**
```json
{
  "name": "Green Restaurant",
  "organization": "Restaurant",
  "requirements": "Need fresh vegetables daily",
  "location": "Mumbai, Maharashtra"
}
```

### Chat System

#### GET `/api/chats`
Get user's chat conversations.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "chats": [
    {
      "chat_id": "chat_uuid",
      "other_user": {
        "id": "other_user_uuid",
        "name": "Restaurant Owner",
        "user_type": "buyer"
      },
      "last_message": {
        "id": "message_uuid",
        "message": "Hello, I'm interested in your tomatoes",
        "created_at": "2024-01-01T10:00:00Z"
      },
      "created_at": "2024-01-01T09:00:00Z"
    }
  ],
  "count": 1
}
```

#### POST `/api/chats/<chat_id>/messages`
Send a message in a chat.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Hello, I'm interested in your tomatoes"
}
```

### User Profiles

#### GET `/api/profile`
Get user profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "profile": {
    "id": "profile_uuid",
    "user_id": "user_uuid",
    "name": "Farmer John",
    "email": "john@farm.com",
    "contact": "9876543210",
    "user_type": "farmer",
    "created_at": "2024-01-01T09:00:00Z"
  }
}
```

### Health Check

#### GET `/api/health`
Check API and database status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Database Schema

### Users Table
- `id`: UUID (Primary Key)
- `username`: VARCHAR(50)
- `email`: VARCHAR(255) UNIQUE
- `password_hash`: TEXT
- `user_type`: VARCHAR(20) CHECK ('farmer' or 'buyer')
- `contact`: VARCHAR(15)
- `google_id`: VARCHAR(255)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### User Profiles Table
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to users.id)
- `name`: VARCHAR(100)
- `email`: VARCHAR(255)
- `contact`: VARCHAR(15)
- `user_type`: VARCHAR(20)
- `bio`: TEXT
- `avatar_url`: TEXT
- `location`: VARCHAR(255)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### Marketplace Posts Table
- `id`: UUID (Primary Key)
- `user_type`: VARCHAR(20)
- `author_id`: UUID (Foreign Key to users.id)
- `crop_name`: VARCHAR(100) (for farmer posts)
- `crop_details`: TEXT (for farmer posts)
- `quantity`: VARCHAR(50) (for farmer posts)
- `name`: VARCHAR(100) (for buyer posts)
- `organization`: VARCHAR(50) (for buyer posts)
- `requirements`: TEXT (for buyer posts)
- `location`: VARCHAR(255)
- `price`: DECIMAL(10,2)
- `unit`: VARCHAR(20)
- `status`: VARCHAR(20)
- `views`: INTEGER
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### User Chats Table
- `id`: UUID (Primary Key)
- `user1_id`: UUID (Foreign Key to users.id)
- `user2_id`: UUID (Foreign Key to users.id)
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### Chat Messages Table
- `id`: UUID (Primary Key)
- `chat_id`: UUID (Foreign Key to user_chats.id)
- `sender_id`: UUID (Foreign Key to users.id)
- `message`: TEXT
- `message_type`: VARCHAR(20)
- `is_read`: BOOLEAN
- `created_at`: TIMESTAMP

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

Tokens expire after 24 hours by default.

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "error": true,
  "message": "Error description",
  "status_code": 400,
  "timestamp": "2024-01-01T10:00:00Z",
  "details": {
    "field": "Additional error details"
  }
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

### Code Style

The project follows PEP 8 style guidelines. Use a linter like `flake8` or `black`:

```bash
pip install flake8 black
flake8 .
black .
```

## Deployment

### Production Environment

1. **Set production environment variables:**
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-production-secret-key
   JWT_SECRET=your-production-jwt-secret
   ```

2. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up environment variables on your hosting platform**

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Future Enhancements

- Google OAuth integration
- Email notifications
- File upload support
- Real-time WebSocket chat
- Push notifications
- Analytics and reporting
- Mobile app API endpoints









