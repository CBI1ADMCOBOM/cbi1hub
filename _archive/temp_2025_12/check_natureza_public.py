from services import supabase
import json

try:
    print("Checking oco_raia table with PUBLIC client...")
    res = supabase.table('oco_raia').select('*').execute()
    print(f"Count: {len(res.data)}")
except Exception as e:
    print(f"Error checking oco_raia with public client: {e}")
