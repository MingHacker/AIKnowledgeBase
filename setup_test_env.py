#!/usr/bin/env python3
"""
Test Environment Setup Script

This script helps set up a test environment for the AI Knowledge Base.
"""

import os
import subprocess
import sys
from pathlib import Path

def create_test_env_file():
    """Create a test .env file if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from example...")
        
        # Read example file
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Replace with test values
        test_content = content.replace(
            "postgresql://username:password@localhost/ai_knowledgebase",
            "postgresql://postgres:password@localhost/ai_knowledgebase_test"
        ).replace(
            "your_openai_api_key_here",
            "sk-test-key-replace-with-real-key"
        ).replace(
            "your_secret_key_here",
            "test-secret-key-for-jwt-tokens-change-in-production"
        )
        
        # Write test env file
        with open(env_file, 'w') as f:
            f.write(test_content)
        
        print("✅ .env file created")
        print("⚠️  Please update the following in .env:")
        print("   - DATABASE_URL (your PostgreSQL connection)")
        print("   - OPENAI_API_KEY (your OpenAI API key)")
        print("   - SECRET_KEY (a secure random string)")
    else:
        print("✅ .env file already exists")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        ('fastapi', 'fastapi'), ('uvicorn', 'uvicorn'), ('sqlalchemy', 'sqlalchemy'), 
        ('alembic', 'alembic'), ('psycopg2', 'psycopg2'), ('pydantic', 'pydantic'), 
        ('python-dotenv', 'dotenv'), ('openai', 'openai'), ('chromadb', 'chromadb'), 
        ('PyPDF2', 'PyPDF2')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def create_test_database():
    """Create test database if it doesn't exist"""
    print("🗄️ Setting up test database...")
    
    try:
        # Try to connect and create database
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="password",  # Update this
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create test database
        try:
            cursor.execute("CREATE DATABASE ai_knowledgebase_test")
            print("✅ Test database created")
        except psycopg2.errors.DuplicateDatabase:
            print("✅ Test database already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"⚠️  Could not set up database: {e}")
        print("💡 Please create the database manually:")
        print("   createdb ai_knowledgebase_test")
        return False

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    
    try:
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database migrations completed")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install requirements.")
        return False

def create_test_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ['uploads', 'chroma_db']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Knowledge Base test environment\n")
    
    # Create .env file
    create_test_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_test_directories()
    
    # Setup database (optional)
    create_test_database()
    
    # Run migrations
    run_migrations()
    
    print("\n🎉 Test environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Update .env with your actual database and API keys")
    print("2. Start the server: python start.py")
    print("3. Run tests: python test_api.py")
    print("4. View API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()