from google.cloud import storage
import pandas as pd
import io

BUCKET_NAME = "sentiment-explorer-user-files"


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
    return [blob.name for blob in bucket.list_blobs(prefix=f"{user_id}/") if blob.name.endswith(".csv")]

def load_user_file(user_id: str, filename: str) -> pd.DataFrame:
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{user_id}/{filename}")
    content = blob.download_as_string()
    return pd.read_csv(io.StringIO(content.decode()))
