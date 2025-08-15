#!/usr/bin/env python3
"""
AI Knowledge Base - Startup Script

This script helps you start the AI Knowledge Base application with proper setup.
"""

import os
import sys
from pathlib import Path
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import openai
        import chromadb
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check environment variables"""
    required_vars = [
        'DATABASE_URL',
        'OPENAI_API_KEY', 
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        return False
    
    print("✓ Environment variables are set")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        Path(os.getenv('UPLOAD_DIRECTORY', './uploads')),
        Path(os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db'))
    ]
    
    for dir_path in directories:
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def run_migrations():
    """Run database migrations"""
    try:
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Database migrations completed")
            return True
        else:
            print(f"✗ Migration failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ Alembic not found. Please install requirements.")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting AI Knowledge Base server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main startup sequence"""
    print("🤖 AI Knowledge Base - Starting Up...\n")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Run migrations
    if not run_migrations():
        print("⚠️  Migration failed, but continuing...")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()