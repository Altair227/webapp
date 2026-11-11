from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.wrappers import Response as BaseResponse

from app.modules.admin.decorators import auth_required, breadcrumbs

from .forms import NewsForm
from .services import NewsService


bp = Blueprint(
    "admin_news",
    __name__,
    url_prefix="/news",
    template_folder="templates",
)


@bp.before_request
def crumbs() -> None:
    g.breadcrumbs.append(("News", url_for("admin.admin_news.index")))


@bp.get("/")
@auth_required(True, "admin.admin_auth.login")
def index() -> str:
    return render_template("admin_news/index.html")


@bp.route("/search")
@auth_required(True, "admin.admin_auth.login")
def search() -> Response:
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 25))
    query = request.args.get("search", "").strip()
    sort_field = request.args.get("sort[0][field]")
    direction = request.args.get("sort[0][dir]")
    total, data = NewsService.get_list(
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
@breadcrumbs("Create news")
def create() -> str | BaseResponse:
    form = NewsForm()
    if form.validate_on_submit():
        error = NewsService.create(
            # DataRequired() guarantees strings; `or ""` narrows the type
            title=form.title.data or "",
            description=form.description.data or "",
            content=form.content.data or "",
            published_at=form.published_at.data,
            image_url=form.image_url.data,
            images=form.images.data,
        )
        if not error:
            return redirect(url_for("admin.admin_news.index"))
        flash(error, "error")
    return render_template("admin_news/create.html", form=form, is_create=True)


@bp.route("/update/<_id>", methods=["GET", "POST"])
@auth_required(True, "admin.admin_auth.login")
@breadcrumbs("Update news")
def update(_id: str) -> str | BaseResponse:
    data = NewsService.get_by_id(int(_id))
    if not data:
        abort(404, description="News not found")
    form = NewsForm(obj=data)
    if form.validate_on_submit():
        error = NewsService.update(
            _id=data.id,
            # DataRequired() guarantees strings; `or ""` narrows the type
            title=form.title.data or "",
            description=form.description.data or "",
            content=form.content.data or "",
            published_at=form.published_at.data,
            image_url=form.image_url.data,
            images=form.images.data,
        )
        if not error:
            return redirect(url_for("admin.admin_news.index"))
        flash(error, "error")
    return render_template(
        "admin_news/update.html", form=form, is_create=False
    )


@bp.route("/view/<_id>", methods=["GET"])
@auth_required(True, "admin.admin_auth.login")
@breadcrumbs("View news")
def view(_id: str) -> str:
    data = NewsService.get_by_id(int(_id))
    if not data:
        abort(404, description="News not found")
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("admin_news/content.html", data=data)
    return render_template("admin_news/view.html", data=data)


@bp.route("/remove/<_id>", methods=["DELETE"])
@auth_required(True, "admin.admin_auth.login")
def remove(_id: str) -> tuple[str, int]:
    message = NewsService.remove([int(_id)])
    if message:
        abort(404, description=message)
    return "", 200


@bp.route("/bulk-remove", methods=["DELETE"])
@auth_required(True, "admin.admin_auth.login")
def bulk_remove() -> tuple[str, int]:
    ids = request.get_json(force=True).get("ids", [])
    message = NewsService.remove(ids)
    if message:
        abort(404, description=message)
    return "", 200


@bp.route("/resume/<_id>", methods=["PUT"])
@auth_required(True, "admin.admin_auth.login")
def resume(_id: str) -> tuple[str, int]:
    message = NewsService.resume([int(_id)])
    if message:
        abort(404, description=message)
    return "", 200


@bp.route("/bulk-resume", methods=["PUT"])
@auth_required(True, "admin.admin_auth.login")
def bulk_resume() -> tuple[str, int]:
    ids = request.get_json(force=True).get("ids", [])
    message = NewsService.resume(ids)
    if message:
        abort(404, description=message)
    return "", 200
