from typing import Any

from wtforms.validators import URL, ValidationError


class UrlOrPath:
    """Absolute URL (https://cdn/x.png) or path from the site root (/x.png).

    Root-relative paths come from the file manager, whose baseurl is
    "/upload/". Protocol-relative values (//host/x.png) are refused.
    """

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "Invalid URL or path."
        # require_tld=False: accept http://localhost:9000/... in development
        self._url = URL(require_tld=False, message=self.message)

    def __call__(self, form: Any, field: Any) -> None:
        value = (field.data or "").strip()
        if value.startswith("/") and value[1:2] not in ("/", "\\"):
            if any(char.isspace() for char in value):
                raise ValidationError(self.message)
            return
        self._url(form, field)
