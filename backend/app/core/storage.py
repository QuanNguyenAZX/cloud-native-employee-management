from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import quote, urlencode, urlsplit, urlunsplit

import httpx

from app.core.config import settings


class StorageError(RuntimeError):
    pass


def _is_configured() -> bool:
    return bool(
        settings.OBJECT_STORAGE_BUCKET
        and settings.OBJECT_STORAGE_ENDPOINT
        and settings.OBJECT_STORAGE_ACCESS_KEY
        and settings.OBJECT_STORAGE_SECRET_KEY
    )


def _parse_endpoint() -> tuple[str, str, str, bool]:
    if not settings.OBJECT_STORAGE_ENDPOINT:
        raise StorageError("Object storage endpoint is not configured")
    parsed = urlsplit(settings.OBJECT_STORAGE_ENDPOINT)
    if not parsed.scheme or not parsed.netloc:
        raise StorageError("Object storage endpoint is invalid")
    host = parsed.netloc
    path_style = settings.OBJECT_STORAGE_FORCE_PATH_STYLE or parsed.port is not None
    return parsed.scheme, host, parsed.path.rstrip("/"), path_style


def _amz_date(now: datetime | None = None) -> tuple[str, str]:
    current = now or datetime.now(timezone.utc)
    return current.strftime("%Y%m%dT%H%M%SZ"), current.strftime("%Y%m%d")


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _signing_key(secret_key: str, date_stamp: str, region: str) -> bytes:
    k_date = _sign(f"AWS4{secret_key}".encode(), date_stamp)
    k_region = _sign(k_date, region)
    k_service = _sign(k_region, "s3")
    return _sign(k_service, "aws4_request")


def _canonical_uri(key: str, path_style: bool, *, bucket_only: bool = False) -> str:
    if bucket_only:
        if path_style:
            if not settings.OBJECT_STORAGE_BUCKET:
                raise StorageError("Object storage bucket is not configured")
            return f"/{settings.OBJECT_STORAGE_BUCKET}"
        return "/"
    encoded_key = quote(key, safe="/~")
    if not settings.OBJECT_STORAGE_BUCKET:
        raise StorageError("Object storage bucket is not configured")
    if path_style:
        return f"/{settings.OBJECT_STORAGE_BUCKET}/{encoded_key}"
    return f"/{encoded_key}"


def _host(path_style: bool, base_host: str) -> str:
    if path_style:
        return base_host
    if not settings.OBJECT_STORAGE_BUCKET:
        raise StorageError("Object storage bucket is not configured")
    return f"{settings.OBJECT_STORAGE_BUCKET}.{base_host}"


def build_object_url(key: str) -> str | None:
    if not _is_configured():
        return None
    return create_presigned_url(
        method="GET",
        key=key,
        expires_in=settings.AVATAR_URL_EXPIRE_SECONDS,
    )


def create_presigned_url(
    *,
    method: str,
    key: str,
    expires_in: int,
    bucket_only: bool = False,
) -> str:
    if not _is_configured():
        raise StorageError("Object storage is not configured")

    scheme, base_host, base_path, path_style = _parse_endpoint()
    host = _host(path_style, base_host)
    canonical_uri = _canonical_uri(key, path_style, bucket_only=bucket_only)
    amz_date, date_stamp = _amz_date()
    credential_scope = f"{date_stamp}/{settings.OBJECT_STORAGE_REGION}/s3/aws4_request"
    params = {
        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        "X-Amz-Credential": f"{settings.OBJECT_STORAGE_ACCESS_KEY}/{credential_scope}",
        "X-Amz-Date": amz_date,
        "X-Amz-Expires": str(expires_in),
        "X-Amz-SignedHeaders": "host",
    }
    canonical_query = urlencode(sorted(params.items()))
    canonical_headers = f"host:{host}\n"
    canonical_request = "\n".join(
        [
            method.upper(),
            canonical_uri,
            canonical_query,
            canonical_headers,
            "host",
            "UNSIGNED-PAYLOAD",
        ]
    )
    string_to_sign = "\n".join(
        [
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ]
    )
    signature = hmac.new(
        _signing_key(
            settings.OBJECT_STORAGE_SECRET_KEY or "",
            date_stamp,
            settings.OBJECT_STORAGE_REGION,
        ),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    params["X-Amz-Signature"] = signature
    query_string = urlencode(params)
    path = f"{base_path}{canonical_uri}" if base_path else canonical_uri
    return urlunsplit((scheme, host, path, query_string, ""))


@lru_cache(maxsize=1)
def ensure_bucket_exists() -> None:
    if not _is_configured():
        return
    url = create_presigned_url(
        method="PUT",
        key="",
        expires_in=900,
        bucket_only=True,
    )
    response = httpx.put(url, timeout=30)
    if response.status_code in {200, 201, 204, 409}:
        return
    if response.status_code >= 300:
        raise StorageError(
            f"Failed to create bucket: {response.status_code} {response.text}"
        )


def upload_object(*, key: str, content: bytes, content_type: str | None = None) -> None:
    ensure_bucket_exists()
    url = create_presigned_url(method="PUT", key=key, expires_in=900)
    headers = {"Content-Type": content_type} if content_type else None
    response = httpx.put(url, content=content, headers=headers, timeout=30)
    if response.status_code >= 300:
        raise StorageError(
            f"Failed to upload object: {response.status_code} {response.text}"
        )


def delete_object(*, key: str) -> None:
    url = create_presigned_url(method="DELETE", key=key, expires_in=900)
    response = httpx.delete(url, timeout=30)
    if response.status_code >= 300 and response.status_code != 404:
        raise StorageError(
            f"Failed to delete object: {response.status_code} {response.text}"
        )


def create_avatar_key(*, user_id: str, suffix: str | None = None) -> str:
    token = secrets.token_urlsafe(16)
    extension = suffix or ".jpg"
    if extension and not extension.startswith("."):
        extension = f".{extension}"
    return f"avatars/{user_id}/{token}{extension}"
