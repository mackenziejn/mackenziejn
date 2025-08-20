# get_chat_ids.py

"""
Script utilitário para obter chat IDs de mensagens recentes enviadas ao bot.
"""

import os
import asyncio
from telegram import Bot

# ⚠️ Use variável de ambiente para segurança
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    print("❌ Token do bot não encontrado. Defina TELEGRAM_BOT_TOKEN no ambiente.")
    exit(1)

async def main():
    bot = Bot(token=TOKEN)

    try:
        updates = await bot.get_updates(offset=0, timeout=10)
    except Exception as e:
        print(f"❌ Erro ao buscar updates: {e}")
        return

    if not updates:
        print("ℹ️ Nenhuma mensagem recente encontrada. Envie uma mensagem para o bot primeiro.")
        return

    print("📨 Updates recebidos:")
    for update in updates:
        if update.message:
            chat = update.message.chat
            chat_type = chat.type
            chat_name = chat.title or chat.username or chat.first_name or "Desconhecido"
            print(f"✅ Chat ID: {chat.id} | Tipo: {chat_type} | Nome: {chat_name}")
        else:
            print("⚠️ Update sem mensagem:", update)

if __name__ == "__main__":
    asyncio.run(main())
