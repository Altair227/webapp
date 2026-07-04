from flask import (
    Blueprint,
    render_template,
    flash,
    request,
    abort,
    redirect,
    url_for,
)
from .forms import LoginForm, ForgotForm
from .services import AuthService
from app.modules.admin.decorators import auth_required

bp = Blueprint(
    "admin_auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
)


@bp.route("/login", methods=["GET", "POST"])
@auth_required(False, "admin.admin_dashboard.index")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user, error = AuthService.login(
            email=form.email.data,
            password=form.password.data,
            remember_me=form.remember_me.data,
        )
        if error:
            flash(error, "error")
            return render_template("admin_auth/login.html", form=form)
        return redirect(url_for("admin.admin_dashboard.index"))
    return render_template("admin_auth/login.html", form=form)


@bp.route("/forgot", methods=["GET", "POST"])
@auth_required(False, "admin.admin_dashboard.index")
def forgot():
    is_sent = False
    form = ForgotForm()
    if form.validate_on_submit():
        AuthService.forgot(email=form.email.data)
        is_sent = True
    return render_template(
        "admin_auth/forgot.html", form=form, is_sent=is_sent
    )


@bp.route("/restore", methods=["GET"])
@auth_required(False, "admin.admin_dashboard.index")
def restore():
    token = request.args.get("token")
    if not token:
        abort(400, description="Token not found")
    message = AuthService.restore(token)
    if message:
        abort(400, description=message)
    return "ok"


@bp.route("/logout", methods=["GET"])
@auth_required(True, "admin.admin_auth.login")
def logout():
    AuthService.logout()
    return redirect("/")
