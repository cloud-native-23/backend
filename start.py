import logging
import os
import sys

import uvicorn
from gunicorn.app.base import BaseApplication
from gunicorn.glogging import Logger
from loguru import logger

from app.core.config import settings
from app.main import app
from app.utils import number_of_workers

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
JSON_LOGS = os.environ.get("JSON_LOGS", "0") == 1 if settings.ENV else True
WORKERS = (
    os.environ.get("GUNICORN_WORKERS", 1)
    if settings.ENV == "dev"
    else number_of_workers()
)

logger.add(sink=sys.stdout, serialize=JSON_LOGS)
logger.add(
    sink="/backend/logs/concise/concise.log",
    enqueue=True,
    serialize=0,
    level="INFO",
    rotation="23:59",
)
logger.add(
    sink="/backend/logs/extend/extend.log",
    enqueue=True,
    serialize=0,
    backtrace=True,
    level="DEBUG",
    rotation="23:59",
)
logger.add(
    sink="/backend/logs/extend/extend-json.json",
    enqueue=True,
    serialize=1,
    level="DEBUG",
    rotation="23:59",
)
logger.add(
    sink="/backend/logs/error/error.log",
    enqueue=True,
    serialize=0,
    backtrace=True,
    level="ERROR",
    rotation="23:59",
)
logger.add(
    sink="/backend/logs/error/error-concise.log",
    enqueue=True,
    serialize=0,
    backtrace=False,
    level="ERROR",
    rotation="23:59",
)


logger.info("Current Environment: {}".format(settings.ENV))


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(LOG_LEVEL)
        self.access_logger.setLevel(LOG_LEVEL)


class StandaloneApplication(BaseApplication):
    """Our Gunicorn application."""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run():
    intercept_handler = InterceptHandler()
    # logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
    # logging.root.handlers = [intercept_handler]
    logging.root.setLevel(LOG_LEVEL)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    from pathlib import Path

    concise_path = os.path.join(*[os.getcwd(), "logs/concise"])
    extend_path = os.path.join(*[os.getcwd(), "logs/extend"])
    error_path = os.path.join(*[os.getcwd(), "logs/error"])
    Path(concise_path).mkdir(parents=True, exist_ok=True)
    Path(extend_path).mkdir(parents=True, exist_ok=True)
    Path(error_path).mkdir(parents=True, exist_ok=True)

    logger.info(f"log path: {concise_path}, {extend_path}, {error_path}")
    options = {
        "bind": "0.0.0.0:8000",
        "workers": WORKERS,
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
    }

    if settings.ENV == "dev":
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        StandaloneApplication(app, options).run()


if __name__ == "__main__":
    run()
