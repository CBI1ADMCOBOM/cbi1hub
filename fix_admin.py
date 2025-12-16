from services import supabase_admin

user_id = 'c89407c5-e1a8-4df9-b276-9a92b140191e'
print(f"Checking user {user_id}...")

try:
    res = supabase_admin.table('profiles').select('*').eq('id', user_id).execute()
    print("Current profile:", res.data)

    if res.data:
        print("Updating to ADMIN...")
        update_res = supabase_admin.table('profiles').update({'role': 'ADMIN'}).eq('id', user_id).execute()
        print("Updated:", update_res.data)
    else:
        print("User not found in profiles! Creating profile...")
        # Fallback if profile doesn't exist at all
        insert_res = supabase_admin.table('profiles').insert({'id': user_id, 'role': 'ADMIN'}).execute()
        print("Created:", insert_res.data)

except Exception as e:
    print(f"Error: {e}")
