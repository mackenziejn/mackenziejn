# src/database.py

import os
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.base import Base
from src.models import Service
from src.utils import load_config

# --------------------------------------------------
# Configuração do banco de dados
config = load_config()
db_path = config["database"]["path"]

DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{Path(db_path).resolve()}"

# --------------------------------------------------
# Criação da engine e SessionLocal
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

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

# Para uso estilo FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------
# Criação de tabelas
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("🧱 Tabelas criadas com sucesso.")

# --------------------------------------------------
# Popula serviços iniciais a partir do config.yml
def populate_initial_services():
    services_config = config["business"]["services"]

    with get_db_session() as db:
        if not db.query(Service).first():
            services = [
                Service(name=s["name"], price=s["price"], duration=s["duration"])
                for s in services_config
            ]
            db.add_all(services)
            print("✨ Serviços iniciais cadastrados a partir do config.yml!")
        else:
            print("ℹ️ Serviços já existentes. Nenhuma alteração feita.")

# --------------------------------------------------
# Inicializa o banco
def init_db():
    print("🚀 Inicializando banco de dados...")
    create_tables()
    populate_initial_services()
    print("✅ Banco inicializado com sucesso.")

# --------------------------------------------------
if __name__ == "__main__":
    init_db()
