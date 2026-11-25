import argparse

from email_validator import EmailNotValidError, validate_email

from app.common.types import AdminType, SmallIntEnum
from app.database import db_session
from app.models import Admin
from app.utils.security import generate_password, hash_password
from app.utils.video_scan import scan_videos, scan_videos_loop


def _create_superadmin() -> None:
    def _prompt_email() -> str:
        while True:
            raw = input("Superadmin email: ").strip()
            try:
                return validate_email(
                    raw, check_deliverability=False
                ).normalized
            except EmailNotValidError as e:
                print(f"  Invalid email: {e}. Please try again.")

    email = _prompt_email()
    password = generate_password()
    password_hash = hash_password(password)
    admin = db_session.query(Admin).filter(Admin.email == email).first()

    if not admin:
        db_session.add(
            Admin(
                email=email,
                password_hash=password_hash,
                type=AdminType.SUPER_ADMIN,
                is_activated=True,
                is_blocked=False,
                is_deleted=False,
            )
        )
        action = "Created"
    else:
        admin.password_hash = password_hash
        admin.type = AdminType.SUPER_ADMIN
        admin.is_activated = True
        admin.is_blocked = False
        admin.is_deleted = False
        action = "Updated"
    db_session.commit()
    print(f"{action} superadmin:")
    print(f"  Email:    {email}")
    print(f"  Password: {password}")


def _scan_videos(loop: bool) -> None:
    if loop:
        return scan_videos_loop()
    done, failed = scan_videos()
    print(f"Scanned videos: {done} done, {failed} failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        name="create-superadmin",
        help="Create or update a super admin account",
    )
    scan_parser = subparsers.add_parser(
        name="scan-videos",
        help="Detect type and find posters for new videos (one pass)",
    )
    scan_parser.add_argument(
        "--loop",
        action="store_true",
        help="Keep scanning until stopped",
    )
    args = parser.parse_args()
    if args.command == "create-superadmin":
        return _create_superadmin()
    if args.command == "scan-videos":
        return _scan_videos(args.loop)


if __name__ == "__main__":
    main()
