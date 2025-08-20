# src/agendamento_cabelo.py

def escolher_tipo_cabelo():
    tipos = ["Liso", "Ondulado", "Cacheado", "Crespo"]
    print("Tipos de cabelo disponíveis:")
    for i, tipo in enumerate(tipos, start=1):
        print(f"{i}. {tipo}")
    escolha = input("Digite o número correspondente ao seu tipo de cabelo: ")
    try:
        return tipos[int(escolha) - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return None

def escolher_tratamento():
    tratamentos = ["Hidratação", "Reconstrução", "Nutrição", "Selagem"]
    print("Tratamentos disponíveis:")
    for i, tratamento in enumerate(tratamentos, start=1):
        print(f"{i}. {tratamento}")
    escolha = input("Digite o número do tratamento desejado: ")
    try:
        return tratamentos[int(escolha) - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return None

def escolher_cor_cabelo():
    cores = ["Preto", "Castanho", "Loiro", "Ruivo", "Colorido"]
    print("Cores de cabelo disponíveis:")
    for i, cor in enumerate(cores, start=1):
        print(f"{i}. {cor}")
    escolha = input("Digite o número correspondente à cor desejada: ")
    try:
        return cores[int(escolha) - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return None

def escolher_tamanho_cabelo():
    tamanhos = ["Curto", "Médio", "Longo", "Muito longo"]
    print("Tamanhos de cabelo disponíveis:")
    for i, tamanho in enumerate(tamanhos, start=1):
        print(f"{i}. {tamanho}")
    escolha = input("Digite o número correspondente ao tamanho do cabelo: ")
    try:
        return tamanhos[int(escolha) - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return None

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

