"""
Cloud storage for migrated test cases.

Usage:
    from problems.storage import get_storage_backend, paths
    storage = get_storage_backend()          # provider chosen by STORAGE_PROVIDER
    storage.upload(paths.test_input_key(7, 1), b"1 2\n")
"""
from . import paths
from .base import StorageBackend, StorageError
from .factory import get_storage_backend

__all__ = ["get_storage_backend", "paths", "StorageBackend", "StorageError"]
