from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str
    project_path: str = Field(default="/opt/projects/app")
    logs_path: str = Field(default="/opt/projects/app/logs/access.log")
    cors_origin: list = Field(default=["http://localhost", "http://localhost:3000"])

    def is_production(self) -> bool:
        return self.environment == "production"

    def is_development(self) -> bool:
        return self.environment == "dev"

    def is_testing(self) -> bool:
        return self.environment == "test"


settings = Settings()
