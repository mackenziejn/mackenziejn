# utils.py

"""
Funções utilitárias para configuração, mensagens, teclados e integração externa.
"""

import yaml
import logging
import asyncio
from pathlib import Path
from datetime import datetime, time, timedelta, date
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.models import Appointment, AppointmentStatus  # Certifique-se que o import está correto

# -------------------------------------------------------------------
# 🔧 Caminhos de arquivos
# -------------------------------------------------------------------

CONFIG_PATH = Path("/home/pensec/ProjetosBot/JacaHair_bot/config.yml")  # Caminho absoluto
MESSAGES_PATH = Path(__file__).resolve().parent.parent / "res" / "messages.yml"

# -------------------------------------------------------------------
# 📝 Logger
# -------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -------------------------------------------------------------------
# ⚙️ Configurações
# -------------------------------------------------------------------

def load_config():
    """Carrega o arquivo config.yml e retorna como dict."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logger.info("✅ Configuração carregada com sucesso.")
        return config
    except Exception as e:
        logger.error(f"❌ Erro ao carregar config.yml: {e}")
        return {}

def get_bot_token():
    """Retorna o token do bot Telegram a partir do config.yml."""
    config = load_config()
    try:
        token = config["telegram"]["token"]
        if not token or "AAG" not in token:
            raise ValueError("Token inválido ou ausente.")
        return token
    except KeyError:
        logger.error("❌ Token do bot não encontrado no config.yml.")
        return None

def get_admin_ids():
    """Retorna lista de admin_ids do config.yml."""
    config = load_config()
    return config.get("telegram", {}).get("admin_ids", [])

# -------------------------------------------------------------------
# 💬 Mensagens
# -------------------------------------------------------------------

def load_messages():
    """Carrega mensagens do arquivo messages.yml."""
    try:
        with open(MESSAGES_PATH, "r", encoding="utf-8") as file:
            messages = yaml.safe_load(file)
        logger.info("✅ Mensagens carregadas com sucesso.")
        return messages
    except Exception as e:
        logger.error(f"❌ Erro ao carregar messages.yml: {e}")
        return {}

# -------------------------------------------------------------------
# ⌨️ Teclados Telegram
# -------------------------------------------------------------------

def create_reply_keyboard(options, resize_keyboard=True, one_time_keyboard=True):
    """Cria teclado de resposta com opções em linhas separadas."""
    keyboard = [[option] for option in options]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
    )

def gerar_teclado_servicos(servicos):
    """Gera teclado inline com botões para cada serviço."""
    botoes = [
        [InlineKeyboardButton(servico.name, callback_data=f"servico_{servico.id}")]
        for servico in servicos
    ]
    return InlineKeyboardMarkup(botoes)

def gerar_teclado_horarios(horarios_disponiveis=None, inicio_hora=None, fim_hora=None, intervalo_min=None):
    """Gera teclado inline com horários disponíveis."""
    if horarios_disponiveis:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(h, callback_data=f"time_{h}")]
            for h in horarios_disponiveis
        ])

    if not all([inicio_hora, fim_hora, intervalo_min]):
        raise ValueError("Informe horários disponíveis ou parâmetros de geração.")

    hoje = datetime.today()
    current_dt = datetime.combine(hoje.date(), time(hour=inicio_hora))
    end_dt = datetime.combine(hoje.date(), time(hour=fim_hora))

    keyboard = []
    while current_dt <= end_dt:
        h_str = current_dt.strftime("%H:%M")
        keyboard.append([InlineKeyboardButton(h_str, callback_data=f"time_{h_str}")])
        current_dt += timedelta(minutes=intervalo_min)

    return InlineKeyboardMarkup(keyboard)

# --- FUNÇÃO CORRIGIDA para gerar teclado de datas com vagas restantes ---

MAX_VAGAS_POR_DIA = 5  # Ajuste conforme a regra de negócio

def gerar_teclado_datas(db, service_id, dias_anteriores=0, dias_futuros=14):
    """Gera teclado inline de datas com indicação de vagas restantes para o serviço."""
    botoes = []
    hoje = date.today()

    for i in range(dias_anteriores, dias_futuros + 1):
        data = hoje + timedelta(days=i)

        # Contar agendamentos para a data e serviço (não cancelados)
        count = db.query(Appointment).filter(
            Appointment.service_id == service_id,
            Appointment.date >= datetime.combine(data, datetime.min.time()),
            Appointment.date < datetime.combine(data + timedelta(days=1), datetime.min.time()),
            Appointment.status != AppointmentStatus.cancelado
        ).count()

        vagas_restantes = MAX_VAGAS_POR_DIA - count
        if vagas_restantes < 0:
            vagas_restantes = 0

        texto = f"{data.strftime('%d/%m/%Y')} ({vagas_restantes}/{MAX_VAGAS_POR_DIA} vagas)"
        callback_data = f"data_{data.isoformat()}"
        botoes.append([InlineKeyboardButton(texto, callback_data=callback_data)])

    return InlineKeyboardMarkup(botoes)

# -------------------------------------------------------------------
# 🔗 Confirmação externa
# -------------------------------------------------------------------

def gerar_confirmation_url(appointment_id: int) -> str:
    """Gera URL de confirmação externa do agendamento."""
    base_url = "https://jacahairbeardbot.onrender.com/confirmacao"
    return f"{base_url}?id={appointment_id}"

async def enviar_confirmacao_externa(appointment, confirmation_url):
    """Simula envio de confirmação para canal externo."""
    try:
        logger.info(f"📤 Enviando confirmação do agendamento ID {appointment.id}")
        logger.info(f"🔗 URL: {confirmation_url}")
        await asyncio.sleep(0.1)  # Simulação de delay
    except Exception as e:
        logger.error(f"❌ Erro ao enviar confirmação externa: {e}")
