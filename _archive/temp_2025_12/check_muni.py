from services import supabase_admin
import json

try:
    print("Checking municipalities table...")
    res = supabase_admin.table('municipalities').select('*').limit(5).execute()
    print(f"Count: {len(res.data)}")
    if res.data:
        print(json.dumps(res.data[0], indent=2))
    else:
        print("Table appears empty.")

except Exception as e:
    print(f"Error checking municipalities: {e}")
