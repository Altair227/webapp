from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = EmailField(
        label="Email",
        validators=[
            DataRequired(),
            Email(
                message="Invalid email format",
            ),
        ],
    )
    password = PasswordField(
        label="Password",
        validators=[
            DataRequired(),
            Length(
                min=6,
                max=128,
                message="Password must be minimum 6 character long",
            ),
        ],
    )

    remember_me = BooleanField(
        label="Remember me",
        default=False,
    )
