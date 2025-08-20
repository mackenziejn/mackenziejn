# src/handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from datetime import datetime, timedelta
import re
import logging

from src.database import get_db_session
from src.models import Service, Client, Appointment, AppointmentStatus
from src.utils import (
    load_messages, gerar_teclado_servicos, gerar_teclado_horarios,
    gerar_teclado_datas, gerar_confirmation_url, enviar_confirmacao_externa
)

# ---------------------------
# Configuração de mensagens
# ---------------------------
#messages = load_messages()#
from pathlib import Path
from src.utils import load_messages

# Caminho absoluto do messages.yml dentro do projeto JacaHair_bot
BASE_PATH = Path(__file__).resolve().parent.parent  # sobe de src/ para JacaHair_bot/
MESSAGES_FILE = BASE_PATH / "res" / "messages.yml"

messages = load_messages(path=MESSAGES_FILE)

# Debug opcional para garantir que está carregando o arquivo correto
print("✅ Mensagens carregadas de:", MESSAGES_FILE)
print("Mensagem de boas-vindas:", messages.get("start_message"))

# ---------------------------
# Estados da conversa
# ---------------------------
(
    ESCOLHENDO_SERVICOS,
    ESCOLHENDO_DATA,
    ESCOLHENDO_HORARIO,
    INSERINDO_NOME,
    INSERINDO_TELEFONE,
    INSERINDO_EMAIL,
    ESCOLHENDO_COR_CABELO,
    ESCOLHENDO_TIPO_CABELO,
    ESCOLHENDO_TAMANHO_CABELO,
    CONFIRMANDO,
) = range(10)

# ---------------------------
# Funções utilitárias
# ---------------------------
def horarios_disponiveis_para_data(db, service_ids, data):
    horarios = [f"{h:02d}:00" for h in range(9, 17)]
    agendamentos = db.query(Appointment).filter(
        Appointment.service_id.in_(service_ids),
        Appointment.date >= datetime.combine(data, datetime.min.time()),
        Appointment.date < datetime.combine(data + timedelta(days=1), datetime.min.time()),
        Appointment.status != AppointmentStatus.cancelado.value
    ).all()
    ocupados = set(a.date.strftime("%H:%M") for a in agendamentos)
    return [h for h in horarios if h not in ocupados]

def parse_date_str(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        return None

def validar_email(email: str) -> bool:
    """Validação simples de email."""
    padrao = r"[^@]+@[^@]+\.[^@]+"
    return re.fullmatch(padrao, email) is not None

def validar_nome(nome: str) -> bool:
    """Validação de nome: apenas letras e espaços, mínimo 2 caracteres."""
    return re.fullmatch(r"[A-Za-zÀ-ÿ ]{2,50}", nome) is not None

# ---------------------------
# Handlers principais
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🐊 <b>Olá, tudo bem?</b>\n"
        "Sou o <b>Jaca</b>, seu assistente virtual! \n\n"
        "Escolha uma das opções abaixo para continuar:"
    )

    keyboard = [
        [InlineKeyboardButton("Serviços e valores", callback_data="servicos")],
        [InlineKeyboardButton("Agendar um horário", callback_data="agendar")],
        [InlineKeyboardButton("Ver meus agendamentos", callback_data="meus_agendamentos")],
        [InlineKeyboardButton("Cancelar um agendamento", callback_data="cancelar")],
        
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            welcome_message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

# ---------------------------
# Fluxo de agendamento
# ---------------------------
async def agendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["servicos_escolhidos"] = []
    await mostrar_servicos(update, context)
    return ESCOLHENDO_SERVICOS

async def mostrar_servicos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_db_session() as db:
        servicos_obj = db.query(Service).all()
        if not servicos_obj:
            await update.message.reply_text(messages.get("no_services", "Nenhum serviço disponível."))
            return ConversationHandler.END
        teclado = gerar_teclado_servicos(servicos_obj)

    msg = messages.get("choose_service", "Escolha os serviços (você pode selecionar vários):")
    if update.message:
        await update.message.reply_text(msg, reply_markup=teclado)
    elif update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=teclado)

async def escolher_servicos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        service_id = int(query.data.split("_")[1])
    except Exception:
        await query.edit_message_text("Serviço inválido.")
        return ESCOLHENDO_SERVICOS

    with get_db_session() as db:
        servico = db.get(Service, service_id)
        if not servico:
            await query.edit_message_text("Serviço inválido.")
            return ESCOLHENDO_SERVICOS

        servicos = context.user_data.get("servicos_escolhidos", [])
        if servico.id not in [s['id'] for s in servicos]:
            servicos.append({
                "id": servico.id,
                "nome": servico.name,
                "duration": servico.duration,
                "price": getattr(servico, "price", 0.0),
            })
            context.user_data["servicos_escolhidos"] = servicos

    botoes = [
        [InlineKeyboardButton("Adicionar outro serviço ➕", callback_data="add_more")],
        [InlineKeyboardButton("Finalizar seleção ✅", callback_data="finish")],
    ]
    markup = InlineKeyboardMarkup(botoes)
    servicos_texto = "\n".join([f"💇‍♀️ {s['nome']} — R$ {s['price']}" for s in servicos])
    await query.edit_message_text(f"Serviços escolhidos até agora:\n{servicos_texto}", reply_markup=markup)
    return ESCOLHENDO_SERVICOS

async def decidir_mais_servicos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "add_more":
        await mostrar_servicos(update, context)
        return ESCOLHENDO_SERVICOS
    else:
        await mostrar_datas(update, context)
        return ESCOLHENDO_DATA

async def mostrar_datas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with get_db_session() as db:
        service_ids = [s["id"] for s in context.user_data.get("servicos_escolhidos", [])]
        service_id = service_ids[0] if service_ids else None
        teclado_datas = gerar_teclado_datas(db, service_id)
    await update.callback_query.edit_message_text("Escolha a data:", reply_markup=teclado_datas)

async def escolher_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        data_str = query.data.split("_", 1)[1]
        data = datetime.fromisoformat(data_str).date()
    except Exception:
        await query.edit_message_text("Data inválida.")
        return ESCOLHENDO_DATA

    context.user_data["data_escolhida"] = data
    with get_db_session() as db:
        service_ids = [s["id"] for s in context.user_data.get("servicos_escolhidos", [])]
        horarios_livres = horarios_disponiveis_para_data(db, service_ids, data)

    teclado_horarios = gerar_teclado_horarios(horarios_livres)
    await query.edit_message_text("Escolha o horário:", reply_markup=teclado_horarios)
    return ESCOLHENDO_HORARIO

async def escolher_horario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    hora_str = query.data.split("_", 1)[1]
    horario = datetime.strptime(hora_str, "%H:%M").time()
    context.user_data["horario_escolhido"] = horario
    await query.edit_message_text("Digite seu nome e sobrenome:")
    return INSERINDO_NOME

# ---------------------------
# Inserção de dados do cliente
# ---------------------------
async def inserir_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = update.message.text.strip()
    if not validar_nome(nome):
        await update.message.reply_text(
            "Nome inválido. Digite apenas letras e espaços, ex: Maria Silva"
        )
        return INSERINDO_NOME

    context.user_data["nome"] = nome
    await update.message.reply_text("Digite seu telefone! (somente números, ex: 11999999999):")
    return INSERINDO_TELEFONE

async def inserir_telefone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telefone = ''.join(filter(str.isdigit, update.message.text.strip()))
    if not telefone or len(telefone) < 10:
        await update.message.reply_text(
            "Número de telefone inválido. Digite apenas números com DDD, ex: 11999999999"
        )
        return INSERINDO_TELEFONE

    context.user_data["telefone"] = telefone
    await update.message.reply_text("Digite seu email! (ex: exemplo@dominio.com):")
    return INSERINDO_EMAIL

async def inserir_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if not validar_email(email):
        await update.message.reply_text("Email inválido. Digite novamente, ex: exemplo@dominio.com")
        return INSERINDO_EMAIL

    context.user_data["email"] = email
    return await escolher_cor_cabelo_prompt(update, context)

# ---------------------------
# Seleção de cabelo
# ---------------------------
async def escolher_cor_cabelo_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botoes = [
        [InlineKeyboardButton("Castanho", callback_data="cor_castanho")],
        [InlineKeyboardButton("Preto", callback_data="cor_preto")],
        [InlineKeyboardButton("Loiro", callback_data="cor_loiro")],
        [InlineKeyboardButton("Ruivo", callback_data="cor_ruivo")],
        [InlineKeyboardButton("Platinado-Branco", callback_data="cor_platinado")],
    ]
    markup = InlineKeyboardMarkup(botoes)
    if update.message:
        await update.message.reply_text("Escolha a cor do seu cabelo:", reply_markup=markup)
    else:
        await update.callback_query.edit_message_text("Escolha a cor do seu cabelo:", reply_markup=markup)
    return ESCOLHENDO_COR_CABELO

async def escolher_cor_cabelo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cor_cabelo"] = query.data.replace("cor_", "")
    tipos = ["Liso", "Ondulado", "Cacheado", "Crespo"]
    botoes = [[InlineKeyboardButton(tipo, callback_data=f"tipo_{tipo.lower()}")] for tipo in tipos]
    await query.edit_message_text("Escolha o tipo do seu cabelo:", reply_markup=InlineKeyboardMarkup(botoes))
    return ESCOLHENDO_TIPO_CABELO

async def escolher_tipo_cabelo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["tipo_cabelo"] = query.data.replace("tipo_", "")
    botoes = [
        [InlineKeyboardButton("Curto", callback_data="tamanho_curto")],
        [InlineKeyboardButton("Médio", callback_data="tamanho_medio")],
        [InlineKeyboardButton("Longo", callback_data="tamanho_longo")],
    ]
    await query.edit_message_text("Escolha o tamanho do seu cabelo:", reply_markup=InlineKeyboardMarkup(botoes))
    return ESCOLHENDO_TAMANHO_CABELO

# ---------------------------
# Confirmação
# ---------------------------
async def mostrar_confirmacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data
    servicos_texto = "\n".join([f"💇‍♀️ {s['nome']} — R$ {s['price']}" for s in dados["servicos_escolhidos"]])
    total = sum([s['price'] for s in dados["servicos_escolhidos"]])
    texto = f"""

Você selecionou:
{servicos_texto}
Total: R$ {total}
Data: {dados['data_escolhida'].strftime('%d/%m/%Y')}
Horário: {dados['horario_escolhido'].strftime('%H:%M')}

Seus dados:
Nome: {dados['nome']}
Telefone: {dados['telefone']}
Email: {dados['email']}
Cor do cabelo: {dados['cor_cabelo']}
Tipo: {dados['tipo_cabelo']}
Tamanho: {dados['tamanho_cabelo']}
"""
    botoes = [
        [InlineKeyboardButton("Confirmar ✅", callback_data="confirmar")],
        [InlineKeyboardButton("Cancelar ❌", callback_data="cancelar")],
    ]
    markup = InlineKeyboardMarkup(botoes)
    if update.message:
        await update.message.reply_text(texto, reply_markup=markup)
    else:
        await update.callback_query.edit_message_text(texto, reply_markup=markup)
    return CONFIRMANDO

async def escolher_tamanho_cabelo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["tamanho_cabelo"] = query.data.replace("tamanho_", "")
    return await mostrar_confirmacao(update, context)

# ---------------------------
# Finalização / Cancelamento
# ---------------------------
async def confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    dados = context.user_data
    with get_db_session() as db:
        cliente = Client(name=dados['nome'], phone=dados['telefone'], email=dados['email'])
        db.add(cliente)
        db.commit()

        for s in dados['servicos_escolhidos']:
            agendamento = Appointment(
                client_id=cliente.id,
                service_id=s['id'],
                date=datetime.combine(dados['data_escolhida'], dados['horario_escolhido']),
                status=AppointmentStatus.confirmado.value,
                cor_cabelo=dados['cor_cabelo'],
                tipo_cabelo=dados['tipo_cabelo'],
                tamanho_cabelo=dados['tamanho_cabelo']
            )
            db.add(agendamento)
        db.commit()

    await query.edit_message_text("✅ Agendamento concluído com sucesso! \nFavor, aguardar confirmação do profissional! Obrigado.")
    return ConversationHandler.END

async def cancelar_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Agendamento cancelado.")
    else:
        await update.message.reply_text("❌ Agendamento cancelado.")
    return ConversationHandler.END

# ---------------------------
# ConversationHandler
# ---------------------------
def get_conversation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("agendar", agendar),
            CallbackQueryHandler(agendar, pattern="^agendar$"),
            CallbackQueryHandler(mostrar_servicos, pattern="^servicos$"),
            CallbackQueryHandler(start, pattern="^start_over$"),
            CallbackQueryHandler(cancelar_comando, pattern="^cancelar$")
        ],
        states={
            ESCOLHENDO_SERVICOS: [
                CallbackQueryHandler(escolher_servicos, pattern="^servico_"),
                CallbackQueryHandler(decidir_mais_servicos, pattern="^(add_more|finish)$")
            ],
            ESCOLHENDO_DATA: [CallbackQueryHandler(escolher_data, pattern="^data_")],
            ESCOLHENDO_HORARIO: [CallbackQueryHandler(escolher_horario, pattern="^horario_")],
            INSERINDO_NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, inserir_nome)],
            INSERINDO_TELEFONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, inserir_telefone)],
            INSERINDO_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, inserir_email)],
            ESCOLHENDO_COR_CABELO: [CallbackQueryHandler(escolher_cor_cabelo, pattern="^cor_")],
            ESCOLHENDO_TIPO_CABELO: [CallbackQueryHandler(escolher_tipo_cabelo, pattern="^tipo_")],
            ESCOLHENDO_TAMANHO_CABELO: [CallbackQueryHandler(escolher_tamanho_cabelo, pattern="^tamanho_")],
            CONFIRMANDO: [
                CallbackQueryHandler(confirmar, pattern="^confirmar$"),
                CallbackQueryHandler(cancelar_comando, pattern="^cancelar$")
            ],
        },
        fallbacks=[CommandHandler("cancelar", cancelar_comando)],
        per_message=False,
        per_user=True
    )
