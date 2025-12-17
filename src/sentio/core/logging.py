import logging
import logging.config

from pythonjsonlogger.json import jsonlogger

from sentio.core.config import Settings


class JsonFormatter(jsonlogger.JsonFormatter):
    pass


def get_logging_config(settings: Settings) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
                "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": settings.log_level,
            }
        },
        "root": {
            "handlers": ["console"],
            "level": settings.log_level,
        },
        "loggers": {
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }


def setup_logging(settings: Settings) -> None:
    config = get_logging_config(settings)
    logging.config.dictConfig(config)
