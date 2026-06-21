import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
print("SUPABASE_URL =", url)
supabase = create_client(url, key)

def save_memory(user_id, username, message):
    supabase.table("memories").insert({
        "user_id": str(user_id),
        "username": username,
        "message": message
    }).execute()

def get_memory(user_id):
    result = (
        supabase.table("memories")
        .select("*")
        .eq("user_id", str(user_id))
        .execute()
    )
    return result.data
