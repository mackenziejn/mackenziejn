# test_db_full.py
from src.database import engine
from sqlalchemy import inspect, text

inspector = inspect(engine)
tabelas = inspector.get_table_names()

print("📋 Tabelas no banco de dados:")
for tabela in tabelas:
    print(f"• {tabela}")

    # Colunas
    colunas = inspector.get_columns(tabela)
    print(f"  📌 Colunas:")
    for col in colunas:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = col['default'] if col['default'] is not None else ""
        print(f"    - {col['name']} ({col['type']}) {nullable} {default}")

    # Chave primária
    pk = inspector.get_pk_constraint(tabela)
    if pk and pk.get('constrained_columns'):
        print(f"  🔑 Chave primária: {pk['constrained_columns']}")

    # Chaves estrangeiras
    fks = inspector.get_foreign_keys(tabela)
    if fks:
        print(f"  🔗 Chaves estrangeiras:")
        for fk in fks:
            print(f"    - {fk['constrained_columns']} → {fk['referred_table']}({fk['referred_columns']})")

    # Índices
    indices = inspector.get_indexes(tabela)
    if indices:
        print(f"  🏷️ Índices:")
        for idx in indices:
            print(f"    - {idx['name']} ({idx['column_names']})")

    # Constraints extras (SQLite não fornece muito detalhado, mas podemos listar CHECKs via pragma)
    if "sqlite" in str(engine.url):
        with engine.connect() as conn:
            res = conn.execute(text(f"PRAGMA table_info({tabela})"))
            checks = [row for row in res if row['type'] and "CHECK" in row['type']]
            if checks:
                print(f"  ⚠️ Constraints adicionais: {checks}")

print("\n✅ Inspeção do banco concluída!")
