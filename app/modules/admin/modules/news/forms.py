from datetime import datetime, timezone

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, optional

from app.modules.admin.components.fields import DateField, WysiwygField
from app.modules.admin.components.validators import UrlOrPath


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
    published_at = DateField(
        "Published at",
        default=lambda: datetime.now(timezone.utc),
        validators=[
            DataRequired(),
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
