import secrets

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator, RedisDsn, PostgresDsn
from datetime import timedelta


class Settings(BaseSettings):
    # Dirs
    BASE_DIR: Optional[str] = Path(__file__).resolve().parent.parent.parent.as_posix()
    PROJECT_DIR: Optional[str] = Path(__file__).resolve().parent.parent.as_posix()
    # Project
    VERSION: Optional[str] = '0.1.0'
    DEBUG: Optional[bool] = False
    PAGINATION_MAX_SIZE: Optional[int] = 25

    DOMAIN: Optional[str] = 'localhost:8000'
    ENABLE_SSL: Optional[bool] = False
    SITE_URL: Optional[str] = 'http://localhost'
    ROOT_PATH: Optional[str] = ""
    ADMIN_ROOT_PATH: Optional[str] = ""
    SELLER_ROOT_PATH: Optional[str] = ""
    ROOT_PATH_IN_SERVERS: Optional[bool] = True
    API_V1_STR: Optional[str] = "/api/v1"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl
    BACKEND_CORS_ORIGINS: Optional[List[AnyHttpUrl]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: Optional[str] = 'project_name'
    SENTRY_DSN: Optional[AnyHttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SQLALCHEMY_TEST_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            host=values.get("DATABASE_HOST"),
            user=values.get("DATABASE_USER"),
            port=values.get("DATABASE_PORT"),
            password=values.get("DATABASE_PASSWORD"),
            path=f"/{values.get('DATABASE_NAME') or ''}",
        )

    @validator("SQLALCHEMY_TEST_DATABASE_URI", pre=True)
    def assemble_test_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            host=values.get("DATABASE_HOST"),
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            path='/test',
        )

    REDIS_HOST: Optional[str] = '127.0.0.1'
    REDIS_PORT: Optional[int] = 6379
    REDIS_URL: Optional[RedisDsn]

    @validator('REDIS_URL', pre=True)
    def assemble_redis_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return f'redis://{values.get("REDIS_HOST")}:{values.get("REDIS_PORT")}/0'

    SMTP_TLS: Optional[bool] = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = 'smtp.server.example'
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    SEND_MAIL_TO: Optional[str] = None

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: Optional[int] = 48
    EMAIL_TEMPLATES_DIR: Optional[str] = "app/email-templates/build"
    EMAILS_ENABLED: Optional[bool] = True

    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    LANGUAGE_CODE: Optional[str] = 'ru'
    LANGUAGE_CODE_LENGTH: Optional[int] = 5
    LANGUAGES: tuple = ('en', 'ru',)

    LOCALE: Dict[str, Any] = {
        'DIR': 'app/locale'
    }
    TIME_ZONE: Optional[str] = 'Asia/Ashgabat'
    USE_TZ: Optional[bool] = True

    DEFAULT_MAX_DIGITS: Optional[int] = 12
    DEFAULT_DECIMAL_PLACES: Optional[int] = 2
    DEFAULT_CURRENCY_CODE_LENGTH: Optional[int] = 3
    DEFAULT_CURRENCY_CODE: Optional[str] = 'USD'

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


class JWTSettings(BaseSettings):
    # Security
    JWT_SECRET_KEY: Optional[str] = secrets.token_urlsafe(32)
    # JWT
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    JWT_ALGORITHM: Optional[str] = "RS256"
    JWT_VERIFY: Optional[bool] = True
    JWT_VERIFY_EXPIRATION: Optional[bool] = True
    JWT_LEEWAY: Optional[int] = 0
    JWT_ARGUMENT_NAME: Optional[str] = 'token'
    # 60 minutes * 24 hours * 8 days = 8 days
    JWT_EXPIRATION_DELTA: timedelta = timedelta(minutes=5.0)
    JWT_ALLOW_REFRESH: Optional[bool] = True
    JWT_REFRESH_EXPIRATION_DELTA: Optional[timedelta] = timedelta(days=7)
    JWT_PASSWORD_RESET_EXPIRATION_DELTA: Optional[timedelta] = timedelta(days=1)
    JWT_AUTH_HEADER_NAME: Optional[str] = 'HTTP_AUTHORIZATION'
    JWT_AUTH_HEADER_PREFIX: str = 'Bearer'
    # Helper functions
    JWT_PASSWORD_VERIFY: Optional[str] = 'app.utils.security.verify_password'
    JWT_PASSWORD_HANDLER: Optional[str] = 'app.utils.security.get_password_hash'
    JWT_PAYLOAD_HANDLER: Optional[str] = 'app.utils.security.jwt_payload'
    JWT_ENCODE_HANDLER: Optional[str] = 'app.utils.security.jwt_encode'
    JWT_DECODE_HANDLER: Optional[str] = 'app.utils.security.jwt_decode'
    JWT_AUDIENCE: Optional[str] = 'client'
    JWT_AUDIENCE_ADMIN: Optional[str] = 'admin'
    JWT_ISSUER: Optional[str] = 'backend'

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


class StructureSettings(BaseSettings):
    # Dirs
    BASE_DIR: Optional[str] = Path(__file__).resolve().parent.parent.parent.as_posix()
    PROJECT_DIR: Optional[str] = Path(__file__).resolve().parent.parent.as_posix()
    MEDIA_DIR: Optional[str] = 'media'  # Without end slash
    PROTECTED_DIR: Optional[str] = 'protected'  # Without end slash
    MEDIA_URL: Optional[str] = '/media/'

    STATIC_DIR: Optional[str] = 'static'
    STATIC_URL: Optional[str] = '/static/'

    TEMPLATES: Optional[dict] = {
        'DIR': 'templates'
    }

    TEMP_PATH: Optional[str] = 'temp/'

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
jwt_settings = JWTSettings()
structure_settings = StructureSettings()
