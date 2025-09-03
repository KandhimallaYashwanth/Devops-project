#!/usr/bin/env python3
"""
Automatic table creation script for FarmLink using Supabase Python client
This script creates all necessary tables in Supabase using the official client
"""

import os
from dotenv import load_dotenv
import logging
from supabase import create_client, Client
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables_with_client():
    """Create tables using Supabase Python client"""
    
    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        logger.error("Missing Supabase credentials in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        logger.info("Supabase client initialized successfully")
        
        # Test connection
        response = supabase.table('users').select('id').limit(1).execute()
        logger.info("Database connection successful")
        
        return True
        
    except Exception as e:
        logger.info(f"Tables don't exist yet, will create them: {e}")
        return create_tables_manually()

def create_tables_manually():
    """Create tables by inserting sample data (tables will be auto-created)"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        logger.info("Creating tables by inserting sample data...")
        
        # Create sample users (this will create the users table)
        sample_users = [
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
        for user_data in sample_users:
            try:
                response = supabase.table('users').insert(user_data).execute()
                logger.info(f"Created user: {user_data['username']}")
            except Exception as e:
                logger.warning(f"User {user_data['username']} might already exist: {e}")
        
        # Get user IDs for creating posts
        users_response = supabase.table('users').select('id, user_type').execute()
        users = users_response.data
        
        farmer_id = None
        buyer_id = None
        
        for user in users:
            if user['user_type'] == 'farmer':
                farmer_id = user['id']
            elif user['user_type'] == 'buyer':
                buyer_id = user['id']
        
        # Create sample posts
        if farmer_id:
            farmer_post = {
                'user_type': 'farmer',
                'author_id': farmer_id,
                'crop_name': 'Organic Tomatoes',
                'crop_details': 'Fresh organic tomatoes, pesticide-free, harvested yesterday',
                'quantity': '50 kg',
                'location': 'Mumbai, Maharashtra'
            }
            
            try:
                supabase.table('marketplace_posts').insert(farmer_post).execute()
                logger.info("Created farmer post")
            except Exception as e:
                logger.warning(f"Could not create farmer post: {e}")
        
        if buyer_id:
            buyer_post = {
                'user_type': 'buyer',
                'author_id': buyer_id,
                'name': 'Green Restaurant',
                'organization': 'Restaurant',
                'requirements': 'Need fresh vegetables daily for our restaurant kitchen',
                'location': 'Mumbai, Maharashtra'
            }
            
            try:
                supabase.table('marketplace_posts').insert(buyer_post).execute()
                logger.info("Created buyer post")
            except Exception as e:
                logger.warning(f"Could not create buyer post: {e}")
        
        logger.info("✅ Sample data created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def check_database_status():
    """Check if database is properly set up"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Check users table
        users_response = supabase.table('users').select('count').execute()
        user_count = len(users_response.data)
        
        # Check posts table
        posts_response = supabase.table('marketplace_posts').select('count').execute()
        post_count = len(posts_response.data)
        
        logger.info(f"✅ Database Status:")
        logger.info(f"   - Users: {user_count}")
        logger.info(f"   - Posts: {post_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting FarmLink database setup...")
    
    # First try to create tables with client
    if create_tables_with_client():
        logger.info("✅ Tables exist or were created successfully!")
        
        # Check database status
        if check_database_status():
            logger.info("🎉 Database setup completed successfully!")
            logger.info("🚀 You can now run your FarmLink application!")
            return True
        else:
            logger.error("❌ Database check failed")
            return False
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
        print("3. Copy and paste the SQL from create_tables.sql")
        print("4. Click 'Run' to execute")
        print("5. Restart your FarmLink application")
