# src/base.py

import os
from sqlalchemy.orm import declarative_base

# ---------------------------
# Base ORM
# ---------------------------
# Base para todos os modelos do SQLAlchemy
Base = declarative_base()

# ---------------------------
# Configurações gerais
# ---------------------------
# URL base da aplicação (usada em links de confirmação via Flask)
BASE_URL = os.getenv("BASE_URL", "https://seusite.com")
