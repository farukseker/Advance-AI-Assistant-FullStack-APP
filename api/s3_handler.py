from datetime import datetime, timezone
from urllib.parse import quote
from typing import Optional, Dict, List
from botocore.exceptions import ClientError
from botocore.client import Config as BotocoreConfig
import boto3

from config import BUCKET_NAME, BUCKET_SECRET_KEY, BUCKET_ACCESS_KEY, BUCKET_ENDPOINT_URL


class S3Handler:
    def __init__(self):
        self.endpoint_url = BUCKET_ENDPOINT_URL
        self.bucket_name = BUCKET_NAME
        self.access_key = BUCKET_ACCESS_KEY
        self.secret_key = BUCKET_SECRET_KEY
        self.region = 'us-east-1'



        botocore_config = BotocoreConfig(
            # signature_version='s3v4',
            signature_version='s3',
            s3={
                "addressing_style": "path",
                'payload_signing_enabled': True
            }
        )

        self.bucket_name = BUCKET_NAME
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            region_name='us-east-1',
            aws_secret_access_key=self.secret_key,
            use_ssl=False,
            config=botocore_config
        )
    def upload_file(
            self,
            file_content: bytes,
            s3_key: str,
            content_type: str,
            metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload file to S3
        """
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=metadata or {}
            )
            return True
        except ClientError as e:
            print(f"Upload error: {e}")
            return False

    def download_file(self, s3_key: str) -> Optional[Dict]:
        """
        Download file from S3
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return {
                'content': response['Body'].read(),
                'content_type': response['ContentType'],
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            print(f"Download error: {e}")
            return None

    def list_files(self, prefix: str='') -> List[Dict]:
        """
        List files with given prefix
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag']
                    })

            return files
        except ClientError as e:
            print(f"List error: {e}")
            return []

    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Delete error: {e}")
            return False

    def file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError:
            return False

    def generate_presigned_url(
            self,
            s3_key: str,
            expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL for file access
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Presigned URL error: {e}")
            return None

    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """
        Copy file within S3
        """
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }
            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dest_key
            )
            return True
        except ClientError as e:
            print(f"Copy error: {e}")
            return False

    def get_file_metadata(self, s3_key: str) -> Optional[Dict]:
        """
        Get file metadata
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return {
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'last_modified': response['LastModified'].isoformat(),
                'metadata': response.get('Metadata', {}),
                'etag': response['ETag']
            }
        except ClientError as e:
            print(f"Metadata error: {e}")
            return None

    def bucket_exists(self) -> bool:
        """
        Check if bucket exists
        """
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False


def get_s3_handler() -> S3Handler:
    """
    Get S3 handler instance
    """
    return S3Handler()




if __name__ == '__main__':
    s3_handler = get_s3_handler()
    s3_handler.bucket_exists()
    # s3_handler.delete_file('test')
    # s3_handler.list_files('test')