from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
)
from app.modules.admin.decorators import auth_required
from .services import NewsService
from .forms import NewsForm

bp = Blueprint(
    "admin_news",
    __name__,
    url_prefix="/news",
    template_folder="templates",
)


@bp.get("/")
@auth_required(True, "admin.admin_auth.login")
def index():
    return render_template("admin_news/index.html")


@bp.route("/search")
@auth_required(True, "admin.admin_auth.login")
def search():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 25))
    query = request.args.get("search", "").strip()
    sort_field = request.args.get("sort[0][field]")
    direction = request.args.get("sort[0][dir]")
    total, data = NewsService.list(
        page=page,
        size=size,
        search=query,
        field=sort_field,
        direction=direction,
    )
    return jsonify(
        {
            "last_page": total,
            "data": data,
        }
    )


@bp.route("/create", methods=["GET", "POST"])
@auth_required(True, "admin.admin_auth.login")
def create():
    form = NewsForm()
    if form.validate_on_submit():
        error = NewsService.create(
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            published_at=form.published_at.data,
        )
        if not error:
            return redirect(url_for("admin.admin_news.index"))
        flash(error, "error")
    return render_template("admin_news/create.html", form=form, is_create=True)
