# init_db.py

"""
Script unificado para inicializar ou resetar o banco do JacaHair Bot.
⚠️ Remove dados existentes! Use com cuidado.
"""

import os
import sqlite3
from src.database import DB_PATH, Base, engine, populate_initial_services

# ---------------------------
# Funções auxiliares
# ---------------------------
def apagar_banco():
    if DB_PATH and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️ Banco SQLite antigo removido: {DB_PATH}")
    else:
        print("⚠️ Banco SQLite não encontrado. Será criado um novo.")

def recriar_tabelas():
    # Derruba tabelas antigas
    Base.metadata.drop_all(bind=engine)
    print("💥 Todas as tabelas foram removidas.")

    # Cria novamente
    Base.metadata.create_all(bind=engine)
    print("🧱 Todas as tabelas foram recriadas.")

def popular_servicos():
    populate_initial_services()
    print("✨ Serviços iniciais cadastrados.")

def mostrar_colunas(tabela):
    if not DB_PATH or not os.path.exists(DB_PATH):
        print(f"⚠️ Banco não encontrado, não é possível mostrar colunas de {tabela}.")
        return

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute(f"PRAGMA table_info({tabela});")
    colunas = cursor.fetchall()
    print(f"\n📋 Colunas da tabela '{tabela}':")
    for col in colunas:
        print(f"• {col[1]} ({col[2]})")
    con.close()

# ---------------------------
# Função principal
# ---------------------------
def init_db_unificado():
    apagar_banco()
    recriar_tabelas()
    popular_servicos()
    for tabela in ["appointments", "clients", "services", "espera_encaixe"]:
        mostrar_colunas(tabela)
    print("\n✅ Banco inicializado com sucesso! Pronto para rodar o bot.")

# ---------------------------
# Execução direta
# ---------------------------
if __name__ == "__main__":
    confirm = input("⚠️ Isso apagará todos os dados existentes. Deseja continuar? (s/n): ")
    if confirm.lower() != "s":
        print("❌ Operação cancelada.")
    else:
        init_db_unificado()
