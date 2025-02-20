from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ownership_field: str = "created_by"


settings = Settings()
