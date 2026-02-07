import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class S3Service:
    def __init__(self):
        self.use_local_storage = os.getenv("USE_LOCAL_STORAGE", "False").lower() == "true"
        self.local_storage_path = os.path.join(os.getcwd(), "data", "uploads")
        
        if self.use_local_storage:
            os.makedirs(self.local_storage_path, exist_ok=True)
            print(f"Using local storage at: {self.local_storage_path}")
        else:
            self.endpoint_url = os.getenv("S3_ENDPOINT")
            self.access_key = os.getenv("S3_ACCESS_KEY")
            self.secret_key = os.getenv("S3_SECRET_KEY")
            self.bucket_name = os.getenv("S3_BUCKET", "kelp-teasers")
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=boto3.session.Config(signature_version='s3v4')
            )
            self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if self.use_local_storage:
            return
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"Creating bucket: {self.bucket_name}")
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                # Enable versioning
                self.s3_client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
            else:
                print(f"Error checking bucket: {e}")

    def upload_file(self, local_path: str, s3_key: str) -> Optional[str]:
        """
        Uploads a file to S3 and returns the version ID.
        """
        try:
            if self.use_local_storage:
                dest_path = os.path.join(self.local_storage_path, s3_key)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                import shutil
                shutil.copy2(local_path, dest_path)
                return "v1" # Dummy version ID for local storage

            with open(local_path, 'rb') as f:
                response = self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=f
                )
            return response.get('VersionId')
        except Exception as e:
            print(f"Upload Error: {e}")
            return None

    def download_file(self, s3_key: str, local_path: str, version_id: Optional[str] = None):
        """
        Downloads a file (specific version if provided) to local path.
        """
        try:
            if self.use_local_storage:
                source_path = os.path.join(self.local_storage_path, s3_key)
                if os.path.exists(source_path):
                    import shutil
                    shutil.copy2(source_path, local_path)
                    return True
                return False

            extra_args = {'VersionId': version_id} if version_id else {}
            self.s3_client.download_file(self.bucket_name, s3_key, local_path, ExtraArgs=extra_args)
            return True
        except Exception as e:
            print(f"Download Error: {e}")
            return False

    def get_presigned_url(self, s3_key: str, version_id: Optional[str] = None, expires_in: int = 3600) -> Optional[str]:
        """
        Generates a presigned URL for downloading the file.
        """
        try:
            if self.use_local_storage:
                # For local storage, we might return a file path or a local server URL
                # Returning absolute path for now as a fallback, or could be served via static files
                return os.path.join(self.local_storage_path, s3_key)

            params = {
                'Bucket': self.bucket_name,
                'Key': s3_key
            }
            if version_id:
                params['VersionId'] = version_id
                
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"Presigned URL Error: {e}")
            return None

# Singleton instance
_s3_service = None

def get_s3_service() -> S3Service:
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service
