# src/models.py

"""
Modelos ORM do sistema de agendamento.
Versão otimizada para produção com constraints, índices e validações.
"""

from enum import Enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum,
    CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, validates
from src.base import Base  # Base declarativa centralizada

# ---------------------------
# Enum de status de agendamento
# ---------------------------
class AppointmentStatus(str, Enum):
    pendente_confirmacao = "pendente_confirmacao"
    confirmado = "confirmado"
    cancelado = "cancelado"
    aguardando = "aguardando"  # para lista de espera / encaixe

# ---------------------------
# Modelo Serviço
# ---------------------------
class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    duration = Column(Integer, nullable=False)  # duração em minutos
    price = Column(Float, nullable=False, default=0.0)

    appointments = relationship(
        "Appointment", back_populates="service", cascade="all, delete-orphan"
    )
    espera_encaixe = relationship(
        "EsperaEncaixe", back_populates="service", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint('duration > 0', name='check_duration_positive'),
        CheckConstraint('price >= 0', name='check_price_non_negative'),
    )

# ---------------------------
# Modelo Cliente
# ---------------------------
class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship(
        "Appointment", back_populates="client", cascade="all, delete-orphan"
    )
    espera_encaixe = relationship(
        "EsperaEncaixe", back_populates="client", cascade="all, delete-orphan"
    )

# ---------------------------
# Modelo Agendamento
# ---------------------------
class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(
        SQLEnum(AppointmentStatus, native_enum=False),
        nullable=False,
        default=AppointmentStatus.pendente_confirmacao
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(500), nullable=True)

    cor_cabelo = Column(String(20), nullable=True)
    tipo_cabelo = Column(String(20), nullable=True)
    tamanho_cabelo = Column(String(20), nullable=True)

    client = relationship("Client", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")

    __table_args__ = (
        Index("idx_service_date", "service_id", "date"),
        UniqueConstraint('client_id', 'service_id', 'date', name='uq_client_service_date'),
        CheckConstraint('date > CURRENT_TIMESTAMP', name='check_future_date'),
    )

    # Validação extra para garantir data futura no ORM
    @validates('date')
    def validate_date(self, key, value):
        if value <= datetime.utcnow():
            raise ValueError("A data do agendamento deve ser no futuro.")
        return value

# ---------------------------
# Modelo Lista de Espera / Encaixe
# ---------------------------
class EsperaEncaixe(Base):
    __tablename__ = 'espera_encaixe'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    data_desejada = Column(DateTime, nullable=False)
    status = Column(
        SQLEnum(AppointmentStatus, native_enum=False),
        nullable=False,
        default=AppointmentStatus.aguardando
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="espera_encaixe")
    service = relationship("Service", back_populates="espera_encaixe")

    __table_args__ = (
        Index("idx_service_data_desejada", "service_id", "data_desejada"),
        CheckConstraint('data_desejada > CURRENT_TIMESTAMP', name='check_future_data_desejada'),
    )

    @validates('data_desejada')
    def validate_data_desejada(self, key, value):
        if value <= datetime.utcnow():
            raise ValueError("A data desejada para encaixe deve ser no futuro.")
        return value
