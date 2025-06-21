import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

load_dotenv()
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def upload_csv_to_s3(local_file_path: str, s3_key: str) -> str:
    s3 = boto3.client("s3")
    try:
        s3.upload_file(local_file_path, BUCKET_NAME, s3_key, ExtraArgs={"ContentType": "text/csv"})
        print(f"✅ Uploaded to S3: s3://{BUCKET_NAME}/{s3_key}")
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    except NoCredentialsError:
        print("❌ AWS credentials not found.")
        return "ERROR"
