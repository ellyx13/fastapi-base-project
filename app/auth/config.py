from pydantic import Field
from pydantic_settings import BaseSettings

PUBLIC_APIS = [
    "/docs",
    "/openapi.json",
    "/redoc",
    "/v1/health/ping",
    "/v1/users/register",
    "/v1/users/login",
]


class Settings(BaseSettings):
    access_token_expire_day: int = Field(default=3)
    secret_key: str
    algorithm: str


settings = Settings()
