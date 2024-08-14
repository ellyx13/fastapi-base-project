from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str
    base_url: str = Field(default="http://api-test")


settings = Settings()
