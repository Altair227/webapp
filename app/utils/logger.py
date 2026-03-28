import logging
from logging.handlers import RotatingFileHandler
from app.config import LoggerConfig
from typing import ClassVar
from pathlib import Path


class Logger:
    _instances: ClassVar[dict[str, logging.Logger]] = {}

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        if name not in cls._instances:
            cls._instances[name] = cls._create(name=name)
        return cls._instances[name]

    @classmethod
    def init(cls, name: str, config: LoggerConfig) -> logging.Logger:
        cls._instances[name] = cls._create(name=name, config=config)
        return cls._instances[name]

    @classmethod
    def _create(
        cls, name: str, config: LoggerConfig | None = None
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logging_level = config.level if config else logging.DEBUG
        logging_format = (
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s",
        )
        if config:
            logging_format = config.format
        logging_date_format = "%Y-%m-%d %H:%M:%S"
        if config:
            logging_date_format = config.date_format

        logger.setLevel(logging_level)
        logger.handlers.clear()
        formatter = logging.Formatter(
            fmt=logging_format,
            datefmt=logging_date_format,
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        if not config or not config.dir:
            return logger
        logging_dir = Path(config.dir)
        logging_dir.mkdir(parents=True, exist_ok=True)
        levels = {
            "access": logging.INFO,
            "error": logging.ERROR,
        }
        for filename, level in levels.items():
            logging_path = Path.joinpath(logging_dir, f"{filename}.log")
            handler = RotatingFileHandler(
                logging_path,
                maxBytes=config.size,
                backupCount=config.count,
            )
            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger


def init_logger(config: LoggerConfig, name: str = "app") -> logging.Logger:
    return Logger.init(name=name, config=config)


def get_logger(name: str = "app") -> logging.Logger:
    return Logger.get_logger(name=name)
