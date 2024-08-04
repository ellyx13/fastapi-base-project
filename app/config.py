from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    environment: str
    project_path: str = Field(default='/opt/projects/app')
    logs_path: str = Field(default='/opt/projects/app/logs/access.log')
    
    
settings = Settings()