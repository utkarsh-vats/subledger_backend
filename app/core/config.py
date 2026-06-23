from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Database
    DB_USER: str = Field(alias="POSTGRES_USER")
    DB_PASSWORD: str = Field(alias="POSTGRES_PASSWORD")
    DB_NAME: str = Field(alias="POSTGRES_DB")
    DB_HOST: str = Field(alias="POSTGRES_HOST", default="db")
    DB_PORT: int = Field(alias="POSTGRES_PORT", default=5432, gt=0, lt=65536)

    # Redis
    REDIS_URL: str = Field(default="redis://redis:6379/0")

    # JWT
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)

    # Admin
    ADMIN_EMAIL: str = Field(default="admin@subledger.local")
    ADMIN_PASSWORD_HASH: str = Field(default="")

    @property
    def database_url(self) -> str:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        ).render_as_string(hide_password=False)
    

@lru_cache
def get_settings() -> Settings:
    return Settings()       # type: ignore[call-arg]
    
settings = get_settings()
