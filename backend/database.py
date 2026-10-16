from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

settings = get_settings()

engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Set True to mirror spring.jpa.show-sql=true
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — equivalent of Spring's @Transactional / EntityManager injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
