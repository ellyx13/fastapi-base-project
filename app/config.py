from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str
    database_url: str
    project_path: str = Field(default="/opt/projects/app")
    logs_path: str = Field(default="/opt/projects/app/logs/access.log")
    cors_origin: list = Field(default=["http://localhost", "http://localhost:3000"]) # List of allowed origins

settings = Settings()
