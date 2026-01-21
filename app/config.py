from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(str(ENV_FILE))


class SqliteConfig(BaseSettings):
    db: str

    @property
    def dsn(self) -> str:
        return f"sqlite:///{self.db}"

    model_config = SettingsConfigDict(
        env_prefix="SQLITE_",
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class Config(BaseSettings):
    sqlite: SqliteConfig = Field(default_factory=SqliteConfig)

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )


@lru_cache
def get_config() -> Config:
    return Config()
