import logging
from pathlib import Path

from flask import Flask, Response, render_template, send_from_directory
from werkzeug.exceptions import HTTPException

import app.modules as app_pkg
from app.config import get_config
from app.database import shutdown_session
from app.utils.logger import init_logger
from app.utils.mailer import get_mailer
from app.utils.modules import register_child_blueprints


BASE_DIR = Path(__file__).resolve().parent.parent  # .../app
UPLOAD_DIR = BASE_DIR / "web" / "upload"


def create_app() -> Flask:
    config = get_config()
    logger = init_logger(config.logger)
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="assets",
        static_url_path="/static",
    )
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["MAIL_SERVER"] = config.mailer.host
    app.config["MAIL_PORT"] = config.mailer.port
    app.config["MAIL_USE_TLS"] = config.mailer.tls
    app.config["MAIL_USERNAME"] = config.mailer.user
    app.config["MAIL_PASSWORD"] = config.mailer.password
    app.config["MAIL_DEFAULT_SENDER"] = config.mailer.sender
    mailer = get_mailer()
    mailer.init_app(app)
    register_child_blueprints(app, app_pkg, routes_module_name="main")
    # host/port only: the mailer config also holds the SMTP password
    logger.info("Mailer: %s:%s", config.mailer.host, config.mailer.port)

    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    app.logger.propagate = False

    wz = logging.getLogger("werkzeug")
    wz.handlers = logger.handlers
    wz.setLevel(logger.level)
    wz.propagate = False

    app.config["SECRET_KEY"] = config.secret_key
    app.teardown_appcontext(shutdown_session)
    app.config["UPLOAD_DIR"] = str(UPLOAD_DIR)

    @app.route("/upload/<path:filename>")
    def uploaded_file(filename: str) -> Response:
        return send_from_directory(app.config["UPLOAD_DIR"], filename)

    @app.errorhandler(404)
    def error_404(error: HTTPException) -> tuple[str, int]:
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(400)
    def error_400(error: HTTPException) -> tuple[str, int]:
        return render_template("errors/400.html", error=error), 400

    return app
