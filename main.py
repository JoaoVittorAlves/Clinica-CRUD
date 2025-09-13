# Arquivo principal para executar exemplos

from db_manager import DatabaseManager
import sql_queries as queries
import os

# --- Funções Auxiliares de Interface ---

def limpar_tela():
    """Limpa o terminal para uma melhor experiência de usuário."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    """Pausa a execução até que o usuário pressione Enter."""
    input("\nPressione Enter para continuar...")

# --- Funções de Operações no Banco de Dados ---

def listar_todos_pacientes(db_manager):
    print("\n--- 5. LISTANDO TODOS OS PACIENTES ---")
    resultados = db_manager.fetch_query(queries.LISTAR_TODOS_PACIENTES)
    if not resultados:
        print("Nenhum paciente cadastrado.")
        return
    
    for r in resultados:
        print(f"  ID: {r[0]}, Nome: {r[1]}, Email: {r[2]}, Telefone: {r[3]}")

def exibir_um_paciente(db_manager):
    print("\n--- 6. EXIBINDO UM PACIENTE ---")
    try:
        paciente_id = int(input("Digite o ID do paciente: "))
    except ValueError:
        print("Erro: ID inválido. Por favor, digite um número.")
        return

    resultado = db_manager.fetch_query(queries.SELECIONAR_PACIENTE_POR_ID, (paciente_id,))
    if not resultado:
        print(f"Paciente com ID {paciente_id} não encontrado.")
        return
        
    paciente = resultado[0]
    print(f"\n  Detalhes do Paciente ID {paciente_id}:")
    print(f"  - Nome: {paciente[1]}")
    print(f"  - Email: {paciente[2]}")
    print(f"  - Telefone: {paciente[3]}")
    print(f"  - Cidade: {paciente[4]}, Estado: {paciente[5]}")

def inserir_novo_paciente(db_manager):
    print("\n--- 1. INSERINDO NOVO PACIENTE ---")
    nome = input("Nome completo: ")
    sexo = input("Sexo (M/F/O): ").upper()
    email = input("Email: ")
    cpf = input("CPF (apenas números): ")
    telefone = input("Telefone (xxxxxxxxx): ")
    
    paciente_novo = (nome, sexo, email, cpf, telefone)
    resultado = db_manager.execute_and_fetch_one(queries.INSERIR_PACIENTE, paciente_novo)
    
    if resultado:
        novo_id = resultado[0]
        print(f"\nPaciente '{nome}' inserido com sucesso! ID: {novo_id}")
    else:
        print("\nFalha ao inserir paciente. Verifique os dados e tente novamente.")

def alterar_paciente(db_manager):
    print("\n--- 2. ALTERANDO PACIENTE ---")
    try:
        paciente_id = int(input("Digite o ID do paciente que deseja alterar: "))
        novo_telefone = input(f"Digite o NOVO telefone para o paciente {paciente_id}: ")
    except ValueError:
        print("Erro: ID inválido. Por favor, digite um número.")
        return

    if db_manager.execute_query(queries.ATUALIZAR_TELEFONE_PACIENTE, (novo_telefone, paciente_id)):
        print(f"\nTelefone do paciente {paciente_id} atualizado com sucesso!")
    else:
        print("\nFalha ao atualizar paciente. Verifique se o ID existe.")

def pesquisar_por_nome(db_manager):
    print("\n--- 3. PESQUISANDO PACIENTE POR NOME ---")
    nome = input("Digite o nome ou parte do nome a ser pesquisado: ")
    parametro_busca = f"%{nome}%"
    resultados = db_manager.fetch_query(queries.PESQUISAR_PACIENTE_POR_NOME, (parametro_busca,))
    
    if not resultados:
        print("Nenhum paciente encontrado com esse nome.")
        return
        
    print("\nResultados encontrados:")
    for r in resultados:
        print(f"  ID: {r[0]}, Nome: {r[1]}, Email: {r[2]}")

def remover_paciente(db_manager):
    print("\n--- 4. REMOVENDO PACIENTE ---")
    try:
        paciente_id = int(input("Digite o ID do paciente que deseja remover: "))
    except ValueError:
        print("Erro: ID inválido. Por favor, digite um número.")
        return

    # Confirmação para segurança
    confirmacao = input(f"Tem certeza que deseja remover o paciente ID {paciente_id}? (s/n): ").lower()
    if confirmacao != 's':
        print("Operação cancelada.")
        return

    if db_manager.execute_query(queries.REMOVER_PACIENTE, (paciente_id,)):
        print(f"\nPaciente com ID {paciente_id} removido com sucesso!")
    else:
        print("\nFalha ao remover paciente. Verifique se o ID existe.")


# --- Execução Principal ---

def menu_principal(db):
    """Renderiza o menu principal e gerencia as escolhas do usuário."""
    while True:
        limpar_tela()
        print("=========================================")
        print("===   Sistema de Gestão da Clínica    ===")
        print("=========================================")
        print("\nEscolha uma opção para a tabela de PACIENTES:")
        print("  1 - Listar todos os pacientes")
        print("  2 - Exibir detalhes de um paciente")
        print("  3 - Inserir novo paciente")
        print("  4 - Alterar telefone de um paciente")
        print("  5 - Pesquisar paciente por nome")
        print("  6 - Remover paciente")
        print("\n  0 - Sair")
        
        escolha = input("\n> ")

        limpar_tela()
        if escolha == '1':
            listar_todos_pacientes(db)
        elif escolha == '2':
            exibir_um_paciente(db)
        elif escolha == '3':
            inserir_novo_paciente(db)
        elif escolha == '4':
            alterar_paciente(db)
        elif escolha == '5':
            pesquisar_por_nome(db)
        elif escolha == '6':
            remover_paciente(db)
        elif escolha == '0':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")
        
        pausar()


if __name__ == "__main__":
    db = DatabaseManager()
    db.connect()
    if db.conn:
        menu_principal(db)
        db.disconnect()