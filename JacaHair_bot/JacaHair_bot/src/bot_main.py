# src/bot_main.py

import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from src.utils import load_messages, get_bot_token
from src.handlers import get_conversation_handler  # Sua função existente

# ---------------------------
# Logger
# ---------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------
# Carregar mensagens e token
# ---------------------------
messages = load_messages()
bot_token = get_bot_token()

if not bot_token:
    logger.error("❌ Token do bot inválido. Verifique o config.yml.")
    exit(1)

# Mensagem de boas-vindas para teste
start_msg = messages.get("start_message", "🐊 Olá! Bem-vindo ao JacaHair Bot!")
logger.info(f"Mensagem de boas-vindas: {start_msg}")

# ---------------------------
# Função start / comando inicial
# ---------------------------
async def start(update, context):
    await update.message.reply_text(start_msg)

# ---------------------------
# Inicializar e rodar bot
# ---------------------------
async def main():
    # Cria a aplicação do bot
    application = ApplicationBuilder().token(bot_token).build()

    # Adiciona comando /start
    application.add_handler(CommandHandler("start", start))

    # Adiciona ConversationHandler do seu handlers.py
    conv_handler = get_conversation_handler()
    application.add_handler(conv_handler)

    # Inicia o bot
    logger.info("🚀 Iniciando JacaHair Bot...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
