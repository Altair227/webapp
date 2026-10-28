from wtforms.fields import Field
from wtforms.widgets import HiddenInput
from typing import Any


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
    ):
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

    def _value(self):
        """
        Returns the value of the field as a string. If the data is None, it returns an empty string.
        """
        if self.data:
            return str(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        """
        Processes incoming form data and sets the field's data attribute.
        If valuelist is empty, it sets data to None. Otherwise, it takes the first value from valuelist.
        """
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = None
