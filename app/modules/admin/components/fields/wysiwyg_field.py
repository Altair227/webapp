from wtforms.fields import TextAreaField


class WysiwygField(TextAreaField):
    default_render_kw = {
        "data-field-type": "wysiwyg",
    }

    def __init__(self, label=None, validators=None, **kwargs):
        render_kw = {
            **self.default_render_kw,
            **(kwargs.pop("render_kw", None) or {}),
        }
        super().__init__(
            label=label, validators=validators, render_kw=render_kw, **kwargs
        )
