from flask import (
    Blueprint,
    render_template,
    flash,
    request,
    abort,
    redirect,
    url_for,
)
from app.modules.admin.decorators import auth_required

bp = Blueprint(
    "admin_dashboard",
    __name__,
    url_prefix="/dashboard",
    template_folder="templates",
)


@bp.route("/", methods=["GET"])
@auth_required(True, "admin.admin_auth.login")
def index():
    return render_template("admin_dashboard/index.html")
