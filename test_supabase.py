#!/usr/bin/env python3
import os
from supabase import create_client

# Test Supabase connection
supabase_url = "https://wsvulchcjrxzeoavgozw.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndzdnVsY2hjanJ4emVvYXZnb3p3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5MTY4NjEsImV4cCI6MjA3MTQ5Mjg2MX0.YD2NAvPQqbr2m58EMkLE0gjghDHJmsdoAkb7IsJa_NM"

try:
    client = create_client(supabase_url, supabase_key)
    print("✓ Supabase client created successfully")
    
    # Test a simple operation
    response = client.table('users').select('*').limit(1).execute()
    print("✓ Connection test successful")
    
except Exception as e:
    print(f"✗ Error: {e}")