from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_database_url


def build_engine():
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )


def build_session_factory(engine):
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )