from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from app.modules.admin.components.fields import (
    DateField,
    ImageListField,
    WysiwygField,
)
from app.modules.admin.components.validators import EachUrlOrPath, UrlOrPath


class NewsForm(FlaskForm):
    title = StringField(
        label="Title",
        validators=[
            DataRequired(),
            Length(min=3, max=255),
        ],
    )
    description = TextAreaField(
        label="Announcement",
        validators=[
            DataRequired(),
            Length(
                min=10,
            ),
        ],
    )
    content = WysiwygField(
        label="Content",
        validators=[
            DataRequired(),
            Length(
                min=10,
            ),
        ],
    )
    # empty: the news is shown on the site right away
    published_at = DateField(
        "Published at",
        validators=[
            Optional(),
        ],
    )
    image_url = StringField(
        label="Cover image",
        validators=[
            Optional(),
            UrlOrPath(),
            Length(max=255),
        ],
    )
    images = ImageListField(
        label="Photos",
        validators=[
            EachUrlOrPath(),
        ],
    )
