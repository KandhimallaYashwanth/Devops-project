#!/usr/bin/env python3
"""
FarmLink Backend Startup Script
Run this file to start the Flask application
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting FarmLink Backend...")
    print(f"📍 Server: {host}:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"🌐 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"📊 Database: {'Connected' if os.getenv('SUPABASE_URL') else 'Not Configured'}")
    print("-" * 50)
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)









