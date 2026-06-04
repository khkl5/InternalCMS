from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from supabase import create_client


@lru_cache(maxsize=1)
def get_supabase_client():
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise ImproperlyConfigured("Supabase service credentials are not configured.")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def upload_file(file_obj, path):
    file_obj.seek(0)
    return (
        get_supabase_client()
        .storage.from_(settings.SUPABASE_STORAGE_BUCKET)
        .upload(
            path=path,
            file=file_obj.read(),
            file_options={
                "content-type": getattr(file_obj, "content_type", None)
                or "application/octet-stream",
                "upsert": "false",
            },
        )
    )


def create_signed_file_url(path, expires_in=None):
    if not path:
        return ""

    response = (
        get_supabase_client()
        .storage.from_(settings.SUPABASE_STORAGE_BUCKET)
        .create_signed_url(
            path=path,
            expires_in=expires_in or settings.SIGNED_URL_TTL_SECONDS,
        )
    )
    if isinstance(response, dict):
        return (
            response.get("signedURL")
            or response.get("signedUrl")
            or response.get("signed_url")
            or ""
        )
    return getattr(response, "signed_url", "") or ""


def delete_file(path):
    if path:
        return (
            get_supabase_client()
            .storage.from_(settings.SUPABASE_STORAGE_BUCKET)
            .remove([path])
        )
    return None
