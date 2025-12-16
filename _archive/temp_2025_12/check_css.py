from services import supabase_admin
import json

try:
    print("Checking css table...")
    # Trying to select from 'css'
    res = supabase_admin.table('css').select('*').execute()
    print(f"Count: {len(res.data)}")
    print(json.dumps(res.data, indent=2))
except Exception as e:
    print(f"Error checking css: {e}")
