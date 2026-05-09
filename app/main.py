import logging
from app.database import shutdown_session
from flask import Flask, render_template
from app.config import get_config
from app.utils.logger import init_logger
from app.utils.modules import register_child_blueprints
import app.modules as app_pkg
from app.utils.mailer import get_mailer


def create_app() -> Flask:
    config = get_config()
    logger = init_logger(config.logger)
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="assets",
        static_url_path="/static",
    )
    app.config['MAIL_SERVER'] = config.mailer.host
    app.config['MAIL_PORT'] = config.mailer.port
    app.config['MAIL_USE_TLS'] = config.mailer.tls
    app.config['MAIL_USERNAME'] = config.mailer.user
    app.config['MAIL_PASSWORD'] = config.mailer.password
    mailer=get_mailer()
    mailer.init_app(app)
    register_child_blueprints(app, app_pkg, routes_module_name="main")


    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    app.logger.propagate = False

    wz = logging.getLogger("werkzeug")
    wz.handlers = logger.handlers
    wz.setLevel(logger.level)
    wz.propagate = False

    app.config["SECRET_KEY"] = config.secret_key
    app.teardown_appcontext(shutdown_session)

    @app.route("/")
    def index():
        return render_template("index.html", title="Main page")

    @app.errorhandler(404)
    def error_404(error):
        return render_template("errors/404.html"), 404

    return app
