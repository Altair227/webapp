from flask import Blueprint, render_template


bp = Blueprint(
    "client_news",
    __name__,
    url_prefix="/news",
    template_folder="templates",
)


@bp.get("/")
def index():
    return render_template("client_news/index.html")
