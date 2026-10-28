"""
AWS S3 storage backend.
"""
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .base import StorageBackend, StorageError

logger = logging.getLogger(__name__)

# S3 DeleteObjects accepts at most 1000 keys per request.
_DELETE_BATCH_SIZE = 1000


class S3Storage(StorageBackend):
    """Stores files as objects in a single S3 bucket."""

    display_name = "AWS S3"

    def __init__(self, bucket_name, region=None, access_key_id=None, secret_access_key=None):
        """
        Args:
            bucket_name (str): Target bucket.
            region (str, optional): Bucket region, e.g. ``ap-south-1``.
            access_key_id (str, optional): Access key. If omitted, boto3's
                default credential chain is used (env vars, ~/.aws, IAM role).
            secret_access_key (str, optional): Secret key matching the access key.
        """
        self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            region_name=region or None,
            aws_access_key_id=access_key_id or None,
            aws_secret_access_key=secret_access_key or None,
        )

    def upload(self, key, data, content_type=None):
        extra = {"ContentType": content_type} if content_type else {}
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=key, Body=data, **extra)
        except (BotoCoreError, ClientError) as e:
            raise StorageError(f"Failed to upload {key} to bucket {self.bucket_name}: {e}") from e
        logger.info("Uploaded s3://%s/%s (%d bytes)", self.bucket_name, key, len(data))

    def delete_prefix(self, prefix, keep=None):
        deleted = 0
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            keys = [
                obj["Key"]
                for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
                for obj in page.get("Contents", [])
                if not keep or obj["Key"] not in keep
            ]
            for start in range(0, len(keys), _DELETE_BATCH_SIZE):
                batch = keys[start:start + _DELETE_BATCH_SIZE]
                response = self.client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={"Objects": [{"Key": k} for k in batch], "Quiet": True},
                )
                errors = response.get("Errors", [])
                if errors:
                    raise StorageError(f"Failed to delete {len(errors)} object(s) under {prefix}: {errors[0]}")
                deleted += len(batch)
        except (BotoCoreError, ClientError) as e:
            raise StorageError(f"Failed to delete objects under {prefix} in bucket {self.bucket_name}: {e}") from e
        logger.info("Deleted %d object(s) under s3://%s/%s", deleted, self.bucket_name, prefix)
        return deleted
