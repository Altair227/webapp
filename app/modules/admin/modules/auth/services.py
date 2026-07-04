from app.models import Admin, EmailToken
from app.database import db_session
from app.utils.security import verify_password
from app.common.types import EntityType, SmallIntEnum, EmailTokenType
from app.utils.mailer import get_mailer
from app.utils.security import generate_password, hash_password
from flask import session, render_template
from flask_mail import Message
from datetime import datetime, timedelta, timezone


class AuthService:
    @staticmethod
    def login(
        email: str, password: str, remember_me: bool = False
    ) -> tuple[Admin | None, str | None]:
        admin = db_session.query(Admin).filter(Admin.email == email).first()
        if not admin or not verify_password(password, admin.password_hash):
            return None, "Incorrect email/password"
        if admin.is_blocked:
            return None, "User is blocked"
        session.permanent = remember_me
        session["user_id"] = admin.id
        session["user_email"] = email
        return admin, None

    @staticmethod
    def forgot(email: str) -> None:
        admin = (
            db_session.query(Admin)
            .filter(Admin.email == email, Admin.is_blocked == False)
            .first()
        )
        if not admin:
            return
        token_value = generate_password(length=40)
        expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        db_session.add(
            EmailToken(
                entity_type=EntityType.ADMIN,
                entity_id=admin.id,
                token=token_value,
                type=EmailTokenType.PASSWORD_RESET,
                expires_at=expires_at,
            )
        )
        db_session.commit()
        mailer = get_mailer()
        message = Message(subject="recovery password", recipients=[email])
        message.html = render_template(
            "emails/forgot_admin_password.html",
            token=token_value,
            expires_at=expires_at,
        )
        mailer.send(message)

    @staticmethod
    def restore(token: str) -> str | None:
        token_data = (
            db_session.query(EmailToken)
            .filter(
                EmailToken.entity_type == EntityType.ADMIN,
                EmailToken.type == EmailTokenType.PASSWORD_RESET,
                EmailToken.token == token,
                EmailToken.used_at.is_(None),
                EmailToken.expires_at >= datetime.now(timezone.utc),
            )
            .first()
        )
        if not token_data:
            return "Token not found or expired"
        admin = (
            db_session.query(Admin)
            .filter(Admin.id == token_data.entity_id)
            .first()
        )
        if not admin:
            return "User not found"
        new_password = generate_password(12)
        new_password_hash = hash_password(new_password)
        admin.password_hash = new_password_hash
        token_data.used_at = datetime.now(timezone.utc)
        db_session.commit()
        mailer = get_mailer()
        message = Message(subject="Change password", recipients=[admin.email])
        message.html = render_template(
            "emails/change_admin_password.html",
            login=admin.email,
            password=new_password,
        )
        mailer.send(message)
        return None

    @staticmethod
    def logout() -> None:
        session.pop("user_id", None)
        session.pop("user_admin", None)
