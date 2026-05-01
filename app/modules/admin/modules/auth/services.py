from app.models import Admin
from app.database import db_session
from app.utils.security import verify_password
from flask import session


class AuthService:
    @staticmethod
    def login(
        email: str, password: str, remember_me: bool = False
    ) -> tuple[Admin | None, str | None]:
        admin = db_session.query(Admin).filter(Admin.email == email).first()
        if not admin or not verify_password(password, admin.password_hash):
            return None, "Incorrect email/password"
        session.permanent = remember_me
        session["user_id"] = admin.id
        session["user_email"] = email
        return admin, None
