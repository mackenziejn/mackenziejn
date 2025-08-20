# src/session.py

import os
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import DB_PATH

# --------------------------------------------------
# URL do banco de dados SQLite
DATABASE_URL = f"sqlite:///{DB_PATH}" if DB_PATH else "sqlite:///./agendamento.db"

# --------------------------------------------------
# Engine e SessionLocal
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# --------------------------------------------------
# Context manager para sessões
@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
