from app.config import get_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

config = get_config()
engine = create_engine(config.postgres.dsn)
db_session = scoped_session(sessionmaker(bind=engine))


def shutdown_session(exception=None) -> None:
    if exception:
        db_session.rollback()
    db_session.remove()
