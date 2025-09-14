# main.py
from db_manager import DatabaseManager
from managers.paciente_manager import PacienteManager
from managers.profissional_manager import ProfissionalManager
from managers.consulta_manager import ConsultaManager
import os

# --- Funções Auxiliares de Interface ---
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("\nPressione Enter para continuar...")

# --- Menus ---
def menu_pacientes(manager: PacienteManager):
    while True:
        limpar_tela()
        print("=== Menu de Pacientes ===")
        print("1 - Listar todos")
        print("2 - Exibir por ID")
        print("3 - Inserir novo")
        print("4 - Alterar telefone")
        print("5 - Pesquisar por nome")
        print("6 - Remover")
        print("0 - Voltar")

        escolha = input("\n> ")

        if escolha == '1':
            resultados = manager.listar_todos()
            for r in resultados:
                print(r)
        elif escolha == '2':
            pid = int(input("ID do paciente: "))
            print(manager.buscar_por_id(pid))
        elif escolha == '3':
            nome = input("Nome: ")
            sexo = input("Sexo (M/F/O): ").upper()
            email = input("Email: ")
            cpf = input("CPF: ")
            telefone = input("Telefone: ")
            novo = (nome, sexo, email, cpf, telefone)
            print("Novo paciente:", manager.inserir(novo))
        elif escolha == '4':
            pid = int(input("ID: "))
            tel = input("Novo telefone: ")
            manager.atualizar_telefone(pid, tel)
        elif escolha == '5':
            nome = input("Nome para pesquisa: ")
            print(manager.buscar_por_nome(nome))
        elif escolha == '6':
            pid = int(input("ID: "))
            manager.remover(pid)
        elif escolha == '0':
            break
        else:
            print("Opção inválida!")
        pausar()

def menu_profissionais(manager: ProfissionalManager):
    while True:
        limpar_tela()
        print("=== Menu de Profissionais ===")
        print("1 - Listar todos")
        print("2 - Exibir por ID")
        print("3 - Inserir novo")
        print("4 - Alterar telefone")
        print("5 - Pesquisar por nome")
        print("6 - Remover")
        print("0 - Voltar")

        escolha = input("\n> ")

        if escolha == '1':
            print(manager.listar_todos())
        elif escolha == '2':
            pid = int(input("ID do profissional: "))
            print(manager.buscar_por_id(pid))
        elif escolha == '3':
            nome = input("Nome: ")
            telefone = input("Telefone: ")
            email = input("Email: ")
            crm = input("CRM: ")
            especialidade = input("Especialidade: ")
            novo = (nome, telefone, email, crm, especialidade)
            print("Novo profissional:", manager.inserir(novo))
        elif escolha == '4':
            pid = int(input("ID: "))
            tel = input("Novo telefone: ")
            manager.atualizar_telefone(pid, tel)
        elif escolha == '5':
            nome = input("Nome para pesquisa: ")
            print(manager.buscar_por_nome(nome))
        elif escolha == '6':
            pid = int(input("ID: "))
            manager.remover(pid)
        elif escolha == '0':
            break
        else:
            print("Opção inválida!")
        pausar()

def menu_consultas(manager: ConsultaManager):
    while True:
        limpar_tela()
        print("=== Menu de Consultas ===")
        print("1 - Listar todas")
        print("2 - Exibir por ID")
        print("3 - Inserir nova")
        print("4 - Atualizar status")
        print("5 - Remover")
        print("0 - Voltar")

        escolha = input("\n> ")

        if escolha == '1':
            print(manager.listar_todas())
        elif escolha == '2':
            cid = int(input("ID da consulta: "))
            print(manager.buscar_por_id(cid))
        elif escolha == '3':
            paciente_id = int(input("ID do paciente: "))
            profissional_id = int(input("ID do profissional: "))
            data = input("Data (YYYY-MM-DD HH:MM): ")
            motivo = input("Motivo: ")
            status = "Agendada"
            nova = (paciente_id, profissional_id, data, motivo, status)
            print("Nova consulta:", manager.inserir(nova))
        elif escolha == '4':
            cid = int(input("ID da consulta: "))
            status = input("Novo status (Agendada/Realizada/Cancelada): ")
            manager.atualizar_status(cid, status)
        elif escolha == '5':
            cid = int(input("ID da consulta: "))
            manager.remover(cid)
        elif escolha == '0':
            break
        else:
            print("Opção inválida!")
        pausar()

def menu_principal(db):
    paciente_manager = PacienteManager(db)
    profissional_manager = ProfissionalManager(db)
    consulta_manager = ConsultaManager(db)

    while True:
        limpar_tela()
        print("=== Sistema de Gestão da Clínica ===")
        print("1 - Gerir Pacientes")
        print("2 - Gerir Profissionais")
        print("3 - Gerir Consultas")
        print("0 - Sair")

        escolha = input("\n> ")

        if escolha == '1':
            menu_pacientes(paciente_manager)
        elif escolha == '2':
            menu_profissionais(profissional_manager)
        elif escolha == '3':
            menu_consultas(consulta_manager)
        elif escolha == '0':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")
            pausar()

# --- Execução ---
if __name__ == "__main__":
    db = DatabaseManager()
    db.connect()
    if db.conn:
        menu_principal(db)
        db.disconnect()
