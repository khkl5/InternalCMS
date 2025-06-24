import os
from supabase import create_client, Client
from dotenv import load_dotenv

# تحميل .env
load_dotenv()

# قراءه SUPABASE_URL و SUPABASE_SERVICE_KEY
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# إنشاء Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
