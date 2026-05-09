from app.models import Admin
from app.database import db_session
from app.utils.security import verify_password
from flask import session
from flask_mail import Message
from app.utils.mailer import get_mailer


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
        mailer=get_mailer()
        message=Message(subject='recovery password',recipients=[email])
        message.body = 'amamamamambhjasv'
        mailer.send(message)
