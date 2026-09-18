from flask import Blueprint, render_template, request
from .services import NewsService

bp = Blueprint(
    "client_news",
    __name__,
    template_folder="templates",
)


@bp.get("/")
def index():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 25))
    query = request.args.get("search", "").strip()
    data = NewsService.list(
        page=page,
        size=size,
        search=query,
    )
    return render_template("client_news/index.html", items=data)

@bp.route("/news-<_id>.html", methods=["GET"])
def view(_id):
    pass