from services import supabase_admin
import json

try:
    print("Checking profiles count...")
    res = supabase_admin.table('profiles').select('*', count='exact').limit(1).execute()
    print(f"Profiles count: {res.count}")
    
    print("Checking vulto_occurrences count...")
    res2 = supabase_admin.table('vulto_occurrences').select('*', count='exact').limit(1).execute()
    print(f"Vulto count: {res2.count}")

    print("Checking last 5 vultos:")
    res3 = supabase_admin.table('vulto_occurrences').select('*').order('created_at', desc=True).limit(5).execute()
    print(json.dumps(res3.data, indent=2, default=str))

except Exception as e:
    print(f"Error: {e}")
