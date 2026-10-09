from app.db.base import Base
from app.db.session import build_engine
from app.models.file_analysis import FileAnalysis


def main():
    engine = build_engine()

    try:
        Base.metadata.create_all(engine)
        print(f"Database ready: {FileAnalysis.__tablename__}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()