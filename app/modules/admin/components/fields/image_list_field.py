import json
from typing import Any

from wtforms.fields import Field
from wtforms.widgets import HiddenInput


class ImageListField(Field):
    """
    A custom WTForms field for handling a list of images.
    This field is designed to work with a hidden input widget, allowing for the storage of image data in a serialized format.
    """

    widget = HiddenInput()

    def __init__(
        self,
        label: str | None = None,
        validators: Any = None,
        max_items: int = 50,
        **kwargs: Any,
    ) -> None:
        render_kw = {
            "data-field-type": "images",
            "data-max-items": str(max_items),
            **(kwargs.pop("render_kw", None) or {}),
        }
        super().__init__(
            label=label,
            validators=validators,
            render_kw=render_kw,
            **kwargs,
        )
        self.max_items = max_items

    def process_data(self, value: Any) -> None:
        self.data = [
            item if isinstance(item, str) else item.url
            for item in (value or [])
        ]

    def _value(self) -> str:
        return json.dumps(self.data or [])

    def process_formdata(self, valuelist: list[str]) -> None:
        if not valuelist or not valuelist[0].strip():
            self.data = []
            return
        try:
            items = json.loads(valuelist[0])
        except ValueError as e:
            self.data = []
            raise ValueError("Invalid image list.") from e
        if not isinstance(items, list) or not all(
            isinstance(item, str) for item in items
        ):
            self.data = []
            raise ValueError("Invalid image list.")
        # strip, drop empty and duplicate URLs, keep order
        self.data = list(dict.fromkeys(i.strip() for i in items if i.strip()))
        if len(self.data) > self.max_items:
            raise ValueError(f"No more than {self.max_items} images.")
