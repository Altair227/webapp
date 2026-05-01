from flask import Blueprint, render_template, flash
from .forms import LoginForm
from .services import AuthService

bp = Blueprint(
    "admin_auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
)


@bp.route("/login", methods=["GET", "POST"])
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
    return render_template("admin_auth/login.html", form=form)
