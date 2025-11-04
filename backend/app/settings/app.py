from settings.logger import GunicornLogger
from fastapi import FastAPI
from gunicorn.app.base import BaseApplication


def get_app_options(
        host: str,
        port: int,
        timeout: int,
        workers: int,
        log_level: str,
) -> dict:
    return {
        "accesslog": "-",
        "errorlog": "-",
        "bind": f"{host}:{port}",
        "loglevel": log_level.upper(),
        "logger_class": GunicornLogger,
        "timeout": timeout,
        "workers": workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
    }


class Application(BaseApplication):
    def __init__(
            self,
            application: FastAPI,
            options: dict | None = None,
    ) -> None:
        self.options = options or {}
        self.application = application
        super().__init__()

    def load(self) -> FastAPI:
        return self.application

    @property
    def config_options(self) -> dict:
        return {
            k: v
            for k, v in self.options.items()
            if k in self.cfg.settings and v is not None
        }

    def load_config(self) -> None:
        for key, value in self.config_options.items():
            self.cfg.set(key.lower(), value)
