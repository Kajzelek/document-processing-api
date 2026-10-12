from functools import lru_cache

from app.db.session import build_engine, build_session_factory


@lru_cache
def get_session_factory():
    engine = build_engine()
    return build_session_factory(engine)


def get_db():
    session_factory = get_session_factory()

    with session_factory() as session:
        yield session