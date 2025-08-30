#!/usr/bin/env python3
import requests
import json

def test_with_manual_token():
    """Test the authentication flow by manually creating a token"""
    
    # You can get a valid token by:
    # 1. Going to your Supabase dashboard
    # 2. Authentication → Users → Select a user → Copy JWT token
    # Or manually confirm the test user in the dashboard
    
    print("=== Testing Backend Authentication ===")
    print("To get a valid token:")
    print("1. Go to https://wsvulchcjrxzeoavgozw.supabase.co/project/auth/users")
    print("2. Find your user and click the three dots → 'Send Email Confirmation' or confirm manually")
    print("3. Or copy a JWT token from an existing user")
    
    token = input("\nEnter a valid JWT token (or press Enter to skip): ").strip()
    
    if not token:
        print("Skipping token test")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
        print(f"\nAPI Response: {response.status_code}")
        if response.status_code == 200:
            print("✓ Backend authentication working!")
            print(f"User data: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"✗ Backend error: {response.text}")
    except Exception as e:
        print(f"✗ API test error: {e}")

def test_backend_login():
    """Test backend login endpoint with confirmed user"""
    email = input("Enter email of confirmed user: ").strip()
    password = input("Enter password: ").strip()
    
    if not email or not password:
        return
        
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login", 
                               json={"email": email, "password": password})
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Backend login successful!")
            print(f"Token: {data['access_token'][:20]}...")
            
            # Test /users/me with this token
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            me_response = requests.get("http://localhost:8000/api/v1/users/me", headers=headers)
            print(f"\n/users/me Response: {me_response.status_code}")
            if me_response.status_code == 200:
                print("✓ /users/me working!")
                print(f"User data: {json.dumps(me_response.json(), indent=2)}")
            else:
                print(f"✗ /users/me error: {me_response.text}")
                
        else:
            print(f"✗ Backend login failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Login test error: {e}")

if __name__ == "__main__":
    print("Choose test option:")
    print("1. Test with manual token")
    print("2. Test backend login with confirmed user")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_with_manual_token()
    elif choice == "2":
        test_backend_login()
    else:
        print("Invalid choice")