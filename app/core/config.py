from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Book Lending System"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/book_lending"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
