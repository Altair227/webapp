from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(str(ENV_FILE))


class LoggerConfig(BaseSettings):
    level: str = "DEBUG"
    dir: str | None = None
    size: int = 0
    count: int = 0
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s: %(lineno)d - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class PostgresConfig(BaseSettings):
    db: str
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}"
            f":{self.port}/{self.db}"
        )

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


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
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    logger: LoggerConfig = Field(default_factory=LoggerConfig)
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
