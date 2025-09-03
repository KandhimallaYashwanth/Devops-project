#!/usr/bin/env python3
"""
Check the actual structure of database tables
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def check_table_structure():
    """Check the structure of all tables"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Connected to Supabase")
        
        # Try to get table structure by inserting a test record
        tables = ['users', 'user_profiles', 'marketplace_posts', 'user_chats', 'chat_messages']
        
        for table in tables:
            print(f"\n📋 Table: {table}")
            print("-" * 30)
            
            try:
                # Try to get one record to see the structure
                response = supabase.table(table).select('*').limit(1).execute()
                if response.data:
                    # Print column names from the first record
                    columns = list(response.data[0].keys())
                    print(f"Columns: {', '.join(columns)}")
                else:
                    print("Table is empty, cannot determine structure")
                    
            except Exception as e:
                print(f"Error: {e}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    print("🔍 Checking FarmLink Database Structure...")
    print("=" * 50)
    check_table_structure()
