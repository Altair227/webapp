from flask import g, url_for, redirect
from functools import wraps


def auth_required(
    need_auth: bool = True, redirect_to: str = "admin.admin_auth.login"
):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            is_auth = g.user is not None
            if need_auth and not is_auth:
                return redirect(url_for(redirect_to))
            if not need_auth and is_auth:
                return redirect(url_for(redirect_to))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
