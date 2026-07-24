from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./fulki.db"
    jwt_secret: str = "change-me-in-production"
    jwt_expire_days: int = 90
    # In dev mode the OTP is returned in the response instead of being sent by SMS.
    otp_dev_mode: bool = True
    free_download_limit: int = 3

    # AWS S3: audio is streamed by clients directly from S3 via presigned URLs.
    # Leave the key/secret empty to fall back to boto3's default credential chain
    # (IAM role, ~/.aws/credentials, AWS_* env vars), which is preferred in production.
    aws_region: str = "eu-west-3"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket_name: str = "fulki-audio"

    class Config:
        env_file = ".env"


settings = Settings()
