import os
from flask import session, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv
from functools import wraps
from minio import Minio

load_dotenv()

# Supabase Configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(url, key)

# Service Role Client (Admin)
service_key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase_admin: Client = None
if service_key:
    supabase_admin = create_client(url, service_key)
else:
    print("WARNING: SUPABASE_SERVICE_KEY not found. Admin functions will fail.")

# MinIO Configuration
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://172.20.0.22:9000") # Use Docker hostname by default
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "cobom_user_minio")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "GC0xeH7gl679P0Y0")
MINIO_BUCKET = "raia-photos"
MINIO_PUBLIC_URL_BASE = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}"

try:
    # MinIO client expects endpoint without scheme (http://)
    minio_endpoint_clean = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")

    # Configuration for Public Access URL
    # Use MINIO_EXTERNAL_URL if set, otherwise fallback to MINIO_ENDPOINT
    # Ensure we don't end up with double http:// or missing schemes
    _external_url = os.environ.get("MINIO_EXTERNAL_URL", MINIO_ENDPOINT)
    
    if not _external_url.startswith("http://") and not _external_url.startswith("https://"):
        _external_url = f"http://{_external_url}"
        
    MINIO_PUBLIC_URL_BASE = f"{_external_url}/{MINIO_BUCKET}"

    minio_client = Minio(
        minio_endpoint_clean,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False 
    )

    # Garantir que o bucket existe (Timeout curto para não travar o boot)
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
        policy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":["s3:GetObject"],"Resource":["arn:aws:s3:::%s/*"]}]}' % MINIO_BUCKET
        minio_client.set_bucket_policy(MINIO_BUCKET, policy)
except Exception as e:
    print(f"⚠️ AVISO: Erro ao conectar no MinIO ({MINIO_ENDPOINT}): {e}")
    # Não dar raise, para a aplicação subir mesmo sem MinIO
    minio_client = None

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login_page')) # Updated to point to auth blueprint
        return f(*args, **kwargs)
    return decorated_function
