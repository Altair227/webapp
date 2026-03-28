from flask import Blueprint
from app.utils.modules import register_child_blueprints
import app.modules.admin.modules as admin_modules


bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
)
register_child_blueprints(bp, admin_modules)
