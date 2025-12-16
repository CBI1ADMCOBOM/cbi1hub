import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not service_key:
    print("Error: Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
    exit(1)

print(f"Connecting to {url}...")
supabase_admin = create_client(url, service_key)

user_id = 'c89407c5-e1a8-4df9-b276-9a92b140191e'
print(f"Checking user {user_id}...")

try:
    # Check if profile exists
    res = supabase_admin.table('profiles').select('*').eq('id', user_id).execute()
    
    if res.data:
        print(f"User found. Current role: {res.data[0].get('role')}")
        print("Promoting to ADMIN...")
        update_res = supabase_admin.table('profiles').update({'role': 'ADMIN'}).eq('id', user_id).execute()
        print("Update result:", update_res.data)
    else:
        print("User profile not found. Creating new ADMIN profile...")
        insert_res = supabase_admin.table('profiles').insert({'id': user_id, 'role': 'ADMIN'}).execute()
        print("Insert result:", insert_res.data)

except Exception as e:
    print(f"An error occurred: {e}")
