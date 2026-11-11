from flask import Blueprint, g, redirect, request, session, url_for
from werkzeug.wrappers import Response as BaseResponse

import app.modules.admin.modules as admin_modules
from app.database import db_session
from app.models import Admin
from app.utils.modules import register_child_blueprints


bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
)
register_child_blueprints(bp, admin_modules)


@bp.before_request
def load_user() -> None:
    user_id = session.get("user_id")
    if not user_id:
        g.user = None
        return
    g.user = (
        db_session.query(Admin)
        .filter(
            Admin.id == user_id,
            Admin.is_activated.is_(True),
            Admin.is_blocked.is_(False),
            Admin.is_deleted.is_(False),
        )
        .first()
    )


# Endpoints available without login (login, forgot, restore...)
PUBLIC_PREFIX = "admin.admin_auth."


@bp.before_request
def require_auth() -> BaseResponse | None:
    if g.user is not None:
        return None
    if (request.endpoint or "").startswith(PUBLIC_PREFIX):
        return None
    return redirect(url_for("admin.admin_auth.login"))


@bp.context_processor
def inject_user() -> dict[str, Admin | None]:
    return dict(current_user=g.user)


@bp.before_request
def base_breadcrumbs() -> None:
    g.breadcrumbs = [("Admin", url_for("admin.admin_dashboard.index"))]


@bp.route("/", strict_slashes=False)
def index() -> BaseResponse:
    return redirect(url_for("admin.admin_dashboard.index"))
