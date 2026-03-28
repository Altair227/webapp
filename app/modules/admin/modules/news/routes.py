from flask import Blueprint, render_template


bp = Blueprint(
    "admin_news",
    __name__,
    url_prefix="/news",
    template_folder="templates",
)


@bp.get("/")
def index():
    return render_template("admin_news/index.html")
