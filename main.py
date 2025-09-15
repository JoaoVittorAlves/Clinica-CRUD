# Arquivo principal para executar exemplos

import os
from db_manager import DatabaseManager
from queries import cadastros_queries, clinico_queries, financeiro_queries

MENU_CONFIG = {
    'cadastros': {
        'nome': 'Cadastros',
        'tabelas': {
            'pacientes': {
                'nome': 'Pacientes',
                'queries': {
                    'listar': cadastros_queries.LISTAR_TODOS_PACIENTES,
                    'exibir_um': cadastros_queries.SELECIONAR_PACIENTE_POR_ID,
                    'pesquisar_nome': cadastros_queries.PESQUISAR_PACIENTE_POR_NOME,
                    'remover': cadastros_queries.REMOVER_PACIENTE,
                    'inserir': cadastros_queries.INSERIR_PACIENTE,
                    'alterar_telefone': cadastros_queries.ATUALIZAR_TELEFONE_PACIENTE
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todos', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Exibir Um por ID', 'handler': 'exibir_um'},
                    {'opcao': '3', 'nome': 'Inserir Novo', 'handler': 'inserir'},
                    {'opcao': '4', 'nome': 'Alterar Telefone', 'handler': 'alterar', 'key': 'alterar_telefone'},
                    {'opcao': '5', 'nome': 'Pesquisar por Nome', 'handler': 'pesquisar', 'key': 'pesquisar_nome'},
                    {'opcao': '6', 'nome': 'Remover por ID', 'handler': 'remover'}
                ],
                'insert_fields': ['Nome', 'Sexo (M/F/O)', 'Email', 'CPF', 'Telefone', 'Logradouro', 'Número', 'Complemento', 'Bairro', 'Cidade', 'Estado (UF)', 'CEP'],
                'prompts': {
                    'alterar_telefone': 'Digite o NOVO telefone para o paciente',
                    'pesquisar_nome': 'Digite o nome ou parte do nome a ser pesquisado'
                }
            },
            'medicos': {
                'nome': 'Médicos',
                'queries': {
                    'listar': cadastros_queries.LISTAR_TODOS_MEDICOS,
                    'exibir_um': cadastros_queries.SELECIONAR_MEDICO_POR_CRM, 
                    'pesquisar_nome': cadastros_queries.PESQUISAR_MEDICO_POR_NOME,
                    'pesquisar_especialidade': cadastros_queries.PESQUISAR_MEDICO_POR_ESPECIALIDADE,
                    'remover': cadastros_queries.REMOVER_MEDICO,
                    'inserir': cadastros_queries.INSERIR_MEDICO,
                    'alterar_salario': cadastros_queries.ATUALIZAR_SALARIO_MEDICO
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todos', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Exibir Um por CRM', 'handler': 'exibir_um', 'prompt': 'Digite o CRM do médico'},
                    {'opcao': '3', 'nome': 'Inserir Novo', 'handler': 'inserir'},
                    {'opcao': '4', 'nome': 'Alterar Salário', 'handler': 'alterar', 'key': 'alterar_salario'},
                    {'opcao': '5', 'nome': 'Pesquisar por Nome', 'handler': 'pesquisar', 'key': 'pesquisar_nome'},
                    {'opcao': '6', 'nome': 'Pesquisar por Especialidade', 'handler': 'pesquisar', 'key': 'pesquisar_especialidade'},
                    {'opcao': '7', 'nome': 'Remover por ID', 'handler': 'remover'}
                ],
                'insert_fields': ['Nome', 'Telefone', 'Email', 'CRM', 'Salário', 'ID da Especialidade', 'Logradouro', 'Número', 'Complemento', 'Bairro', 'Cidade', 'Estado (UF)', 'CEP'],
                'prompts': {
                    'alterar_salario': 'Digite o NOVO salário para o médico',
                    'pesquisar_nome': 'Digite o nome do médico',
                    'pesquisar_especialidade': 'Digite o nome da especialidade'
                }
            },
            'especialidades': {
                'nome': 'Especialidades',
                'queries': {
                    'listar': cadastros_queries.LISTAR_TODAS_ESPECIALIDADES,
                    'remover': cadastros_queries.REMOVER_ESPECIALIDADE,
                    'check_delete': cadastros_queries.VERIFICAR_MEDICOS_POR_ESPECIALIDADE,
                    'alterar_status': cadastros_queries.ATUALIZAR_STATUS_ESPECIALIDADE,
                    'inserir': cadastros_queries.INSERIR_ESPECIALIDADE,
                    'pesquisar_nome': cadastros_queries.PESQUISAR_ESPECIALIDADE_POR_NOME,
                    'exibir_um': cadastros_queries.SELECIONAR_ESPECIALIDADE_POR_ID
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todas', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Exibir Uma por ID', 'handler': 'exibir_um'},
                    {'opcao': '3', 'nome': 'Inserir Nova', 'handler': 'inserir'},
                    {'opcao': '4', 'nome': 'Pesquisar por Nome', 'handler': 'pesquisar', 'key': 'pesquisar_nome'},
                    {'opcao': '5', 'nome': 'Alterar Status (Ativa/Inativa)', 'handler': 'alterar_status_especialidade'}, 
                    {'opcao': '6', 'nome': 'Remover (com verificação)', 'handler': 'remover_seguro'} 
                ],
                'insert_fields': ['Nome da Especialidade', 'Está ativa? (True/False)'],
                'prompts': {
                    'pesquisar_nome': 'Digite o nome ou parte do nome da especialidade'
                }
            },
            'funcionarios': {
                'nome': 'Funcionários',
                'queries': { 
                    'listar': cadastros_queries.LISTAR_TODOS_FUNCIONARIOS,
                    'exibir_um': cadastros_queries.SELECIONAR_FUNCIONARIO_POR_ID,
                    'inserir': cadastros_queries.INSERIR_FUNCIONARIO,
                    'pesquisar_nome': cadastros_queries.PESQUISAR_FUNCIONARIO_POR_NOME,
                    'pesquisar_contrato': cadastros_queries.PESQUISAR_FUNCIONARIO_POR_TIPO_DE_CONTRATO,
                    'remover': cadastros_queries.REMOVER_FUNCIONARIO,
                    'alterar_perfil': cadastros_queries.ATUALIZAR_PERFIL_ACESSO_FUNCIONARIO
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todos', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Exibir Um por ID', 'handler': 'exibir_um'},
                    {'opcao': '3', 'nome': 'Inserir Novo', 'handler': 'inserir'},
                    {'opcao': '4', 'nome': 'Alterar Perfil de Acesso', 'handler': 'alterar_perfil_funcionario'}, 
                    {'opcao': '5', 'nome': 'Pesquisar por Nome', 'handler': 'pesquisar', 'key': 'pesquisar_nome'},
                    {'opcao': '6', 'nome': 'Pesquisar por Tipo de Contrato', 'handler': 'pesquisar', 'key': 'pesquisar_contrato'},
                    {'opcao': '7', 'nome': 'Remover por ID', 'handler': 'remover'}
                ],
                'insert_fields': ['Nome', 'Telefone', 'Email', 'Salário', 'Cargo', 'Tipo de Contrato (CLT/PJ/Estágio)', 'ID do Perfil de Acesso'],
                'prompts': {
                    'pesquisar_nome': 'Digite o nome ou parte do nome do funcionário',
                    'pesquisar_contrato': 'Digite o tipo de contrato (CLT, PJ, Estágio)'
                }
            },
             'perfis_acesso': {
                'nome': 'Perfis de Acesso',
                'queries': {
                    'listar': cadastros_queries.LISTAR_TODOS_PERFIS_ACESSO,
                    'exibir_um': cadastros_queries.SELECIONAR_PERFIL_ACESSO_POR_ID,
                    'inserir': cadastros_queries.INSERIR_PERFIL_ACESSO,
                    'pesquisar_nome': cadastros_queries.PESQUISAR_PERFIL_ACESSO_POR_NOME,
                    'alterar_descricao': cadastros_queries.ATUALIZAR_DESCRICAO_PERFIL_ACESSO,
                    'remover': cadastros_queries.REMOVER_PERFIL_ACESSO,
                    'check_delete': cadastros_queries.VERIFICAR_FUNCIONARIOS_POR_PERFIL
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todos', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Exibir Um por ID (Interativo)', 'handler': 'exibir_um_perfil_interativo'},
                    {'opcao': '3', 'nome': 'Inserir Novo', 'handler': 'inserir'},
                    {'opcao': '4', 'nome': 'Alterar Descrição', 'handler': 'alterar', 'key': 'alterar_descricao'},
                    {'opcao': '5', 'nome': 'Pesquisar por Nome', 'handler': 'pesquisar', 'key': 'pesquisar_nome'},
                    {'opcao': '6', 'nome': 'Remover (com verificação)', 'handler': 'remover_seguro'}
                ],
                'insert_fields': ['Nome do Perfil', 'Descrição'],
                'prompts': {
                    'alterar_descricao': 'Digite a NOVA descrição para o perfil',
                    'pesquisar_nome': 'Digite o nome ou parte do nome do perfil'
                }
            }
        }
    },
    'clinico': {
        'nome': 'Clínico',
        'tabelas': {
            'consultas': {
                'nome': 'Consultas',
                'queries': { 
                    'listar': clinico_queries.LISTAR_TODAS_CONSULTAS,
                    'exibir_um': clinico_queries.SELECIONAR_CONSULTA_POR_ID,
                    'inserir': clinico_queries.INSERIR_CONSULTA,
                    'remover': clinico_queries.REMOVER_CONSULTA,
                    'alterar_status': clinico_queries.ATUALIZAR_CONSULTA,
                    'pesquisar_paciente': clinico_queries.PESQUISAR_CONSULTA_POR_NOME_PACIENTE
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todas', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Exibir Uma por ID', 'handler': 'exibir_um'},
                    {'opcao': '3', 'nome': 'Agendar Nova Consulta', 'handler': 'inserir_consulta_interativo'},
                    {'opcao': '4', 'nome': 'Atualizar Status/Diagnóstico', 'handler': 'alterar_consulta_status'},
                    {'opcao': '5', 'nome': 'Pesquisar por Nome do Paciente', 'handler': 'pesquisar', 'key': 'pesquisar_paciente'},
                    {'opcao': '6', 'nome': 'Remover/Cancelar Consulta', 'handler': 'remover_consulta_seguro'}
                ],
                'delete_warning': 'Ao remover esta consulta, as receitas associadas serão PERMANENTEMENTE apagadas.',
                'prompts': {
                    'pesquisar_paciente': 'Digite o nome do paciente'
                }
            },
            'receitas': {
                'nome': 'Receitas',
                'queries': { 
                    'listar': clinico_queries.LISTAR_TODAS_RECEITAS,
                    'pesquisar_paciente': clinico_queries.PESQUISAR_RECEITA_POR_PACIENTE
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todas', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Pesquisar por Nome do Paciente', 'handler': 'pesquisar', 'key': 'pesquisar_paciente'}
                ],
                'prompts': {
                    'pesquisar_paciente': 'Digite o nome do paciente'
                }
            }
        },
        'relatorios': {
            'detalhes_consultas': {
                'nome': 'Relatório Detalhado de Consultas',
                'query': clinico_queries.DETALHES_CONSULTAS
            }
        }
    },
    'financeiro': {
        'nome': 'Financeiro',
        'tabelas': {
            'pagamentos': {
                'nome': 'Pagamentos',
                'queries': { 
                    'listar': financeiro_queries.LISTAR_TODOS_PAGAMENTOS,
                    'exibir_um': financeiro_queries.SELECIONAR_PAGAMENTO_POR_ID,
                    'inserir': financeiro_queries.INSERIR_PAGAMENTO,
                    'alterar_status': financeiro_queries.ATUALIZAR_STATUS_PAGAMENTO,
                    'pesquisar_paciente': financeiro_queries.PESQUISAR_PAGAMENTO_POR_NOME_PACIENTE
                },
                'menu_ops': [
                    {'opcao': '1', 'nome': 'Listar Todos', 'handler': 'listar'},
                    {'opcao': '2', 'nome': 'Exibir Um por ID', 'handler': 'exibir_um'},
                    {'opcao': '3', 'nome': 'Lançar Novo Pagamento', 'handler': 'inserir_pagamento_interativo'},
                    {'opcao': '4', 'nome': "Marcar como 'Pago'", 'handler': 'marcar_como_pago'},
                    {'opcao': '5', 'nome': 'Pesquisar por Nome do Paciente', 'handler': 'pesquisar', 'key': 'pesquisar_paciente'}
                ],
                'prompts': {
                    'pesquisar_paciente': 'Digite o nome do paciente'
                }
            }
        }
    }
}



# --- Funções Auxiliares de Interface ---
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("\nPressione Enter para continuar...")

def formatar_resultados(resultados, cursor_description):
    if not resultados: return "Nenhum resultado encontrado."
    
    colunas = [desc[0] for desc in cursor_description]
    larguras = [len(col) for col in colunas]
    for linha in resultados:
        for i, item in enumerate(linha):
            larguras[i] = max(larguras[i], len(str(item)))
    
    cabecalho = " | ".join(f"{col.upper():<{larguras[i]}}" for i, col in enumerate(colunas))
    separador = "-+-".join("-" * w for w in larguras)
    
    linhas_dados = []
    for linha in resultados:
        linhas_dados.append(" | ".join(f"{str(item):<{larguras[i]}}" for i, item in enumerate(linha)))
        
    return "\n".join([cabecalho, separador] + linhas_dados)


# --- Funções Genéricas e Específicas de CRUD ---

def listar_registros(db, config, **kwargs):
    print(f"\n--- LISTANDO: {config['nome']} ---")
    query = config['queries'].get('listar')
    if not query:
        print("Operação não configurada.")
        return
    resultados, description = db.fetch_query(query)
    print(formatar_resultados(resultados, description))

def exibir_um_registro(db, config, **kwargs):
    print(f"\n--- EXIBINDO UM: {config['nome']} ---")
    prompt_text = kwargs.get('prompt', 'Digite o ID do registro')
    termo = input(f"{prompt_text}: ")
    query = config['queries']['exibir_um']
    resultados, description = db.fetch_query(query, (termo,))
    print(formatar_resultados(resultados, description))

def inserir_registro(db, config, **kwargs):
    print(f"\n--- INSERINDO: {config['nome']} ---")
    query = config['queries'].get('inserir')
    fields = config.get('insert_fields')
    if not query or not fields: return print("Operação não configurada.")
        
    valores = [input(f"{campo}: ") for campo in fields]
    resultado = db.execute_and_fetch_one(query, tuple(valores))
    if resultado: print(f"\nRegistro inserido com sucesso! ID: {resultado[0]}")
    else: print("\nFalha ao inserir registro.")

def alterar_registro(db, config, key):
    print(f"\n--- ALTERANDO: {config['nome']} ---")
    query = config['queries'][key]
    prompt = config['prompts'][key]
    
    try:
        registro_id = int(input(f"Digite o ID do(a) {config['nome']} que deseja alterar: "))
        novo_valor = input(f"{prompt}: ")
    except ValueError: return print("Erro: ID inválido.")

    if db.execute_query(query, (novo_valor, registro_id)):
        print(f"\nRegistro ID {registro_id} atualizado com sucesso!")
    else: print("\nFalha ao atualizar. Verifique se o ID existe.")

def pesquisar_registros(db, config, key):
    print(f"\n--- PESQUISANDO: {config['nome']} ---")
    query = config['queries'][key]
    prompt = config['prompts'][key]
    
    termo = input(f"{prompt}: ")
    parametro_busca = f"%{termo}%" if 'ILIKE' in query.upper() else termo
    
    resultados, description = db.fetch_query(query, (parametro_busca,))
    print(formatar_resultados(resultados, description))

def remover_registro(db, config, **kwargs):
    print(f"\n--- REMOVENDO: {config['nome']} ---")
    query = config['queries'].get('remover')
    if not query: return print("Operação não configurada.")
    
    try:
        registro_id = int(input(f"Digite o ID do(a) {config['nome']} que deseja remover: "))
    except ValueError: return print("Erro: ID inválido.")

    alerta = config.get('delete_warning')
    if alerta:
        print("\n" + "="*70)
        print(f"ATENÇÃO: {alerta}")
        print("="*70)

    if input(f"\nTem certeza que deseja remover o registro ID {registro_id}? (s/n): ").lower() != 's':
        return print("Operação cancelada.")

    if db.execute_query(query, (registro_id,)):
        print(f"\nRegistro ID {registro_id} removido com sucesso!")
    else:
        print("\nFalha ao remover. Verifique se o ID existe.")

# --- Funções Específicas de CRUD ---

def remover_seguro(db, config, **kwargs):
    print(f"\n--- REMOVENDO: {config['nome']} (com verificação) ---")
    try:
        registro_id = int(input(f"Digite o ID da {config['nome']} que deseja remover: "))
    except ValueError: return print("Erro: ID inválido.")
        
    check_query = config['queries']['check_delete']
    resultado, desc = db.fetch_query(check_query, (registro_id,))
    vinculados = resultado[0][0] if resultado else 0

    if vinculados > 0:
        print(f"\n[ERRO] Não é possível remover: {vinculados} registro(s) dependem deste.")
    else:
        remover_registro(db, config)

def alterar_status_especialidade(db, config, **kwargs):
    print(f"\n--- ALTERANDO STATUS: {config['nome']} ---")
    try:
        registro_id = int(input(f"Digite o ID da {config['nome']} que deseja alterar: "))
    except ValueError: 
        print("Erro: ID inválido.")
        return

    # Busca o status atual para inverter
    resultados, description = db.fetch_query(cadastros_queries.SELECIONAR_ESPECIALIDADE_POR_ID, (registro_id,))
    
    if not resultados: 
        print("Especialidade não encontrada.")
        return
    
    status_atual = resultados[0][2] 
    novo_status = not status_atual
    
    status_atual_texto = 'Ativa' if status_atual else 'Inativa'
    novo_status_texto = 'Ativa' if novo_status else 'Inativa'

    confirmacao = input(f"O status atual é '{status_atual_texto}'. Deseja alterar para '{novo_status_texto}'? (s/n): ").lower()
    if confirmacao != 's': 
        print("Operação cancelada.")
        return
    
    if db.execute_query(config['queries']['alterar_status'], (novo_status, registro_id)):
        print(f"\nStatus da especialidade ID {registro_id} alterado com sucesso!")
    else: 
        print("\nFalha ao alterar o status.")

def alterar_perfil_funcionario(db, config, **kwargs):
    """Handler especializado para alterar o perfil de um funcionário de forma interativa."""
    print(f"\n--- ALTERANDO PERFIL DE ACESSO DO FUNCIONÁRIO ---")
    
    try:
        funcionario_id = int(input(f"Digite o ID do Funcionário que deseja alterar: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    # Passo 1: Buscar dinamicamente os perfis de acesso disponíveis no banco
    print("\nBuscando perfis de acesso disponíveis...")
    perfis, desc = db.fetch_query(cadastros_queries.LISTAR_TODOS_PERFIS_ACESSO)

    if not perfis:
        print("Nenhum perfil de acesso encontrado no sistema.")
        return

    # Passo 2: Exibir a lista de perfis para o usuário
    print("Perfis de Acesso Disponíveis:")
    perfis_disponiveis = {}
    for perfil in perfis:
        perfil_id, nome, descricao = perfil
        perfis_disponiveis[str(perfil_id)] = nome
        print(f"  ID: {perfil_id} - {nome}")

    # Passo 3: Pedir ao usuário para escolher um da lista
    while True:
        novo_perfil_id_str = input("\nDigite o ID do NOVO perfil de acesso para este funcionário: ")
        if novo_perfil_id_str in perfis_disponiveis:
            break
        else:
            print("Erro: ID de perfil inválido. Por favor, escolha um da lista acima.")
    
    # Passo 4: Executar o UPDATE com o ID escolhido
    query = config['queries']['alterar_perfil']
    if db.execute_query(query, (int(novo_perfil_id_str), funcionario_id)):
        print(f"\nPerfil do funcionário ID {funcionario_id} alterado para '{perfis_disponiveis[novo_perfil_id_str]}' com sucesso!")
    else:
        print("\nFalha ao atualizar o perfil. Verifique se o ID do funcionário existe.")

def exibir_um_perfil_interativo(db, config, **kwargs):
    """Handler especializado para exibir um perfil de acesso, listando as opções primeiro."""
    print(f"\n--- EXIBINDO UM: {config['nome']} ---")
    
    # 1. Busca e exibe a lista de todos os perfis
    perfis, desc_lista = db.fetch_query(config['queries']['listar'])
    if not perfis:
        print("Nenhum perfil de acesso cadastrado para exibir.")
        return

    print("Perfis de Acesso Disponíveis:")
    perfis_disponiveis = {str(p[0]): p[1] for p in perfis} # Mapeia ID -> Nome
    for perfil_id, nome in perfis_disponiveis.items():
        print(f"  ID: {perfil_id} - {nome}")

    # 2. Pede ao usuário para escolher um ID da lista
    while True:
        escolha_id = input("\nDigite o ID do perfil que deseja ver em detalhes: ")
        if escolha_id in perfis_disponiveis:
            break
        else:
            print("Erro: ID inválido. Por favor, escolha um da lista acima.")

    # 3. Busca e exibe os detalhes completos do perfil escolhido
    query = config['queries']['exibir_um']
    resultados, description = db.fetch_query(query, (int(escolha_id),))
    
    print("\nDetalhes do Perfil de Acesso:")
    print(formatar_resultados(resultados, description))

def remover_consulta_seguro(db, config, **kwargs):
    print(f"\n--- REMOVENDO/CANCELANDO: {config['nome']} ---")
    try:
        registro_id = int(input(f"Digite o ID da {config['nome']} que deseja gerenciar: "))
    except ValueError: return print("Erro: ID inválido.")
        
    check_query = financeiro_queries.VERIFICAR_PAGAMENTO_POR_CONSULTA
    resultado, desc = db.fetch_query(check_query, (registro_id,))
    vinculados = resultado[0][0] if resultado else 0

    if vinculados > 0:
        print(f"\n[AVISO] Esta consulta possui {vinculados} pagamento(s) e não pode ser removida permanentemente.")
        confirmacao = input("Deseja alterar o status desta consulta para 'Cancelada'? (s/n): ").lower()
        if confirmacao == 's':
            query_update = config['queries']['alterar_status']
            if db.execute_query(query_update, ('Cancelada', 'Cancelado pelo sistema', registro_id)):
                print("\nConsulta cancelada com sucesso!")
            else:
                print("\nFalha ao cancelar a consulta.")
        else:
            print("Operação cancelada.")
    else:
        remover_registro(db, config)

def inserir_consulta_interativo(db, config, **kwargs):
    """Handler especializado para agendar uma nova consulta de forma interativa."""
    print(f"\n--- AGENDANDO NOVA CONSULTA ---")
    
    # 1. Lista e seleciona o paciente 
    listar_registros(db, MENU_CONFIG['cadastros']['tabelas']['pacientes'])
    try:
        paciente_id = int(input("\nDigite o ID do Paciente para a consulta: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    # 2. Lista os médicos 
    print("\n--- Selecione o Médico ---")
    resultados_medicos, description_medicos = db.fetch_query(cadastros_queries.LISTAR_MEDICOS_COM_ESPECIALIDADE)
    print(formatar_resultados(resultados_medicos, description_medicos))
    
    try:
        medico_id = int(input("\nDigite o ID do Médico para a consulta: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    # 3. Pede os dados restantes
    data = input("Data e Hora da consulta (YYYY-MM-DD HH:MM): ")
    motivo = input("Motivo da consulta: ")
    status = "Agendada"

    nova_consulta = (paciente_id, medico_id, data, motivo, status)
    resultado = db.execute_and_fetch_one(config['queries']['inserir'], nova_consulta)
    
    if resultado:
        print(f"\nConsulta agendada com sucesso! ID: {resultado[0]}")
    else:
        print("\nFalha ao agendar consulta.")

def alterar_consulta_status(db, config, **kwargs):
    """Handler especializado para alterar o status e diagnóstico de uma consulta."""
    print(f"\n--- ATUALIZANDO CONSULTA ---")
    try:
        consulta_id = int(input("Digite o ID da consulta que deseja alterar: "))
    except ValueError: return print("Erro: ID inválido.")
    
    print("\nStatus disponíveis: Agendada, Realizada, Cancelada")
    novo_status = input("Digite o NOVO status da consulta: ")
    diagnostico = input("Digite o diagnóstico (ou deixe em branco): ")

    if db.execute_query(config['queries']['alterar_status'], (novo_status, diagnostico, consulta_id)):
        print(f"\nConsulta ID {consulta_id} atualizada com sucesso!")
    else:
        print("\nFalha ao atualizar. Verifique se o ID da consulta existe.")

def inserir_pagamento_interativo(db, config, **kwargs):
    """Handler especializado para lançar um novo pagamento de forma interativa."""
    print(f"\n--- LANÇANDO NOVO PAGAMENTO ---")
    
    print("\nConsultas disponíveis para vincular o pagamento:")
    listar_registros(db, MENU_CONFIG['clinico']['tabelas']['consultas'])
    try:
        consulta_id = int(input("\nDigite o ID da Consulta para este pagamento: "))
    except ValueError:
        print("Erro: ID inválido.")
        return

    valor = input("Valor do pagamento (ex: 350.00): ")
    metodo = input("Método de pagamento (Dinheiro, Cartão, Transferência, Seguro): ")
    pago = input("O pagamento já foi efetuado? (s/n): ").lower() == 's'
    data_pagamento = 'NOW()' if pago else None # Usa a data/hora atual se foi pago

    novo_pagamento = (consulta_id, float(valor), metodo, pago, data_pagamento)
    resultado = db.execute_and_fetch_one(config['queries']['inserir'], novo_pagamento)
    
    if resultado:
        print(f"\nPagamento lançado com sucesso! ID: {resultado[0]}")
    else:
        print("\nFalha ao lançar pagamento.")


def marcar_como_pago(db, config, **kwargs):
    """Handler especializado para marcar um pagamento como 'pago'."""
    print(f"\n--- ATUALIZANDO STATUS DE PAGAMENTO ---")
    
    print("\nPagamentos com status 'Não Pago':")
    query_pendentes = "SELECT id, consulta_id, valor, metodo FROM financeiro.pagamentos WHERE pago = FALSE ORDER BY id;"
    pendentes, desc = db.fetch_query(query_pendentes)
    print(formatar_resultados(pendentes, desc))
    
    try:
        pagamento_id = int(input("\nDigite o ID do pagamento que deseja marcar como 'PAGO': "))
    except ValueError:
        print("Erro: ID inválido.")
        return
    
    if db.execute_query(config['queries']['alterar_status'], (pagamento_id,)):
        print(f"\nPagamento ID {pagamento_id} marcado como PAGO com sucesso!")
    else:
        print("\nFalha ao atualizar o pagamento. Verifique se o ID existe.")


# Mapeamento de strings de 'handler' para as funções reais
CRUD_HANDLERS = {
    'listar': listar_registros,
    'exibir_um': exibir_um_registro,
    'inserir': inserir_registro,
    'alterar': alterar_registro,
    'pesquisar': pesquisar_registros,
    'remover': remover_registro,
    'remover_seguro': remover_seguro,
    'alterar_status_especialidade': alterar_status_especialidade,
    'alterar_perfil_funcionario': alterar_perfil_funcionario,
    'exibir_um_perfil_interativo': exibir_um_perfil_interativo,
    'remover_consulta_seguro': remover_consulta_seguro,
    'inserir_consulta_interativo': inserir_consulta_interativo,
    'alterar_consulta_status': alterar_consulta_status,
    'inserir_pagamento_interativo': inserir_pagamento_interativo, 
    'marcar_como_pago': marcar_como_pago,
}

# --- Funções de Navegação nos Menus ---
def menu_crud(db, schema_key, table_key):
    config_tabela = MENU_CONFIG[schema_key]['tabelas'][table_key]
    while True:
        limpar_tela()
        print(f"=== Gerenciando: {config_tabela['nome']} ===")
        
        # Gera o menu dinamicamente a partir da configuração
        opcoes_menu = {op['opcao']: op for op in config_tabela.get('menu_ops', [])}
        for opcao, config_op in opcoes_menu.items():
            print(f"  {opcao} - {config_op['nome']}")

        print("\n  0 - Voltar")
        escolha = input("\n> ")
        limpar_tela()

        if escolha == '0': break
        
        if escolha in opcoes_menu:
            op_selecionada = opcoes_menu[escolha]
            handler_func = CRUD_HANDLERS.get(op_selecionada['handler'])
            if handler_func:
                # Prepara os argumentos para a função handler
                handler_args = {'db': db, 'config': config_tabela, 'key': op_selecionada.get('key')}
                # Adiciona o prompt customizado se houver
                if 'prompt' in op_selecionada:
                    handler_args['prompt'] = op_selecionada['prompt']
                
                handler_func(**{k: v for k, v in handler_args.items() if v is not None})
            else:
                print(f"Handler '{op_selecionada['handler']}' não implementado.")
        else:
            print("Opção inválida!")
        pausar()


def menu_tabelas(db, schema_key):
    config_schema = MENU_CONFIG[schema_key]
    while True:
        limpar_tela()
        print(f"=== Schema: {config_schema['nome']} ===")
        # Menu de Tabelas
        tabelas = config_schema.get('tabelas', {})
        opcoes_tabela = list(tabelas.keys())
        for i, key in enumerate(opcoes_tabela):
            print(f"  {i+1} - Gerenciar {tabelas[key]['nome']}")
        
        # Menu de Relatórios
        relatorios = config_schema.get('relatorios', {})
        opcoes_relatorio = list(relatorios.keys())
        if relatorios:
            print("\n--- Relatórios ---")
            for i, key in enumerate(opcoes_relatorio):
                print(f"  R{i+1} - {relatorios[key]['nome']}")

        print("\n  0 - Voltar")
        escolha = input("\n> ")

        if escolha.upper().startswith('R'):
            try:
                idx = int(escolha[1:]) - 1
                if 0 <= idx < len(opcoes_relatorio):
                    key = opcoes_relatorio[idx]
                    listar_registros(db, relatorios[key]) # Reutiliza a função de listar
                    pausar()
            except (ValueError, IndexError):
                print("Opção de relatório inválida!"); pausar()
        else:
            try:
                idx = int(escolha) - 1
                if idx == -1: break
                if 0 <= idx < len(opcoes_tabela):
                    key = opcoes_tabela[idx]
                    menu_crud(db, schema_key, key)
                else: print("Opção inválida!"); pausar()
            except ValueError: print("Opção inválida!"); pausar()


def menu_principal(db):
    while True:
        limpar_tela()
        print("=========================================")
        print("===   Sistema de Gestão da Clínica    ===")
        print("=========================================")
        opcoes = list(MENU_CONFIG.keys())
        for i, key in enumerate(opcoes):
            print(f"  {i+1} - {MENU_CONFIG[key]['nome']}")
        print("\n  0 - Sair")
        escolha = input("\n> ")
        try:
            idx = int(escolha) - 1
            if idx == -1: break
            if 0 <= idx < len(opcoes):
                key_schema_selecionado = opcoes[idx]
                menu_tabelas(db, key_schema_selecionado)
            else: print("Opção inválida!"); pausar()
        except ValueError: print("Opção inválida!"); pausar()
    print("Saindo do sistema...")

if __name__ == "__main__":
    db = DatabaseManager()
    db.connect()
    if db.conn:
        menu_principal(db)
        db.disconnect()