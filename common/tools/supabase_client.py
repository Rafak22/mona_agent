from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client conditionally
supabase = None
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if supabase_url and supabase_key:
        supabase = create_client(
            supabase_url=supabase_url,
            supabase_key=supabase_key
        )
    else:
        print("⚠️  Supabase environment variables not found. Running without database connection.")
except Exception as e:
    print(f"⚠️  Failed to initialize Supabase client: {e}")
    supabase = None