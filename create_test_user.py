#!/usr/bin/env python3
import os
from supabase import create_client

# Use the test Supabase credentials
supabase_url = "https://wsvulchcjrxzeoavgozw.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzdnVsY2hjanJ4emVvYXZnb3p3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5MTY4NjEsImV4cCI6MjA3MTQ5Mjg2MX0.YD2NAvPQqbr2m58EMkLE0gjghDHJmsdoAkb7IsJa_NM"

def test_user_creation():
    try:
        client = create_client(supabase_url, supabase_key)
        print("✓ Supabase client created successfully")
        
        # Try to create a test user
        email = "testuser@gmail.com"
        password = "testpassword123"
        
        print(f"Attempting to create user: {email}")
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": "testuser",
                    "full_name": "Test User"
                }
            }
        })
        
        if response.user:
            print("✓ User created successfully!")
            print(f"User ID: {response.user.id}")
            print(f"Email confirmed: {response.user.email_confirmed_at}")
            
            if response.session:
                print(f"Access token: {response.session.access_token[:20]}...")
                return response.session.access_token
            else:
                print("No session - user may need email confirmation")
                
        return None
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_login(email="testuser@gmail.com", password="testpassword123"):
    try:
        client = create_client(supabase_url, supabase_key)
        print(f"Attempting to login: {email}")
        
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user and response.session:
            print("✓ Login successful!")
            print(f"Access token: {response.session.access_token[:20]}...")
            return response.session.access_token
        else:
            print("✗ Login failed - no user or session")
            
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

if __name__ == "__main__":
    print("=== Testing Supabase User Creation ===")
    token = test_user_creation()
    
    print("\n=== Testing Supabase Login ===")
    if not token:
        token = test_login()
    
    if token:
        print(f"\n=== Testing Backend API with Token ===")
        import requests
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
            print(f"API Response: {response.status_code}")
            if response.status_code == 200:
                print("✓ Backend authentication working!")
                print(f"User data: {response.json()}")
            else:
                print(f"✗ Backend error: {response.text}")
        except Exception as e:
            print(f"✗ API test error: {e}")