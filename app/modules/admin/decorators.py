from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import g, redirect, url_for
from werkzeug.wrappers import Response


def auth_required[**P, R](
    need_auth: bool = True, redirect_to: str = "admin.admin_auth.login"
) -> Callable[[Callable[P, R]], Callable[P, R | Response]]:
    def decorator(f: Callable[P, R]) -> Callable[P, R | Response]:
        @wraps(f)
        def decorated_function(
            *args: P.args, **kwargs: P.kwargs
        ) -> R | Response:
            is_auth = g.user is not None
            if need_auth and not is_auth:
                return redirect(url_for(redirect_to))
            if not need_auth and is_auth:
                return redirect(url_for(redirect_to))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def breadcrumbs[**P, R](
    label: str, endpoint: str | None = None, **url_kwargs: Any
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
            url = url_for(endpoint, **url_kwargs) if endpoint else None
            g.breadcrumbs.append((label, url))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
