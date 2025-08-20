# src/utils.py

"""
Utilitários do sistema de agendamento:
- Carregamento de arquivos YAML (config e mensagens)
- Geração de teclados inline do Telegram
- Integração externa simulada para confirmações
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

# Caminhos fixos para arquivos YAML dentro da pasta res/
BASE_PATH = Path(__file__).resolve().parent.parent / "res"
CONFIG_PATH = BASE_PATH / "config.yml"
MESSAGES_PATH = BASE_PATH / "messages.yml"

# ---------------------------
# 💼 Configuração - carregamento do YAML config.yml
# ---------------------------
def load_config(path=None):
    config_path = Path(path) if path else CONFIG_PATH
    if not config_path.exists():
        logger.error(f"Arquivo de configuração '{config_path}' não encontrado.")
        raise FileNotFoundError(f"Arquivo de configuração '{config_path}' não encontrado.")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    logger.info(f"Configuração carregada de '{config_path}'")
    return config

# ---------------------------
# 💬 Mensagens - carregamento do YAML messages.yml
# ---------------------------
def load_messages(path=None):
    messages_path = Path(path) if path else MESSAGES_PATH
    if not messages_path.exists():
        logger.error(f"Arquivo de mensagens '{messages_path}' não encontrado.")
        return {}
    try:
        with open(messages_path, "r", encoding="utf-8") as f:
            messages = yaml.safe_load(f)
        logger.info("✅ Mensagens carregadas com sucesso.")
        return messages
    except Exception as e:
        logger.error(f"❌ Falha ao carregar messages.yml: {e}")
        return {}

# ---------------------------
# 🎛️ Funções para teclados inline Telegram
# ---------------------------
def gerar_teclado_servicos(servicos_obj):
    """
    Gera teclado inline com botões para cada serviço.
    """
    botoes = [
        [InlineKeyboardButton(servico.name, callback_data=f"servico_{servico.id}")]
        for servico in servicos_obj
    ]
    return InlineKeyboardMarkup(botoes)

def gerar_teclado_horarios(horarios):
    """
    Gera teclado inline com horários disponíveis (lista de strings "HH:MM").
    """
    botoes = [
        [InlineKeyboardButton(horario, callback_data=f"horario_{horario}")]
        for horario in horarios
    ]
    return InlineKeyboardMarkup(botoes)

def gerar_teclado_datas(db=None, service_id=None, dias_uteis=7, max_vagas_por_dia=5):
    """
    Gera teclado inline com datas a partir de hoje, nos próximos 'dias_uteis' dias,
    mostrando as vagas restantes para o serviço especificado.
    Requer db (sessão SQLAlchemy) e service_id para consulta dos agendamentos.
    Se db ou service_id não forem passados, gera datas simples.
    """
    botoes = []
    hoje = datetime.now().date()

    if db is None or service_id is None:
        # Datas simples (sem vagas)
        for i in range(dias_uteis):
            dia = hoje + timedelta(days=i)
            texto = dia.strftime("%d/%m/%Y")
            callback = f"data_{dia.isoformat()}"
            botoes.append([InlineKeyboardButton(texto, callback_data=callback)])
        return InlineKeyboardMarkup(botoes)

    # Importação local para evitar import circular
    from src.models import Appointment, AppointmentStatus

    for i in range(dias_uteis):
        dia = hoje + timedelta(days=i)
        inicio_dia = datetime.combine(dia, datetime.min.time())
        fim_dia = inicio_dia + timedelta(days=1)

        qtd_agendamentos = db.query(Appointment).filter(
            Appointment.service_id == service_id,
            Appointment.date >= inicio_dia,
            Appointment.date < fim_dia,
            Appointment.status != AppointmentStatus.cancelado
        ).count()

        vagas_restantes = max_vagas_por_dia - qtd_agendamentos
        texto = f"{dia.strftime('%d/%m/%Y')} - Vagas {vagas_restantes} de {max_vagas_por_dia}"
        callback = f"data_{dia.isoformat()}"
        botoes.append([InlineKeyboardButton(texto, callback_data=callback)])

    return InlineKeyboardMarkup(botoes)

# ---------------------------
# 🌐 Integração externa (simulada)
# ---------------------------
def gerar_confirmation_url(agendamento_id):
    """
    Gera URL para confirmação externa do agendamento.
    """
    base_url = "https://jacahairbeardbot.onrender.com/confirmacao"
    return f"{base_url}?id={agendamento_id}"

async def enviar_confirmacao_externa(agendamento_data: dict, confirmation_url: str):
    """
    Simula envio de confirmação para canal externo (SMS, e-mail, webhook, etc).
    Recebe um dict com os dados do agendamento.
    """
    try:
        logger.info(f"📤 Enviando confirmação externa para agendamento {agendamento_data.get('id')}")
        logger.info(f"Cliente: {agendamento_data.get('client_name')}")
        logger.info(f"Telefone: {agendamento_data.get('client_phone')}")
        logger.info(f"E-mail: {agendamento_data.get('client_email')}")
        logger.info(f"Data e Hora: {agendamento_data.get('date')}")
        logger.info(f"Cor do cabelo: {agendamento_data.get('cor_cabelo', 'N/A')}")
        logger.info(f"Tipo do cabelo: {agendamento_data.get('tipo_cabelo', 'N/A')}")
        logger.info(f"Tamanho do cabelo: {agendamento_data.get('tamanho_cabelo', 'N/A')}")
        logger.info(f"🔗 URL de confirmação: {confirmation_url}")

        import asyncio
        await asyncio.sleep(0.1)  # simula envio externo
    except Exception as e:
        logger.error(f"❌ Erro ao enviar confirmação externa: {e}")
