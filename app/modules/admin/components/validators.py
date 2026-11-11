from typing import Any
from urllib.parse import urlsplit

from wtforms.validators import ValidationError


def is_url_or_path(value: str) -> bool:
    """Absolute URL (https://cdn/x.png) or path from the site root (/x.png).

    Root-relative paths come from the file manager, whose baseurl is
    "/upload/". Protocol-relative values (//host/x.png) are refused.
    URLs need http(s) and a host; localhost is fine in development.
    """
    value = value.strip()
    if not value or any(char.isspace() for char in value):
        return False
    if value.startswith("/"):
        return value[1:2] not in ("/", "\\")
    try:
        parts = urlsplit(value)
        return parts.scheme in ("http", "https") and bool(parts.hostname)
    except ValueError:  # e.g. "http://[::1" or a bad port
        return False


class UrlOrPath:
    """Field validator for a single URL or root-relative path."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "Invalid URL or path."

    def __call__(self, form: Any, field: Any) -> None:
        if not is_url_or_path(field.data or ""):
            raise ValidationError(self.message)


class EachUrlOrPath:
    """Field validator for a list of URLs or root-relative paths."""

    def __init__(self, max_length: int = 255) -> None:
        self.max_length = max_length

    def __call__(self, form: Any, field: Any) -> None:
        for value in field.data or []:
            if len(value) > self.max_length:
                raise ValidationError(
                    f"Image URL is longer than {self.max_length} characters."
                )
            if not is_url_or_path(value):
                raise ValidationError(f"Invalid image URL or path: {value}")
