"""
Provider-neutral storage interface used by the migration flow.

The migration code only talks to ``StorageBackend``; each cloud provider
(S3-compatible, Azure Blob, ...) implements it in its own module, so the
provider can be swapped by changing ``STORAGE_PROVIDER`` without touching
the migration logic.
"""
from abc import ABC, abstractmethod


class StorageError(Exception):
    """Raised when a storage operation fails."""


class StorageBackend(ABC):
    """Minimal set of operations the migration flow needs from cloud storage."""

    #: Human-readable provider name, used in log and UI messages.
    display_name = "cloud storage"

    @abstractmethod
    def upload(self, key, data, content_type=None):
        """
        Uploads ``data`` to ``key``, overwriting any existing object.

        Args:
            key (str): Object path, e.g. ``test_cases/7/01``.
            data (bytes): File contents.
            content_type (str, optional): MIME type to store with the object.

        Raises:
            StorageError: If the upload fails.
        """

    @abstractmethod
    def delete_prefix(self, prefix, keep=None):
        """
        Deletes every object whose key starts with ``prefix``, except those in ``keep``.

        Args:
            prefix (str): Key prefix, e.g. ``test_cases/7/``.
            keep (set[str], optional): Keys to leave in place.

        Returns:
            int: Number of objects deleted.

        Raises:
            StorageError: If listing or deleting fails.
        """
