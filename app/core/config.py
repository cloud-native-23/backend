from typing import List, Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    # app
    APP_NAME: str = "stadium-matching-backend"
    API_V1_STR: str = "/api/v1"
    ENV: str
    test_int: int = 50
    POOL_SIZE: int
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:4200",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://localhost",
        "https://localhost:4200",
        "https://localhost:3000",
        "https://localhost:8080",
        "https://104.199.134.61:3000",
        "http://104.199.134.61:3000",
        # "http://backend.sdm-teamatch.com/",
        # "https://stag.sdm-teamatch.com/",
        # "https://sdm-teamatch.com/",
        # "https://app.sdm-teamatch.com/",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # database
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_HOSTNAME: str

    ADMIN_EMAIL: str
    ADMIN_NAME: str
    ADMIN_PASSWORD: str
    

    # auth
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    JWT_ALGORITHM: str
    SESSION_DURATION: str

    SECRET_KEY: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_SECRET_KEY: str

    # origin
    CLIENT_ORIGIN: str

    class Config:
        env_file = "./.env"


settings = Settings()