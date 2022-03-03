from pydantic import BaseSettings


class Settings(BaseSettings):
    db_args: str = '{"check_same_thread": false}'
    db_url: str = "sqlite:///sample.db"


settings = Settings()
