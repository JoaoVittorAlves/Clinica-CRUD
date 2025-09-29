import streamlit as st
import pandas as pd
from db_manager import DatabaseManager
# Importa todos os arquivos de queries existentes
from queries import cadastros_queries, clinico_queries, financeiro_queries
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
# Define o título da aba do navegador e o layout da página
st.set_page_config(page_title="Gestão da Clínica", layout="wide")


# --- FUNÇÕES AUXILIARES E CONEXÃO COM O BANCO ---

@st.cache_resource
def get_db_manager():
    """
    Cria e gerencia uma única instância da classe de conexão com o banco.
    O decorator @st.cache_resource garante que a conexão seja feita apenas uma vez.
    """
    db = DatabaseManager()
    db.connect()
    return db

db_manager = get_db_manager()

def safe_remover(id_remocao, remover_query, check_query, tipo_registro):
    """
    Função genérica para remoção segura, verificando dependências antes de apagar.
    """
    dependentes, _ = db_manager.fetch_query(check_query, (id_remocao,))
    if dependentes and dependentes[0][0] > 0:
        st.error(f"Não é possível remover este(a) {tipo_registro}. Existem {dependentes[0][0]} registros que dependem dele(a).")
        return
    
    if db_manager.execute_query(remover_query, (id_remocao,)):
        st.success(f"{tipo_registro.capitalize()} ID {id_remocao} removido com sucesso!")
        st.experimental_rerun()
    else:
        st.error(f"Falha ao remover o(a) {tipo_registro}.")

def carregar_dados_para_selectbox(query, id_col_index=0, nome_col_index=1):
    """
    Carrega dados de uma query para popular um selectbox de forma amigável.
    Retorna um dicionário (ID -> Nome) e uma lista de opções formatadas ("ID - Nome").
    """
    dados, _ = db_manager.fetch_query(query)
    if not dados:
        return {}, ["Nenhum item encontrado"]
    
    mapeamento = {item[id_col_index]: item[nome_col_index] for item in dados}
    opcoes = [f"{id} - {nome}" for id, nome in mapeamento.items()]
    return mapeamento, opcoes


# --- PÁGINA DE CADASTROS ---
def pagina_cadastros():
    st.header("Módulo de Cadastros")
    
    # Abas para cada tipo de cadastro, melhorando a organização da UI
    tab_pacientes, tab_medicos, tab_funcionarios, tab_especialidades, tab_perfis = st.tabs([
        "Pacientes", "Médicos", "Funcionários", "Especialidades", "Perfis de Acesso"
    ])

    # --- ABA DE PACIENTES ---
    with tab_pacientes:
        st.subheader("Gerenciamento de Pacientes")
        
        with st.expander("➕ Cadastrar Novo Paciente"):
            with st.form("novo_paciente_form", clear_on_submit=True):
                # O formulário é dividido em colunas para melhor layout
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome Completo*")
                    sexo = st.selectbox("Sexo", ["M", "F", "O"])
                    email = st.text_input("Email")
                    cpf = st.text_input("CPF (somente números)")
                    telefone = st.text_input("Telefone")
                with col2:
                    logradouro = st.text_input("Logradouro")
                    numero = st.text_input("Número")
                    complemento = st.text_input("Complemento")
                    bairro = st.text_input("Bairro")
                    cidade = st.text_input("Cidade")
                    sigla_estado = st.text_input("UF", max_chars=2)
                    cep = st.text_input("CEP")

                if st.form_submit_button("Salvar Paciente"):
                    if not nome:
                        st.warning("O campo 'Nome' é obrigatório.")
                    else:
                        dados = (nome, sexo, email, cpf, telefone, logradouro, numero, complemento, bairro, cidade, sigla_estado, cep)
                        resultado = db_manager.execute_and_fetch_one(cadastros_queries.INSERIR_PACIENTE, dados)
                        if resultado:
                            st.success(f"Paciente '{nome}' cadastrado com o ID {resultado[0]}")
                        else:
                            st.error("Erro ao cadastrar paciente. Verifique se o email ou CPF já existem.")

        st.subheader("Pacientes Cadastrados")
        pesquisa_paciente = st.text_input("Pesquisar paciente por nome:", key="search_pac")
        
        if pesquisa_paciente:
            pacientes, desc = db_manager.fetch_query(cadastros_queries.PESQUISAR_PACIENTE_POR_NOME, (f"%{pesquisa_paciente}%",))
        else:
            pacientes, desc = db_manager.fetch_query(cadastros_queries.LISTAR_TODOS_PACIENTES)

        if pacientes:
            df_pacientes = pd.DataFrame(pacientes, columns=[d[0] for d in desc])
            st.dataframe(df_pacientes, use_container_width=True)

            st.markdown("---")
            col_alt, col_rem = st.columns(2)
            with col_alt:
                st.subheader("Alterar Telefone")
                id_alt_pac = st.number_input("ID do Paciente", min_value=1, step=1, key="id_alt_pac")
                novo_tel = st.text_input("Novo Telefone", key="tel_pac")
                if st.button("Alterar Telefone"):
                    if db_manager.execute_query(cadastros_queries.ATUALIZAR_TELEFONE_PACIENTE, (novo_tel, id_alt_pac)):
                        st.success(f"Telefone do paciente ID {id_alt_pac} alterado!")
                        st.experimental_rerun()
                    else:
                        st.error("Falha ao alterar. Verifique se o ID do paciente existe.")
            with col_rem:
                st.subheader("Remover Paciente")
                id_rem_pac = st.number_input("ID do Paciente", min_value=1, step=1, key="id_rem_pac")
                if st.button("Remover Paciente", type="primary"):
                    st.warning("A remoção de um paciente apagará todas as suas consultas e pagamentos associados. Esta ação não pode ser desfeita.")
                    # A remoção direta é perigosa devido às restrições ON DELETE CASCADE.
                    # É melhor desativar um paciente do que removê-lo em um sistema real.
                    if db_manager.execute_query(cadastros_queries.REMOVER_PACIENTE, (id_rem_pac,)):
                        st.success(f"Paciente ID {id_rem_pac} removido.")
                        st.experimental_rerun()
                    else:
                        st.error("Falha ao remover.")
        else:
            st.info("Nenhum paciente encontrado.")

    # --- ABA DE MÉDICOS ---
    with tab_medicos:
        st.subheader("Gerenciamento de Médicos")

        _, especialidades_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_TODAS_ESPECIALIDADES)

        with st.expander("➕ Cadastrar Novo Médico"):
            with st.form("novo_medico_form", clear_on_submit=True):
                nome = st.text_input("Nome Completo do Médico*")
                email = st.text_input("Email do Médico")
                crm = st.text_input("CRM*")
                telefone = st.text_input("Telefone do Médico")
                salario = st.number_input("Salário", min_value=0.0, format="%.2f")
                
                especialidade_selecionada = st.selectbox("Especialidade*", especialidades_opts)

                if st.form_submit_button("Salvar Médico"):
                    if not nome or not crm or especialidade_selecionada == "Nenhum item encontrado":
                        st.warning("Campos com * são obrigatórios.")
                    else:
                        especialidade_id = int(especialidade_selecionada.split(" - ")[0])
                        dados = (nome, telefone, email, crm, salario, especialidade_id, None, None, None, None, None, None, None)
                        resultado = db_manager.execute_and_fetch_one(cadastros_queries.INSERIR_MEDICO, dados)
                        if resultado:
                            st.success(f"Médico '{nome}' cadastrado com ID {resultado[0]}.")
                        else:
                            st.error("Erro ao cadastrar médico. Verifique se CRM, email ou telefone já existem.")
        
        st.subheader("Médicos Cadastrados")
        medicos, desc = db_manager.fetch_query(cadastros_queries.LISTAR_MEDICOS_COM_ESPECIALIDADE)
        if medicos:
            df_medicos = pd.DataFrame(medicos, columns=[d[0] for d in desc])
            st.dataframe(df_medicos, use_container_width=True)

    # --- ABA DE FUNCIONÁRIOS ---
    with tab_funcionarios:
        st.subheader("Gerenciamento de Funcionários")

        _, perfis_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_TODOS_PERFIS_ACESSO)

        with st.expander("➕ Cadastrar Novo Funcionário"):
            with st.form("novo_funcionario_form", clear_on_submit=True):
                nome_func = st.text_input("Nome Completo*")
                email_func = st.text_input("Email")
                telefone_func = st.text_input("Telefone")
                salario_func = st.number_input("Salário", min_value=0.0, format="%.2f")
                cargo = st.text_input("Cargo*")
                tipo_contrato = st.selectbox("Tipo de Contrato", ["CLT", "PJ", "Estágio"])
                perfil_selecionado = st.selectbox("Perfil de Acesso*", perfis_opts)

                if st.form_submit_button("Salvar Funcionário"):
                    if not nome_func or not cargo or "Nenhum" in perfil_selecionado:
                        st.warning("Campos com * são obrigatórios.")
                    else:
                        perfil_id = int(perfil_selecionado.split(" - ")[0])
                        dados = (nome_func, telefone_func, email_func, salario_func, cargo, tipo_contrato, perfil_id)
                        res = db_manager.execute_and_fetch_one(cadastros_queries.INSERIR_FUNCIONARIO, dados)
                        if res:
                            st.success(f"Funcionário '{nome_func}' salvo com ID {res[0]}.")
                        else:
                            st.error("Erro ao salvar funcionário.")
        
        st.subheader("Funcionários Cadastrados")
        funcionarios, desc = db_manager.fetch_query(cadastros_queries.LISTAR_TODOS_FUNCIONARIOS)
        if funcionarios:
            df_func = pd.DataFrame(funcionarios, columns=[d[0] for d in desc])
            st.dataframe(df_func, use_container_width=True)

    # --- ABA DE ESPECIALIDADES ---
    with tab_especialidades:
        st.subheader("Gerenciamento de Especialidades")
        
        with st.expander("➕ Cadastrar Nova Especialidade"):
            with st.form("nova_especialidade_form", clear_on_submit=True):
                nome_espec = st.text_input("Nome da Especialidade")
                ativa = st.checkbox("Ativa", value=True)
                if st.form_submit_button("Salvar Especialidade"):
                    res = db_manager.execute_and_fetch_one(cadastros_queries.INSERIR_ESPECIALIDADE, (nome_espec, ativa))
                    st.success(f"Especialidade '{nome_espec}' salva com ID {res[0]}.")

        st.subheader("Especialidades Cadastradas")
        especialidades, desc = db_manager.fetch_query(cadastros_queries.LISTAR_TODAS_ESPECIALIDADES)
        if especialidades:
            df_espec = pd.DataFrame(especialidades, columns=[d[0] for d in desc])
            st.dataframe(df_espec, use_container_width=True)

            id_rem_esp = st.number_input("ID da Especialidade para remover", min_value=1, step=1, key="id_rem_esp")
            if st.button("Remover Especialidade", type="primary"):
                safe_remover(id_rem_esp, 
                             cadastros_queries.REMOVER_ESPECIALIDADE,
                             cadastros_queries.VERIFICAR_MEDICOS_POR_ESPECIALIDADE,
                             "especialidade")

    # --- ABA DE PERFIS DE ACESSO ---
    with tab_perfis:
        st.subheader("Gerenciamento de Perfis de Acesso")

        with st.expander("➕ Cadastrar Novo Perfil de Acesso"):
            with st.form("novo_perfil_form", clear_on_submit=True):
                nome_perfil = st.text_input("Nome do Perfil*")
                descricao_perfil = st.text_area("Descrição")
                if st.form_submit_button("Salvar Perfil"):
                    if not nome_perfil:
                        st.warning("O nome do perfil é obrigatório.")
                    else:
                        res = db_manager.execute_and_fetch_one(cadastros_queries.INSERIR_PERFIL_ACESSO, (nome_perfil, descricao_perfil))
                        st.success(f"Perfil '{nome_perfil}' salvo com ID {res[0]}.")

        st.subheader("Perfis Cadastrados")
        perfis, desc = db_manager.fetch_query(cadastros_queries.LISTAR_TODOS_PERFIS_ACESSO)
        if perfis:
            df_perfis = pd.DataFrame(perfis, columns=[d[0] for d in desc])
            st.dataframe(df_perfis, use_container_width=True)

            id_rem_perfil = st.number_input("ID do Perfil para remover", min_value=1, step=1, key="id_rem_perfil")
            if st.button("Remover Perfil", type="primary"):
                safe_remover(id_rem_perfil,
                             cadastros_queries.REMOVER_PERFIL_ACESSO,
                             cadastros_queries.VERIFICAR_FUNCIONARIOS_POR_PERFIL,
                             "perfil de acesso")


# --- PÁGINA CLÍNICA ---
def pagina_clinico():
    st.header("Módulo Clínico")

    tab_consultas, tab_receitas = st.tabs(["Consultas", "Receitas"])

    with tab_consultas:
        st.subheader("Gerenciamento de Consultas")
        
        # Carrega dados para os formulários
        _, medicos_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_MEDICOS_COM_ESPECIALIDADE)
        _, pacientes_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_TODOS_PACIENTES)
        
        with st.expander("🗓️ Agendar Nova Consulta"):
            with st.form("nova_consulta_form", clear_on_submit=True):
                paciente_selecionado = st.selectbox("Paciente*", pacientes_opts)
                medico_selecionado = st.selectbox("Médico*", medicos_opts)
                # CORREÇÃO AQUI: Substituído st.datetime_input por st.date_input e st.time_input
                data_consulta = st.date_input("Data da Consulta")
                hora_consulta = st.time_input("Hora da Consulta")
                motivo = st.text_area("Motivo da Consulta")
                
                # CORREÇÃO AQUI: Botão de submit dentro do formulário para corrigir o erro "Missing Submit Button"
                if st.form_submit_button("Agendar Consulta"):
                    if "Nenhum" in paciente_selecionado or "Nenhum" in medico_selecionado:
                        st.warning("É necessário selecionar um paciente e um médico.")
                    else:
                        paciente_id = int(paciente_selecionado.split(" - ")[0])
                        medico_id = int(medico_selecionado.split(" - ")[0])
                        # CORREÇÃO AQUI: Combina a data e a hora em um único objeto datetime
                        data_hora_completa = datetime.combine(data_consulta, hora_consulta)
                        dados = (paciente_id, medico_id, data_hora_completa, motivo, 'Agendada')
                        res = db_manager.execute_and_fetch_one(clinico_queries.INSERIR_CONSULTA, dados)
                        if res: 
                            st.success(f"Consulta agendada com ID {res[0]}")
                        else: 
                            st.error("Falha ao agendar consulta.")

        st.subheader("Consultas Agendadas")
        consultas, desc = db_manager.fetch_query(clinico_queries.DETALHES_CONSULTAS)
        if consultas:
            df_consultas = pd.DataFrame(consultas, columns=[d[0] for d in desc])
            st.dataframe(df_consultas, use_container_width=True)

            st.markdown("---")
            st.subheader("Atualizar Status de uma Consulta")
            id_consulta_alt = st.number_input("ID da Consulta", min_value=1, step=1, key="id_consulta_alt")
            novo_status = st.selectbox("Novo Status", ["Agendada", "Realizada", "Cancelada"])
            diagnostico = st.text_area("Diagnóstico/Observações", key="diag")
            if st.button("Atualizar Consulta"):
                if db_manager.execute_query(clinico_queries.ATUALIZAR_CONSULTA, (novo_status, diagnostico, id_consulta_alt)):
                    st.success("Consulta atualizada!")
                    st.experimental_rerun()
                else:
                    st.error("Falha ao atualizar. Verifique o ID da consulta.")

    with tab_receitas:
        st.subheader("Visualização de Receitas")
        receitas, desc = db_manager.fetch_query(clinico_queries.LISTAR_TODAS_RECEITAS)
        if receitas:
            df_receitas = pd.DataFrame(receitas, columns=[d[0] for d in desc])
            st.dataframe(df_receitas, use_container_width=True)


# --- PÁGINA FINANCEIRA ---
def pagina_financeiro():
    st.header("Módulo Financeiro")

    st.subheader("Gerenciamento de Pagamentos")
    
    # Carrega dados para o formulário de lançamento
    _, consultas_opts = carregar_dados_para_selectbox(clinico_queries.LISTAR_TODAS_CONSULTAS, 0, 1)

    with st.expander("💸 Lançar Novo Pagamento"):
        with st.form("novo_pagamento_form", clear_on_submit=True):
            consulta_selecionada = st.selectbox("Vincular à Consulta*", consultas_opts)
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            metodo = st.selectbox("Método de Pagamento", ["Dinheiro", "Cartão", "Transferência", "Seguro"])
            pago = st.checkbox("Pagamento já recebido?")
            
            if st.form_submit_button("Lançar Pagamento"):
                if "Nenhum" in consulta_selecionada:
                    st.warning("É necessário selecionar uma consulta.")
                else:
                    consulta_id = int(consulta_selecionada.split(" - ")[0])
                    data_pagamento = 'NOW()' if pago else None
                    dados = (consulta_id, valor, metodo, pago, data_pagamento)
                    res = db_manager.execute_and_fetch_one(financeiro_queries.INSERIR_PAGAMENTO, dados)
                    if res: st.success(f"Pagamento lançado com ID {res[0]}")
                    else: st.error("Falha ao lançar pagamento.")

    st.subheader("Todos os Pagamentos")
    pagamentos, desc = db_manager.fetch_query(financeiro_queries.LISTAR_TODOS_PAGAMENTOS)
    if pagamentos:
        df_pag = pd.DataFrame(pagamentos, columns=[d[0] for d in desc])
        st.dataframe(df_pag, use_container_width=True)

        st.markdown("---")
        st.subheader("Marcar Pagamento como 'Recebido'")
        # Filtra apenas pagamentos não pagos para a seleção
        pag_pendentes, _ = db_manager.fetch_query("SELECT id, consulta_id, valor FROM financeiro.pagamentos WHERE pago = FALSE;")
        if pag_pendentes:
            _, pag_pendentes_opts = carregar_dados_para_selectbox("SELECT id, valor FROM financeiro.pagamentos WHERE pago = FALSE;")
            pag_a_quitar = st.selectbox("Selecione o Pagamento Pendente", pag_pendentes_opts)
            if st.button("Confirmar Recebimento"):
                pag_id = int(pag_a_quitar.split(" - ")[0])
                if db_manager.execute_query(financeiro_queries.ATUALIZAR_STATUS_PAGAMENTO, (pag_id,)):
                    st.success("Pagamento confirmado!")
                    st.experimental_rerun()
                else:
                    st.error("Falha ao confirmar pagamento.")
        else:
            st.info("Não há pagamentos pendentes.")

# --- NAVEGAÇÃO PRINCIPAL (SIDEBAR) ---
def main():
    # Adiciona um logo e título à barra lateral
    # CORREÇÃO AQUI: Parâmetro antigo 'use_column_width' trocado pelo novo 'use_container_width'
    st.sidebar.image("image_0b8972.jpg", use_container_width=True)
    
    # Define as páginas da aplicação
    paginas = {
        "Cadastros": pagina_cadastros,
        "Clínico": pagina_clinico,
        "Financeiro": pagina_financeiro,
    }
    
    st.sidebar.divider()
    
    # Cria o menu de rádio para navegação
    selecao = st.sidebar.radio("Navegue pelos Módulos", list(paginas.keys()))
    
    st.sidebar.divider()
    st.sidebar.info("Projeto de Banco de Dados I\n\nDesenvolvido com Python, Streamlit e PostgreSQL.")
    
    # Chama a função da página que foi selecionada no menu
    pagina_selecionada_func = paginas[selecao]
    pagina_selecionada_func()

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    if db_manager.conn:
        main()
    else:
        # Mensagem de erro amigável se a conexão com o banco falhar
        st.error("🔴 Falha na conexão com o banco de dados!")
        st.info("Por favor, verifique as seguintes opções:")
        st.markdown("""
        - O serviço do PostgreSQL está ativo na sua máquina?
        - As credenciais no arquivo `db_config.py` (usuário, senha, nome do banco) estão corretas?
        """)

