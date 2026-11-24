from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

db_url = settings.database_url

connect_options = {}
if db_url.startswith("sqlite"):
    connect_options["check_same_thread"] = False

engine = create_engine(
    db_url,
    connect_args=connect_options
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()