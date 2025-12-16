from services import minio_client, MINIO_BUCKET, MINIO_PUBLIC_URL_BASE
import json

print(f"--- MINIO DEBUG ---")
print(f"Bucket: {MINIO_BUCKET}")
print(f"Public Base: {MINIO_PUBLIC_URL_BASE}")

try:
    if not minio_client.bucket_exists(MINIO_BUCKET):
        print("❌ Bucket does not exist!")
    else:
        print("✅ Bucket exists.")
        
        # Check Policy
        try:
            policy = minio_client.get_bucket_policy(MINIO_BUCKET)
            print(f"📜 Current Policy: {policy}")
        except Exception as e:
            print(f"⚠️ Could not read policy (might be empty/private): {e}")

        # List objects
        print("\n--- Recent Files ---")
        objects = minio_client.list_objects(MINIO_BUCKET)
        count = 0
        for obj in objects:
            count += 1
            print(f"📄 Found: {obj.object_name} ({obj.size} bytes)")
            print(f"   🔗 Generated URL: {MINIO_PUBLIC_URL_BASE}/{obj.object_name}")
            if count >= 3: break
            
        if count == 0:
            print("⚠️ No files found in bucket.")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
