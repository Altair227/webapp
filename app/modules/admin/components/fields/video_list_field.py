from typing import Any

from markupsafe import Markup, escape
from wtforms.fields import Field


class VideoListWidget:
    """One row per video: [url input][browse][+][-].

    Every input has the field name, so the browser posts all of them and
    the field receives the list. main.js (data-field-type="videos") wires
    the buttons: browse opens the file manager, + adds a row, - removes it.
    """

    def __call__(self, field: VideoListField, **kwargs: Any) -> Markup:
        css = "video-rows" + (" is-invalid" if field.errors else "")
        rows = "".join(
            self._row(field.name, url) for url in (field.data or [""])
        )
        return Markup(
            f'<div class="{css}" id="{escape(field.id)}"'
            f' data-field-type="videos"'
            f' data-max-items="{field.max_items}">{rows}</div>'
        )

    @staticmethod
    def _row(name: str, url: str) -> str:
        return (
            '<div class="input-group mb-2 video-row">'
            f'<input type="text" class="form-control" name="{escape(name)}"'
            f' value="{escape(url)}"'
            ' placeholder="Paste a link or choose a video">'
            '<button class="btn btn-primary" type="button"'
            ' data-video-action="browse" title="Browse">'
            '<i class="bi bi-folder"></i></button>'
            '<button class="btn btn-outline-success" type="button"'
            ' data-video-action="add" title="Add row">'
            '<i class="bi bi-plus-lg"></i></button>'
            '<button class="btn btn-outline-danger" type="button"'
            ' data-video-action="remove" title="Remove">'
            '<i class="bi bi-dash-lg"></i></button>'
            "</div>"
        )


class VideoListField(Field):
    """List of video URLs, one text input per video (see VideoListWidget).

    data is list[str]. Populated from obj, it accepts a list of URLs or of
    objects with a .url attribute (e.g. News.videos -> SourceVideo).
    """

    widget = VideoListWidget()

    def __init__(
        self,
        label: str | None = None,
        validators: Any = None,
        max_items: int = 50,
        **kwargs: Any,
    ) -> None:
        super().__init__(label=label, validators=validators, **kwargs)
        self.max_items = max_items

    def process_data(self, value: Any) -> None:
        self.data = [
            item if isinstance(item, str) else item.url
            for item in (value or [])
        ]

    def process_formdata(self, valuelist: list[str]) -> None:
        # strip, drop empty rows and duplicate URLs, keep order
        self.data = list(
            dict.fromkeys(v.strip() for v in valuelist if v.strip())
        )
        if len(self.data) > self.max_items:
            raise ValueError(f"No more than {self.max_items} videofs.")
