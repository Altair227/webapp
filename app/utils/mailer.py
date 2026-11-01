from functools import lru_cache

from flask_mail import Mail


@lru_cache
def get_mailer() -> Mail:
    return Mail()
