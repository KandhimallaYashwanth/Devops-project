#!/usr/bin/env python3
"""
Database initialization script for FarmLink
This script will create all necessary tables and insert sample data
"""

import os
from dotenv import load_dotenv
from database import DatabaseManager
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to initialize database"""
    
    # Get Supabase credentials from environment
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')  # Use service key for admin operations
    
    if not supabase_url or not supabase_key:
        logger.error("Missing Supabase credentials in .env file")
        logger.error("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY")
        return False
    
    try:
        # Initialize database manager
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager(supabase_url, supabase_key)
        
        if not db_manager.client:
            logger.error("Failed to initialize Supabase client")
            return False
        
        # Create tables
        logger.info("Creating database tables...")
        if not db_manager.create_tables():
            logger.error("Failed to create tables")
            return False
        
        # Insert sample data
        logger.info("Inserting sample data...")
        if not db_manager.insert_sample_data():
            logger.error("Failed to insert sample data")
            return False
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Database initialized successfully!")
        print("🚀 You can now run your FarmLink application with real database!")
    else:
        print("❌ Database initialization failed!")
        print("🔍 Check the logs above for details")
