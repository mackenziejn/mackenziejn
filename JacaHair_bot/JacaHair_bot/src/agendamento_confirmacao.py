# src/agendamento_confirmacao.py

def confirmar(agendamento):
    print("\n✅ Agendamento confirmado com sucesso!")
    print("Detalhes do agendamento:")
    for chave, valor in agendamento.items():
        print(f"{chave.capitalize()}: {valor}")
    return True

def cancelar():
    print("\n❌ Agendamento cancelado.")
    return False

def cancelar_comando(comando):
    comandos_cancelamento = ["cancelar", "sair", "parar", "não quero"]
    return comando.strip().lower() in comandos_cancelamento

from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

def get_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("agendar", iniciar_agendamento)],
        states={
            ESCOLHER_SERVICO: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_servico)],
            ESCOLHER_HORARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_horario)],
            CONFIRMAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_agendamento)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar_agendamento)],
        per_message=False  # ou True, dependendo da lógica
    )

