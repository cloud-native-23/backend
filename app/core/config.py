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
        "http://localhost/",
        "http://localhost:4200/",
        "http://localhost:3000/",
        "http://localhost:8080/",
        "https://localhost/",
        "https://localhost:4200/",
        "https://localhost:3000/",
        "https://localhost:8080/",
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
# import json
# import os
# from typing import Any, Dict, List, Optional, Union

# import loguru
# from google.cloud import secretmanager
# from google.oauth2 import service_account
# from pydantic import AnyHttpUrl, BaseSettings, validator

# GCS_APP_KEY = "./app/core/k8s-codelab-381104-86fe71c3464f.json"


# def get_google_cloud_secret(key) -> Optional[str]:
#     # if not os.getenv(GCS_APP_KEY):
#     #     print('in first if!!!!')
#     #     LOGGER.debug("Not fetching secret from GCS: %s not present", GCS_APP_KEY)
#     #     return
#     try:
#         # only for dev test
#         if os.path.exists(GCS_APP_KEY):
#             credentials = service_account.Credentials.from_service_account_file(
#                 GCS_APP_KEY
#             )
#             loguru.logger.info(GCS_APP_KEY)
#             client = secretmanager.SecretManagerServiceClient(credentials=credentials)
#         # no need using credentials when deployed to GCP
#         else:
#             client = secretmanager.SecretManagerServiceClient()
#         response = client.access_secret_version(name=key)
#         return response.payload.data.decode()
#     except KeyError as e:
#         print("Error: ", e)


# def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
#     """
#     A simple settings source that loads variables from a JSON file
#     at the project's root.

#     Here we happen to choose to use the `env_file_encoding` from Config
#     when reading `config.json`
#     """
#     env_json_str = get_google_cloud_secret(
#         "projects/993698511015/secrets/teamatch-secret/versions/latest"
#     )
#     env_json = json.loads(env_json_str)
#     # print("secret from google cloud secret manager >>> ", env_json)
#     return env_json


# class Settings(BaseSettings):
#     # app
#     APP_NAME: str = "teamatch-backend"
#     API_V1_STR: str = "/api/v1"
#     ENV: str
#     test_int: int = 50
#     POOL_SIZE: int
#     BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
#         "http://localhost/",
#         "http://localhost:4200/",
#         "http://localhost:3000/",
#         "http://localhost:8080/",
#         "https://localhost/",
#         "https://localhost:4200/",
#         "https://localhost:3000/",
#         "https://localhost:8080/",
#         "http://backend.sdm-teamatch.com/",
#         "https://stag.sdm-teamatch.com/",
#         "https://sdm-teamatch.com/",
#         "https://app.sdm-teamatch.com/",
#     ]

#     @validator("BACKEND_CORS_ORIGINS", pre=True)
#     def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
#         if isinstance(v, str) and not v.startswith("["):
#             return [i.strip() for i in v.split(",")]
#         elif isinstance(v, (list, str)):
#             return v
#         raise ValueError(v)

#     # database
#     DATABASE_PORT: int
#     POSTGRES_PASSWORD: str
#     POSTGRES_USER: str
#     POSTGRES_DB: str
#     POSTGRES_HOST: str
#     POSTGRES_HOSTNAME: str

#     ADMIN_EMAIL: str
#     ADMIN_NAME: str
#     ADMIN_PASSWORD: str

#     # auth
#     JWT_PUBLIC_KEY: str
#     JWT_PRIVATE_KEY: str
#     ACCESS_TOKEN_EXPIRE_MINUTES: int
#     REFRESH_TOKEN_EXPIRE_MINUTES: int
#     JWT_ALGORITHM: str
#     SESSION_DURATION: str

#     SECRET_KEY: str

#     GOOGLE_CLIENT_ID: str
#     GOOGLE_CLIENT_SECRET: str
#     GOOGLE_SECRET_KEY: str

#     # origin
#     CLIENT_ORIGIN: str

#     # new add
#     WATCHFILES_FORCE_POLLING: bool
#     GUNICORN_WORKERS: int
#     JSON_LOGS: str
#     LOG_LEVEL: str
#     PRE_COMMIT_HOME: str
#     RABBITMQ_HOST: str

#     class Config:
#         @classmethod
#         def customise_sources(
#             cls,
#             init_settings,
#             env_settings,
#             file_secret_settings,
#         ):
#             return (
#                 init_settings,
#                 json_config_settings_source,
#                 env_settings,
#                 file_secret_settings,
#             )


# settings = Settings()
# # print('settings >>> ', settings)
