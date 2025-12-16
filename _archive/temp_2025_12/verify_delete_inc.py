
from services import supabase_admin
import uuid

# 1. Create a dummy inconsistency directly in DB (simulating a user creation)
user_id = 'c89407c5-e1a8-4df9-b276-9a92b140191e' # The user we are debugging
dummy_id = str(uuid.uuid4())

print(f"Creating dummy inconsistency {dummy_id} for user {user_id}...")

try:
    data = {
        'id': dummy_id,
        'user_id': user_id,
        'data_ocorrencia': '2025-12-16',
        'tipo': 'TECNICA',
        'motivo_tec_codigo': 'TEST_DELETE',
        'observacao': 'TO BE DELETED'
    }
    supabase_admin.table('inconsistencies').insert(data).execute()
    print("Created.")
    
    # 2. Verify it exists
    res = supabase_admin.table('inconsistencies').select('*').eq('id', dummy_id).execute()
    if not res.data:
        print("Error: Could not find created item.")
        exit(1)
    
    print("Item verified in DB.")

    # 3. Simulate Logic of 'delete_inconsistencia' manually (since we can't easily curl with auth session)
    # This validates the SERVER logic
    print("Simulating delete logic...")
    
    # Logic from route:
    server_res = supabase_admin.table('inconsistencies').select('user_id').eq('id', dummy_id).single().execute()
    
    if not server_res.data:
         print("Logic Error: Record not found.")
    elif server_res.data['user_id'] != user_id:
         print("Logic Error: Permission denied.")
    else:
         print("Logic Check: Permission GRANTED.")
         del_res = supabase_admin.table('inconsistencies').delete().eq('id', dummy_id).execute()
         print("Delete executed.")
         
         # 4. Confirm deletion
         final_check = supabase_admin.table('inconsistencies').select('*').eq('id', dummy_id).execute()
         if not final_check.data:
             print("SUCCESS: Item was deleted.")
         else:
             print("FAILURE: Item still exists.")

except Exception as e:
    print(f"Exception: {e}")
