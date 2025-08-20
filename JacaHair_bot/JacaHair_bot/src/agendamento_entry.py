# src/agendamento_entry.py

def escolher_servico():
    """
    Exibe os serviços disponíveis e permite que o usuário escolha um.
    """
    servicos = ["Corte", "Coloração", "Barba", "Bigode", "Sombrancelah",]
    print("Serviços disponíveis:")
    for i, servico in enumerate(servicos, start=1):
        print(f"{i}. {servico}")
    escolha = input("Digite o número do serviço desejado: ")
    try:
        return servicos[int(escolha) - 1]
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return None

def agendar(servico):
    """
    Agenda o serviço escolhido para uma data e hora.
    """
    data = input("Digite a data do agendamento (DD/MM/AAAA): ")
    hora = input("Digite o horário do agendamento (HH:MM): ")
    print(f"Agendamento confirmado: {servico} em {data} às {hora}.")

def iniciar_agendamento():
    """
    Inicia o processo completo de agendamento.
    """
    servico = escolher_servico()
    if servico:
        agendar(servico)
    else:
        print("Não foi possível iniciar o agendamento.")

# src/agendamento_data.py

def escolher_data():
    print("Função escolher_data chamada.")
    data = input("Digite a data desejada (DD/MM/AAAA): ")
    return data

def escolher_horario():
    print("Função escolher_horario chamada.")
    horario = input("Digite o horário desejado (HH:MM): ")
    return horario
