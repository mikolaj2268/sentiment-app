from google.cloud import storage
import pandas as pd
import io
import os
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

def save_user_csv(user_id: str, filename: str, df: pd.DataFrame):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{user_id}/{filename}")
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

def list_user_files(user_id: str):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    prefix = f"{user_id}/"
    blobs = bucket.list_blobs(prefix=prefix)
    return [
        blob.name[len(prefix):]  # usuwamy prefix "user_id/" z nazwy pliku
        for blob in blobs
        if blob.name.endswith(".csv")
    ]

def load_user_file(user_id: str, filename: str) -> pd.DataFrame:
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{user_id}/{filename}")
    content = blob.download_as_string()
    return pd.read_csv(io.StringIO(content.decode()))
