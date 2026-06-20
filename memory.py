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
import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

def save_memory(user_id, username, message):
    supabase.table("memories").insert({
        "user_id": str(user_id),
        "username": username,
        "message": message
    }).execute()

def get_memory(user_id, limit=20):
    result = (
        supabase.table("memories")
        .select("*")
        .eq("user_id", str(user_id))
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
