"""
Storage factory: builds the backend named by the ``STORAGE_PROVIDER`` setting.

Switching provider only requires changing ``STORAGE_PROVIDER`` in ``.env``.
Adding a provider: implement ``StorageBackend`` in a new module, write a
``_build_<name>`` function below, and register it in ``_PROVIDERS``.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _require(provider, *names):
    """Returns the values of the given settings, failing clearly if any is empty."""
    missing = [name for name in names if not getattr(settings, name, None)]
    if missing:
        raise ImproperlyConfigured(
            f"Storage provider '{provider}' needs these .env settings: {', '.join(missing)}"
        )
    return [getattr(settings, name) for name in names]


def _build_s3():
    from .s3 import S3Storage

    (bucket,) = _require("s3", "AWS_S3_BUCKET_NAME")
    return S3Storage(
        bucket_name=bucket,
        region=settings.AWS_REGION,
        access_key_id=settings.AWS_ACCESS_KEY_ID,
        secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def _build_azure():
    from .azure_blob import AzureBlobStorage

    account_url, container, tenant, client, username, password = _require(
        "azure",
        "AZURE_STORAGE_ACCOUNT_URL", "AZURE_CONTAINER_NAME", "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID", "AZURE_USERNAME", "AZURE_PASSWORD",
    )
    return AzureBlobStorage(account_url, container, tenant, client, username, password)


# Provider name (value of STORAGE_PROVIDER) -> function that builds its backend.
_PROVIDERS = {
    "s3": _build_s3,
    "azure": _build_azure,
}


def get_storage_backend(provider=None):
    """
    Builds the storage backend for ``provider`` (defaults to ``settings.STORAGE_PROVIDER``).

    Returns:
        StorageBackend: A ready-to-use backend.

    Raises:
        ImproperlyConfigured: If the provider is unknown or its settings are missing.
    """
    name = (provider or settings.STORAGE_PROVIDER or "").strip().lower()
    try:
        builder = _PROVIDERS[name]
    except KeyError:
        raise ImproperlyConfigured(
            f"Unknown STORAGE_PROVIDER '{name}'. Supported values: {', '.join(sorted(_PROVIDERS))}."
        ) from None
    return builder()
