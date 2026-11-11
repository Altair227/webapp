from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import get_config


config = get_config()
engine = create_engine(config.postgres.dsn)
db_session = scoped_session(sessionmaker(bind=engine))


def shutdown_session(exception: BaseException | None = None) -> None:
    if exception:
        db_session.rollback()
    db_session.remove()
