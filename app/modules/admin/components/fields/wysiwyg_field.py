from typing import Any, ClassVar

from wtforms.fields import TextAreaField


class WysiwygField(TextAreaField):
    default_render_kw: ClassVar[dict[str, str]] = {
        "data-field-type": "wysiwyg",
    }

    def __init__(
        self,
        label: str | None = None,
        validators: Any = None,
        **kwargs: Any,
    ) -> None:
        render_kw = {
            **self.default_render_kw,
            **(kwargs.pop("render_kw", None) or {}),
        }
        super().__init__(
            label=label, validators=validators, render_kw=render_kw, **kwargs
        )
