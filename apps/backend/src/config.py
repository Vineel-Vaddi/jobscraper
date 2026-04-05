from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # MinIO
    MINIO_BUCKET_NAME: str
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str = "us-east-1"
    
    # Backend
    SECRET_KEY: str
    FRONTEND_URL: str
    
    # Auth
    MOCK_LINKEDIN: bool = False
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
