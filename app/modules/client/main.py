from flask import Blueprint
from app.utils.modules import register_child_blueprints
import app.modules.client.modules as client_modules


bp = Blueprint(
    "client",
    __name__,
    template_folder="templates",
)
register_child_blueprints(bp, client_modules)
