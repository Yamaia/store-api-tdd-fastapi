from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    title: str = "Store API"
    version: str = "1.0.0"
    root_path: str = ""
    database_url: str = "mongodb://localhost:27017"
    database_name: str = "store"


settings = Settings()
