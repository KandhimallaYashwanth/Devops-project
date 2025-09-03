@echo off
REM FarmLink Backend Deployment Script for Windows
REM This script helps deploy the backend to production

echo 🚀 FarmLink Backend Deployment Script
echo ======================================

REM Check if running in production mode
if not "%FLASK_ENV%"=="production" (
    echo ⚠️  Warning: Not running in production mode
    echo    Set FLASK_ENV=production for production deployment
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ Error: .env file not found
    echo    Please create .env file from env_example.txt
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check if database is configured
if "%SUPABASE_URL%"=="" (
    echo ⚠️  Warning: Database configuration incomplete
    echo    Please check SUPABASE_URL and SUPABASE_ANON_KEY in .env
) else (
    echo ✅ Database configuration found
)

REM Initialize database (if needed)
echo 🗄️  Initializing database...
python database.py

REM Run tests (optional)
if "%1"=="--test" (
    echo 🧪 Running tests...
    python test_api.py
)

REM Start the application
echo 🌟 Starting FarmLink Backend...
echo    Server will be available at: http://0.0.0.0:%PORT%
if "%PORT%"=="" echo    Server will be available at: http://0.0.0.0:5000
echo    Press Ctrl+C to stop the server
echo.

REM Use gunicorn in production, Flask dev server otherwise
if "%FLASK_ENV%"=="production" (
    echo 🏭 Running with Gunicorn (Production)
    gunicorn -w 4 -b 0.0.0.0:%PORT% --timeout 120 app:app
) else (
    echo 🔧 Running with Flask Development Server
    python run.py
)

pause









