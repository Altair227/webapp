from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField
from app.modules.admin.components.fields import DateField, WysiwygField
from wtforms.validators import DataRequired, Length
from datetime import datetime, timezone


class NewsForm(FlaskForm):
    title = StringField(
        label="Title", validators=[DataRequired(), Length(min=3, max=255)]
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
        validators=[DataRequired()],
    )
