from supabase import create_client, Client
from .config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

def get_supabase() -> Client:
    return supabase

# For compatibility with existing endpoints
def get_db():
    return get_supabase()