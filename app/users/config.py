from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    default_admin_email: str
    default_admin_password: str
    minimum_length_of_the_password: int = Field(default=8)


settings = Settings()
