from services import minio_client, MINIO_BUCKET

if minio_client:
    try:
        print(f"Connecting to MinIO...")
        exists = minio_client.bucket_exists(MINIO_BUCKET)
        print(f"Bucket '{MINIO_BUCKET}' exists? {exists}")
        print("SUCCESS: MinIO connection working.")
    except Exception as e:
        print(f"FAILURE: {e}")
else:
    print("FAILURE: minio_client is None")
