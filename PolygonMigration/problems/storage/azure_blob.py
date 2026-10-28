"""
Azure Blob Storage backend (the tool's original provider).

Reuses ``AzureBlobManager`` for authentication.
"""
import logging

from azure.core.exceptions import AzureError

from problems.AzureTestcase import AzureBlobManager

from .base import StorageBackend, StorageError

logger = logging.getLogger(__name__)


class AzureBlobStorage(StorageBackend):
    """Stores files as blobs in a single Azure Blob Storage container."""

    display_name = "Azure Blob Storage"

    def __init__(self, account_url, container_name, tenant_id, client_id, username, password):
        manager = AzureBlobManager(account_url, tenant_id, client_id, username, password)
        self.container_name = container_name
        self.container_client = manager.blob_service_client.get_container_client(container_name)

    def upload(self, key, data, content_type=None):
        try:
            self.container_client.upload_blob(key, data, overwrite=True)
        except AzureError as e:
            raise StorageError(f"Failed to upload {key} to container {self.container_name}: {e}") from e
        logger.info("Uploaded azure://%s/%s (%d bytes)", self.container_name, key, len(data))

    def delete_prefix(self, prefix):
        deleted = 0
        try:
            for blob in self.container_client.list_blobs(name_starts_with=prefix):
                self.container_client.delete_blob(blob.name)
                deleted += 1
        except AzureError as e:
            raise StorageError(f"Failed to delete blobs under {prefix} in container {self.container_name}: {e}") from e
        logger.info("Deleted %d blob(s) under azure://%s/%s", deleted, self.container_name, prefix)
        return deleted
