from gunicorn.app.base import BaseApplication
import os
from app.main import app as flask_app


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.app = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.app


if __name__ == "__main__":
    options = flask_app.config["GUNICORN_OPTIONS"].copy()
    options["bind"] = f"{HOST}:{PORT}"

    StandaloneApplication(flask_app, options).run()
