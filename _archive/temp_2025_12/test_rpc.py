from services import supabase_admin

try:
    print("Testing exec_sql RPC...")
    # Trying a harmless select
    # Note: if exec_sql returns void, we can't extract data easily, but we check for No Error.
    # Usually exec_sql is for DDL/DML, not SELECT.
    # We can try a Create Table temp or similar, or just a valid syntax that does nothing.
    sql = "SELECT 1;" 
    res = supabase_admin.rpc('exec_sql', {'query': sql}).execute()
    print("RPC call successful.")
except Exception as e:
    print(f"RPC failed: {e}")
