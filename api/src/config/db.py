import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Supabase client initialized")
