from flask_mail import Mail
from functools import lru_cache


@lru_cache
def get_mailer() -> Mail:
    return Mail()