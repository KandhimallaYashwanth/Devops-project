#!/bin/bash

# FarmLink Backend Deployment Script
# This script helps deploy the backend to production

set -e  # Exit on any error

echo "🚀 FarmLink Backend Deployment Script"
echo "======================================"

# Check if running in production mode
if [ "$FLASK_ENV" != "production" ]; then
    echo "⚠️  Warning: Not running in production mode"
    echo "   Set FLASK_ENV=production for production deployment"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create .env file from env_example.txt"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if database is configured
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "⚠️  Warning: Database configuration incomplete"
    echo "   Please check SUPABASE_URL and SUPABASE_ANON_KEY in .env"
else
    echo "✅ Database configuration found"
fi

# Initialize database (if needed)
echo "🗄️  Initializing database..."
python database.py

# Run tests (optional)
if [ "$1" = "--test" ]; then
    echo "🧪 Running tests..."
    python test_api.py
fi

# Start the application
echo "🌟 Starting FarmLink Backend..."
echo "   Server will be available at: http://0.0.0.0:${PORT:-5000}"
echo "   Press Ctrl+C to stop the server"
echo ""

# Use gunicorn in production, Flask dev server otherwise
if [ "$FLASK_ENV" = "production" ]; then
    echo "🏭 Running with Gunicorn (Production)"
    gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} --timeout 120 app:app
else
    echo "🔧 Running with Flask Development Server"
    python run.py
fi









