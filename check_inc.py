from services import supabase_admin
import json

try:
    print("Checking inconsistencies table (Admin)...")
    res = supabase_admin.table('inconsistencies').select('*').execute()
    print(f"Count: {len(res.data)}")
    if res.data:
        print("Sample data:")
        print(json.dumps(res.data[0], indent=2))
except Exception as e:
    print(f"Error checking inconsistencies: {e}")
