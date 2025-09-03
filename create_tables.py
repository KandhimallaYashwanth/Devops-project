#!/usr/bin/env python3
"""
Automatic table creation script for FarmLink
This script creates all necessary tables in Supabase using proper SQL execution
"""

import os
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all necessary tables in Supabase"""
    
    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        logger.error("Missing Supabase credentials in .env file")
        return False
    
    # Remove /rest/v1 from URL for SQL operations
    base_url = supabase_url.replace('/rest/v1', '')
    
    # Headers for SQL operations
    headers = {
        'apikey': supabase_service_key,
        'Authorization': f'Bearer {supabase_service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # SQL to create all tables
    create_tables_sql = """
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Create users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        username VARCHAR(50) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
        contact VARCHAR(15),
        google_id VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create user_profiles table
    CREATE TABLE IF NOT EXISTS user_profiles (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(100),
        bio TEXT,
        location VARCHAR(100),
        profile_image_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create marketplace_posts table
    CREATE TABLE IF NOT EXISTS marketplace_posts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
        author_id UUID REFERENCES users(id) ON DELETE CASCADE,
        crop_name VARCHAR(100),
        crop_details TEXT,
        quantity VARCHAR(50),
        name VARCHAR(100),
        organization VARCHAR(100),
        requirements TEXT,
        location VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create user_chats table
    CREATE TABLE IF NOT EXISTS user_chats (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user1_id UUID REFERENCES users(id) ON DELETE CASCADE,
        user2_id UUID REFERENCES users(id) ON DELETE CASCADE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create chat_messages table
    CREATE TABLE IF NOT EXISTS chat_messages (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        chat_id UUID REFERENCES user_chats(id) ON DELETE CASCADE,
        sender_id UUID REFERENCES users(id) ON DELETE CASCADE,
        message TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
    CREATE INDEX IF NOT EXISTS idx_posts_user_type ON marketplace_posts(user_type);
    CREATE INDEX IF NOT EXISTS idx_posts_location ON marketplace_posts(location);
    CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON chat_messages(chat_id);
    """
    
    try:
        # Execute SQL using Supabase's SQL endpoint
        sql_url = f"{base_url}/rest/v1/rpc/exec_sql"
        
        # Try the exec_sql function first
        response = requests.post(sql_url, headers=headers, json={'sql': create_tables_sql})
        
        if response.status_code == 200:
            logger.info("Tables created successfully using exec_sql")
            return True
        else:
            logger.warning(f"exec_sql failed: {response.status_code} - {response.text}")
            
            # Fallback: Use direct SQL endpoint
            sql_url = f"{base_url}/rest/v1/sql"
            response = requests.post(sql_url, headers=headers, json={'query': create_tables_sql})
            
            if response.status_code == 200:
                logger.info("Tables created successfully using direct SQL")
                return True
            else:
                logger.error(f"Direct SQL failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample data into tables"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    headers = {
        'apikey': supabase_service_key,
        'Authorization': f'Bearer {supabase_service_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Sample users
        users_data = [
            {
                'username': 'Demo Farmer',
                'email': 'farmer@demo.com',
                'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy',  # demo123
                'user_type': 'farmer',
                'contact': '9876543210'
            },
            {
                'username': 'Demo Buyer',
                'email': 'buyer@demo.com',
                'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy',  # demo123
                'user_type': 'buyer',
                'contact': '9876543211'
            }
        ]
        
        # Insert users
        for user_data in users_data:
            response = requests.post(f"{supabase_url}/users", headers=headers, json=user_data)
            if response.status_code == 201:
                logger.info(f"Created user: {user_data['username']}")
            else:
                logger.warning(f"Could not create user {user_data['username']}: {response.text}")
        
        logger.info("Sample data inserted successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error inserting sample data: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting automatic table creation...")
    
    # Create tables
    if create_tables():
        logger.info("✅ Tables created successfully!")
        
        # Insert sample data
        if insert_sample_data():
            logger.info("✅ Sample data inserted successfully!")
        else:
            logger.warning("⚠️ Could not insert sample data")
        
        logger.info("🚀 Database setup completed!")
        logger.info("You can now run your FarmLink application!")
        return True
    else:
        logger.error("❌ Failed to create tables")
        logger.info("💡 You may need to create tables manually in Supabase dashboard")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Manual Setup Instructions:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run the SQL commands from the create_tables.sql file")
        print("4. Restart your FarmLink application")
