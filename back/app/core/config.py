from pydantic_settings import BaseSettings
import dotenv
import os

dotenv.load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS"))

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")

    APP_ENV: str = os.getenv("APP_ENV")
    DEBUG: bool = os.getenv("DEBUG") == "True"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
