import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

from memory import supabase

supabase.table("memories").insert({
    "user_id": "123",
    "username": "test",
    "message": "Hello Mini Luffy!"
}).execute()

print("Saved!")
