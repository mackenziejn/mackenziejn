# src/app.py

import logging
import nest_asyncio
import threading
import asyncio
import os
from flask import Flask, request, jsonify

from telegram.ext import ApplicationBuilder, CommandHandler
from src.handlers import get_conversation_handler, start, cancelar_comando
from src.utils import load_config
from src.database import get_db_session
from src.models import Appointment, AppointmentStatus

# ---------------------------
# Configuração de logging
# ---------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("werkzeug").setLevel(logging.WARNING)  # silencia logs HTTP
nest_asyncio.apply()

# ---------------------------
# Flask App
# ---------------------------
app = Flask(__name__)

@app.route("/confirmacao", methods=["GET"])
def confirmacao():
    """Confirmação de agendamento via link GET"""
    agendamento_id = request.args.get("id")
    if not agendamento_id:
        return jsonify({"error": "Parâmetro 'id' é obrigatório."}), 400

    try:
        agendamento_id = int(agendamento_id)
    except ValueError:
        return jsonify({"error": "ID inválido."}), 400

    with get_db_session() as db:
        agendamento = db.get(Appointment, agendamento_id)
        if not agendamento:
            return jsonify({"error": "Agendamento não encontrado."}), 404

        if agendamento.status == AppointmentStatus.confirmado.value:
            return jsonify({"message": "Agendamento já estava confirmado."}), 200

        agendamento.status = AppointmentStatus.confirmado.value
        db.commit()
        logger.info(f"✅ Agendamento {agendamento_id} confirmado via Flask")
        return jsonify({"message": f"Agendamento {agendamento_id} confirmado com sucesso."}), 200

@app.route("/healthz")
def health_check():
    """Rota para Render health check"""
    return jsonify({"status": "ok"}), 200

def run_flask():
    config = load_config()
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🌐 Servidor Flask iniciado em 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)

# ---------------------------
# Bot Telegram
# ---------------------------
async def error_handler(update, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

async def run_bot():
    config = load_config()
    logger.info("⚙️ Config carregada.")

    token = os.environ.get("TELEGRAM_BOT_TOKEN") or config["telegram"]["token"]
    if not token:
        logger.error("❌ Token do bot Telegram não encontrado.")
        return

    application = ApplicationBuilder().token(token).build()
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(get_conversation_handler())
    application.add_handler(CommandHandler("cancelar", cancelar_comando))
    application.add_error_handler(error_handler)

    logger.info("🤖 Bot iniciado. Rodando polling...")
    await application.run_polling()

# ---------------------------
# Ponto de entrada
# ---------------------------
if __name__ == "__main__":
    # Flask em thread separada
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Bot rodando na main thread
    asyncio.run(run_bot())
