from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://muzakarah:muzakarah@localhost:5432/muzakarah_db"
    secret_key: str = "dev-secret-key-change-in-production"
    encryption_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/callback"
    frontend_url: str = "http://localhost:5173"
    admin_email: str = "asifaliarif2526@gmail.com"
    meilisearch_url: str = "http://127.0.0.1:7700"
    meilisearch_api_key: str = "masterKey"
    cors_origins: str = "http://localhost:5173,http://localhost:8000"
    access_token_expire_minutes: int = 60 * 24 * 7

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
