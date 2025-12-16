from services import supabase
import json

try:
    print("Checking css table with PUBLIC client...")
    res = supabase.table('css').select('*').execute()
    print(f"Count: {len(res.data)}")
    print(json.dumps(res.data, indent=2))
except Exception as e:
    print(f"Error checking css with public client: {e}")
