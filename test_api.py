#!/usr/bin/env python3
"""
API Testing Script for AI Knowledge Base

This script tests the main API endpoints to ensure everything is working correctly.
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.document_id = None
        self.session_id = None
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n👤 Testing user registration...")
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/users/", json=user_data)
            if response.status_code == 201:
                user_info = response.json()
                self.user_id = user_info["id"]
                print("✅ User registration successful")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User registration error: {e}")
            return False
    
    def test_user_login(self):
        """Test user login"""
        print("\n🔐 Testing user login...")
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,  # Form data for OAuth2
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                token_info = response.json()
                self.token = token_info["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Login successful")
                print(f"   Token received: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_user_profile(self):
        """Test getting user profile"""
        print("\n👤 Testing user profile...")
        try:
            response = self.session.get(f"{API_BASE}/users/me")
            if response.status_code == 200:
                profile = response.json()
                print("✅ Profile retrieval successful")
                print(f"   Username: {profile['username']}")
                print(f"   Email: {profile['email']}")
                return True
            else:
                print(f"❌ Profile retrieval failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Profile retrieval error: {e}")
            return False
    
    def create_test_pdf(self):
        """Create a simple test PDF file"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            filename = "test_document.pdf"
            c = canvas.Canvas(filename, pagesize=letter)
            
            # Add content to PDF
            c.drawString(100, 750, "AI Knowledge Base Test Document")
            c.drawString(100, 700, "This is a test document for the AI Knowledge Base system.")
            c.drawString(100, 650, "It contains sample content that can be processed and searched.")
            c.drawString(100, 600, "Key topics include: artificial intelligence, machine learning,")
            c.drawString(100, 550, "natural language processing, and document retrieval.")
            
            c.showPage()
            
            # Second page
            c.drawString(100, 750, "Page 2 - Additional Content")
            c.drawString(100, 700, "This page contains more information about:")
            c.drawString(100, 650, "- Vector databases and embeddings")
            c.drawString(100, 600, "- Retrieval augmented generation (RAG)")
            c.drawString(100, 550, "- FastAPI and Python web development")
            
            c.save()
            print(f"✅ Test PDF created: {filename}")
            return filename
            
        except ImportError:
            # Create a simple text file instead
            filename = "test_document.txt"
            content = """AI Knowledge Base Test Document

This is a test document for the AI Knowledge Base system.
It contains sample content that can be processed and searched.

Key topics include:
- Artificial intelligence
- Machine learning  
- Natural language processing
- Document retrieval
- Vector databases and embeddings
- Retrieval augmented generation (RAG)
- FastAPI and Python web development

This document serves as a test case for the PDF processing pipeline.
"""
            with open(filename, 'w') as f:
                f.write(content)
            print(f"⚠️  Created text file instead (reportlab not available): {filename}")
            return filename
    
    def test_document_upload(self):
        """Test document upload"""
        print("\n📄 Testing document upload...")
        
        # Create test file
        filename = self.create_test_pdf()
        
        try:
            with open(filename, 'rb') as f:
                files = {'file': (filename, f, 'application/pdf')}
                response = self.session.post(f"{API_BASE}/documents/upload", files=files)
            
            if response.status_code == 201:
                doc_info = response.json()
                self.document_id = doc_info["id"]
                print("✅ Document upload successful")
                print(f"   Document ID: {self.document_id}")
                print(f"   Filename: {doc_info['original_filename']}")
                print(f"   Size: {doc_info['file_size_bytes']} bytes")
                return True
            else:
                print(f"❌ Document upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Document upload error: {e}")
            return False
        finally:
            # Clean up test file
            Path(filename).unlink(missing_ok=True)
    
    def test_document_processing(self):
        """Test document processing"""
        if not self.document_id:
            print("❌ No document to process")
            return False
        
        print("\n⚙️ Testing document processing...")
        try:
            response = self.session.post(f"{API_BASE}/documents/{self.document_id}/process")
            if response.status_code == 202:
                result = response.json()
                print("✅ Document processing initiated")
                print(f"   Message: {result['message']}")
                
                # Check processing result
                if result.get('result', {}).get('errors'):
                    print("⚠️  Processing errors:")
                    for error in result['result']['errors']:
                        print(f"      - {error}")
                else:
                    print(f"   Text extraction: {result['result'].get('text_extraction', False)}")
                    print(f"   Chunking: {result['result'].get('chunking', False)}")
                    print(f"   Embeddings: {result['result'].get('embedding_generation', False)}")
                    print(f"   Total chunks: {result['result'].get('total_chunks', 0)}")
                
                return True
            else:
                print(f"❌ Document processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Document processing error: {e}")
            return False
    
    def test_document_status(self):
        """Test document processing status"""
        if not self.document_id:
            print("❌ No document to check status")
            return False
        
        print("\n📊 Testing document status...")
        try:
            response = self.session.get(f"{API_BASE}/documents/{self.document_id}/status")
            if response.status_code == 200:
                status = response.json()
                print("✅ Document status retrieved")
                doc = status['document']
                print(f"   Processing status: {doc['processing_status']}")
                print(f"   Total pages: {doc.get('total_pages', 'N/A')}")
                print(f"   Total characters: {doc.get('total_characters', 'N/A')}")
                print(f"   Total chunks: {status['chunks']['total']}")
                print(f"   Chunks with embeddings: {status['chunks']['with_embeddings']}")
                return True
            else:
                print(f"❌ Document status failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Document status error: {e}")
            return False
    
    def test_chat_question(self):
        """Test asking a question"""
        print("\n💬 Testing chat question...")
        question_data = {
            "question": "What are the main topics covered in this document?",
            "use_history": True
        }
        
        try:
            response = self.session.post(f"{API_BASE}/chat/ask", json=question_data)
            if response.status_code == 200:
                answer = response.json()
                self.session_id = answer.get("session_id")
                print("✅ Question answered successfully")
                print(f"   Answer: {answer['answer'][:200]}...")
                print(f"   Sources found: {len(answer.get('sources', []))}")
                print(f"   Session ID: {self.session_id}")
                print(f"   Response time: {answer.get('response_time_ms', 0)}ms")
                return True
            else:
                print(f"❌ Question failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Question error: {e}")
            return False
    
    def test_chat_sessions(self):
        """Test chat session management"""
        print("\n💭 Testing chat sessions...")
        try:
            response = self.session.get(f"{API_BASE}/chat/sessions")
            if response.status_code == 200:
                sessions = response.json()
                print("✅ Chat sessions retrieved")
                print(f"   Number of sessions: {len(sessions)}")
                for session in sessions[:3]:  # Show first 3
                    print(f"   - {session['title'][:50]}...")
                return True
            else:
                print(f"❌ Chat sessions failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Chat sessions error: {e}")
            return False
    
    def test_user_settings(self):
        """Test user settings"""
        print("\n⚙️ Testing user settings...")
        try:
            response = self.session.get(f"{API_BASE}/settings/")
            if response.status_code == 200:
                settings = response.json()
                print("✅ User settings retrieved")
                print(f"   Preferred model: {settings['preferred_model']}")
                print(f"   Max tokens: {settings['max_tokens']}")
                print(f"   Temperature: {settings['temperature']}")
                return True
            else:
                print(f"❌ User settings failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ User settings error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting AI Knowledge Base API Tests\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("User Profile", self.test_user_profile),
            ("Document Upload", self.test_document_upload),
            ("Document Processing", self.test_document_processing),
            ("Document Status", self.test_document_status),
            ("Chat Question", self.test_chat_question),
            ("Chat Sessions", self.test_chat_sessions),
            ("User Settings", self.test_user_settings)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

def main():
    tester = APITester()
    
    print("🚀 Starting automated API tests...")
    print("Server should be running on http://localhost:8000\n")
    
    tester.run_all_tests()

if __name__ == "__main__":
    main()