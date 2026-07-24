import boto3

from ..config import settings

EXPIRY_SEC = 6 * 3600

_s3_client = None


def _client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
    return _s3_client


def signed_url(audio_path: str) -> tuple[str, int]:
    """Builds a time-limited S3 presigned GET URL so audio never transits through the API."""
    url = _client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": audio_path},
        ExpiresIn=EXPIRY_SEC,
    )
    return url, EXPIRY_SEC
