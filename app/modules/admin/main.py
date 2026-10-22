from flask import Blueprint, session, g, url_for, redirect, request
from app.utils.modules import register_child_blueprints
import app.modules.admin.modules as admin_modules
from app.models import Admin
from app.database import db_session

bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
)
register_child_blueprints(bp, admin_modules)


@bp.before_request
def load_user():
    user_id = session.get("user_id")
    if not user_id:
        g.user = None
        return
    g.user = (
        db_session.query(Admin)
        .filter(
            Admin.id == user_id,
            Admin.is_activated == True,
            Admin.is_blocked == False,
            Admin.is_deleted == False,
        )
        .first()
    )


# Endpoints available without login (login, forgot, restore...)
PUBLIC_PREFIX = "admin.admin_auth."


@bp.before_request
def require_auth():
    if g.user is not None:
        return None
    if (request.endpoint or "").startswith(PUBLIC_PREFIX):
        return None
    return redirect(url_for("admin.admin_auth.login"))


@bp.context_processor
def inject_user():
    return dict(current_user=g.user)


@bp.before_request
def base_breadcrumbs():
    g.breadcrumbs = [("Admin", url_for("admin.admin_dashboard.index"))]


@bp.route("/", strict_slashes=False)
def index():
    return redirect(url_for("admin.admin_dashboard.index"))
