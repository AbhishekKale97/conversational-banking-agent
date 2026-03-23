from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    google_api_key: str = Field(
        ...,
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    )
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")
    app_env: str = Field(default="dev", alias="APP_ENV")
    faq_data_path: Path = Field(default=BASE_DIR / "data" / "faqs.json")
    kb_data_path: Path = Field(default=BASE_DIR / "data" / "knowledge_base.md")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
