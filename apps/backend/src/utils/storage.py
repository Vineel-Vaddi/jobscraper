import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
import uuid
import os
from src.config import settings

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION
    )

def upload_file_to_s3(file: UploadFile, prefix: str = "") -> str:
    """Uploads file to S3 and returns the unique storage key."""
    s3_client = get_s3_client()
    bucket_name = settings.MINIO_BUCKET_NAME
    
    file_ext = ""
    if file.filename:
        _, file_ext = os.path.splitext(file.filename)
        
    storage_key = f"{prefix}{uuid.uuid4()}{file_ext}"
    
    try:
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            storage_key,
            ExtraArgs={'ContentType': file.content_type}
        )
    except ClientError as e:
        print(f"Failed to upload to S3: {e}")
        raise
        
    return storage_key

def get_file_url(storage_key: str, expiration: int = 3600) -> str:
    """Generates a presigned URL to securely download a file."""
    s3_client = get_s3_client()
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.MINIO_BUCKET_NAME,
                'Key': storage_key
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(e)
        return ""
    return response

def download_file_to_memory(storage_key: str) -> bytes:
    """Downloads a file directly to memory byte string."""
    s3_client = get_s3_client()
    response = s3_client.get_object(Bucket=settings.MINIO_BUCKET_NAME, Key=storage_key)
    return response['Body'].read()

def upload_bytes_to_s3(data: bytes, storage_key: str, content_type: str = "text/plain") -> str:
    """Uploads literal bytes to S3 and returns the storage key."""
    s3_client = get_s3_client()
    s3_client.put_object(
        Bucket=settings.MINIO_BUCKET_NAME,
        Key=storage_key,
        Body=data,
        ContentType=content_type
    )
    return storage_key
