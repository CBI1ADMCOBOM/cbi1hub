
import os
import io
from minio import Minio

# Mock Environment Variables (matching services.py and .env)
# Assuming run inside container where MINIO__ENDPOINT is reachable
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "172.20.0.22:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "cobom_user_minio")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "GC0xeH7gl679P0Y0")
MINIO_BUCKET = "raia-photos"
MINIO_EXTERNAL_URL = os.environ.get("MINIO_EXTERNAL_URL", f"http://{MINIO_ENDPOINT}")

# Logic from services.py
minio_endpoint_clean = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")

print(f"DEBUG: Endpoint Clean: {minio_endpoint_clean}")
print(f"DEBUG: External URL: {MINIO_EXTERNAL_URL}")

try:
    client = Minio(
        minio_endpoint_clean,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    # Check bucket
    if not client.bucket_exists(MINIO_BUCKET):
        print(f"Bucket {MINIO_BUCKET} does not exist. Creating...")
        client.make_bucket(MINIO_BUCKET)
    else:
        print(f"Bucket {MINIO_BUCKET} exists.")

    # Upload Test
    file_name = "backend_test_file.txt"
    content = b"Hello MinIO from Backend Script"
    stream = io.BytesIO(content)
    
    client.put_object(
        MINIO_BUCKET,
        file_name,
        stream,
        length=len(content),
        content_type="text/plain"
    )
    print(f"Successfully uploaded {file_name}")

    # Generate URL (Logic from services.py)
    if not MINIO_EXTERNAL_URL.startswith("http"):
        base = f"http://{MINIO_EXTERNAL_URL}"
    else:
        base = MINIO_EXTERNAL_URL
        
    public_url = f"{base}/{MINIO_BUCKET}/{file_name}"
    print(f"Generated Public URL: {public_url}")
    
    # Try stat object
    stat = client.stat_object(MINIO_BUCKET, file_name)
    print(f"Stat Object: {stat.object_name}, Size: {stat.size}")

except Exception as e:
    print(f"ERROR: {e}")
