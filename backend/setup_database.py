#!/usr/bin/env python3
"""
FarmLink Database Setup Guide
This script will guide you through creating tables using Supabase's table editor
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_setup_instructions():
    """Print step-by-step setup instructions"""
    
    print("🚀 FarmLink Database Setup Guide")
    print("=" * 50)
    print()
    
    print("📋 Step 1: Go to Supabase Dashboard")
    print("   • Open: https://supabase.com/dashboard")
    print("   • Click on your project: tkibhdxdruomxoluxxkq")
    print()
    
    print("📋 Step 2: Create Tables Using Table Editor")
    print("   • Click 'Table Editor' in the left sidebar")
    print("   • Click 'Create a new table'")
    print()
    
    print("📋 Step 3: Create 'users' Table")
    print("   • Table name: users")
    print("   • Enable Row Level Security: ✅")
    print("   • Columns:")
    print("     - id: uuid (Primary Key, Default: gen_random_uuid())")
    print("     - username: varchar(50) (Not Null)")
    print("     - email: varchar(255) (Unique, Not Null)")
    print("     - password_hash: text (Not Null)")
    print("     - user_type: varchar(20) (Not Null)")
    print("     - contact: varchar(15)")
    print("     - google_id: varchar(255)")
    print("     - created_at: timestamptz (Default: now())")
    print("     - updated_at: timestamptz (Default: now())")
    print()
    
    print("📋 Step 4: Create 'user_profiles' Table")
    print("   • Table name: user_profiles")
    print("   • Enable Row Level Security: ✅")
    print("   • Columns:")
    print("     - id: uuid (Primary Key, Default: gen_random_uuid())")
    print("     - user_id: uuid (Foreign Key -> users.id)")
    print("     - name: varchar(100)")
    print("     - bio: text")
    print("     - location: varchar(100)")
    print("     - profile_image_url: text")
    print("     - created_at: timestamptz (Default: now())")
    print("     - updated_at: timestamptz (Default: now())")
    print()
    
    print("📋 Step 5: Create 'marketplace_posts' Table")
    print("   • Table name: marketplace_posts")
    print("   • Enable Row Level Security: ✅")
    print("   • Columns:")
    print("     - id: uuid (Primary Key, Default: gen_random_uuid())")
    print("     - user_type: varchar(20) (Not Null)")
    print("     - author_id: uuid (Foreign Key -> users.id)")
    print("     - crop_name: varchar(100)")
    print("     - crop_details: text")
    print("     - quantity: varchar(50)")
    print("     - name: varchar(100)")
    print("     - organization: varchar(100)")
    print("     - requirements: text")
    print("     - location: varchar(100) (Not Null)")
    print("     - created_at: timestamptz (Default: now())")
    print("     - updated_at: timestamptz (Default: now())")
    print()
    
    print("📋 Step 6: Create 'user_chats' Table")
    print("   • Table name: user_chats")
    print("   • Enable Row Level Security: ✅")
    print("   • Columns:")
    print("     - id: uuid (Primary Key, Default: gen_random_uuid())")
    print("     - user1_id: uuid (Foreign Key -> users.id)")
    print("     - user2_id: uuid (Foreign Key -> users.id)")
    print("     - created_at: timestamptz (Default: now())")
    print()
    
    print("📋 Step 7: Create 'chat_messages' Table")
    print("   • Table name: chat_messages")
    print("   • Enable Row Level Security: ✅")
    print("   • Columns:")
    print("     - id: uuid (Primary Key, Default: gen_random_uuid())")
    print("     - chat_id: uuid (Foreign Key -> user_chats.id)")
    print("     - sender_id: uuid (Foreign Key -> users.id)")
    print("     - message: text (Not Null)")
    print("     - created_at: timestamptz (Default: now())")
    print()
    
    print("📋 Step 8: Test Database Connection")
    print("   • Run: python test_database.py")
    print()
    
    print("📋 Step 9: Start Your Application")
    print("   • Backend: python app.py")
    print("   • Frontend: python -m http.server 8000")
    print()
    
    print("🎉 You're all set! Your FarmLink database is ready!")

def create_sample_data_script():
    """Create a script to insert sample data after tables are created"""
    
    script_content = '''#!/usr/bin/env python3
"""
Insert sample data into FarmLink database
Run this after creating all tables
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def insert_sample_data():
    """Insert sample users and posts"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Connected to Supabase")
        
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
            try:
                response = supabase.table('users').insert(user_data).execute()
                print(f"✅ Created user: {user_data['username']}")
            except Exception as e:
                print(f"⚠️ User {user_data['username']} might already exist")
        
        # Get user IDs
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
                print("✅ Created farmer post")
            except Exception as e:
                print(f"⚠️ Could not create farmer post: {e}")
        
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
                print("✅ Created buyer post")
            except Exception as e:
                print(f"⚠️ Could not create buyer post: {e}")
        
        print("🎉 Sample data inserted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = insert_sample_data()
    if success:
        print("🚀 Your FarmLink database is ready!")
    else:
        print("❌ Failed to insert sample data")
'''
    
    with open('insert_sample_data.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Created 'insert_sample_data.py' script")

def main():
    """Main function"""
    print_setup_instructions()
    print()
    create_sample_data_script()
    print()
    print("📝 Next Steps:")
    print("1. Follow the instructions above to create tables")
    print("2. Run: python insert_sample_data.py")
    print("3. Run: python app.py")
    print("4. Open: http://localhost:8000")

if __name__ == "__main__":
    main()
