from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    access_token_expire_day: int = Field(default=3)
    secret_key: str
    algorithm: str


settings = Settings()
