import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Supabase environment variables are missing! Check your .env file")

# Create Supabase client
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Supabase connected successfully!")