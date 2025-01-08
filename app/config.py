from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_string: str = "postgresql://postgres:will@localhost/lc-100"


settings = Settings()
