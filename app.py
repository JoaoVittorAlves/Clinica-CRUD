import streamlit as st
import pandas as pd
from db_manager import DatabaseManager
from queries import cadastros_queries, clinico_queries, financeiro_queries, vendas_queries
from datetime import datetime
import json
import altair as alt

st.set_page_config(page_title="Gestão da Clínica", layout="wide")

if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = {'type': None, 'id': None}
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- FUNÇÕES AUXILIARES E CONEXÃO COM O BANCO ---

@st.cache_resource
def get_db_manager():
    """
    Cria e gere uma única instância da classe de conexão com o banco.
    O decorador @st.cache_resource garante que a conexão seja feita apenas uma vez.
    """
    db = DatabaseManager()
    db.connect()
    return db

db_manager = get_db_manager()

def safe_remover(id_remocao, remover_query, check_query, tipo_registo):
    """
    Função para remoção segura, verificando dependências antes de apagar.
    """
    # Para médicos e funcionários, a verificação de dependência é se eles têm consultas agendadas
    if tipo_registo == "médico":
        check_query = "SELECT COUNT(*) FROM clinico.consultas WHERE medico_id = %s;"
    elif tipo_registo == "funcionário":
        check_query = "SELECT COUNT(*) FROM clinico.consultas WHERE funcionario_id = %s;"
    
    dependentes, _ = db_manager.fetch_query(check_query, (id_remocao,))
    
    if dependentes and dependentes[0][0] > 0:
        st.error(f"Não é possível remover. Existem {dependentes[0][0]} registos que dependem dele(a).")
        return False
    if db_manager.execute_query(remover_query, (id_remocao,)):
        st.success(f"{tipo_registo.capitalize()} ID {id_remocao} removido com sucesso!")
        return True
    else:
        st.error(f"Falha ao remover o(a) {tipo_registo}.")
        return False

def carregar_dados_para_selectbox(query, id_col_index=0, nome_col_index=1):
    dados, _ = db_manager.fetch_query(query)
    if not dados:
        return {}, ["Nenhum item encontrado"]
    
    mapeamento = {item[id_col_index]: item[nome_col_index] for item in dados}
    opcoes = [f"{id} - {nome}" for id, nome in mapeamento.items()]
    return mapeamento, opcoes

# --- PÁGINA DE CADASTROS ---
def pagina_cadastros():
    st.header("Módulo de Cadastros")
    
    tab_pacientes, tab_medicos, tab_funcionarios, tab_especialidades, tab_perfis = st.tabs([
        "Pacientes", "Médicos", "Funcionários", "Especialidades", "Perfis de Acesso"
    ])

    # --- SEPARADOR DE PACIENTES ---
    with tab_pacientes:
        st.subheader("Gerenciamento de Pacientes")
        
        with st.expander("➕ Cadastrar Novo Paciente"):
            with st.form("novo_paciente_form", clear_on_submit=True):
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

                st.markdown("---")
                st.write("**Critérios para Desconto:**")
                torce_flamengo = st.checkbox("Torce para o Flamengo")
                assiste_one_piece = st.checkbox("Assiste One Piece")
                nasceu_sousa = st.checkbox("Nasceu em Sousa-PB")

                if st.form_submit_button("Salvar Paciente"):
                    if not nome:
                        st.warning("O campo 'Nome' é obrigatório.")
                    else:
                        # A query INSERIR_PACIENTE já está correta em cadastros_queries.py
                        dados = (nome, sexo, email, cpf, telefone, logradouro, numero, complemento, bairro, cidade, sigla_estado, cep, torce_flamengo, assiste_one_piece, nasceu_sousa)
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
            col_alt, col_rem, col_desc = st.columns(3)
            with col_alt:
                st.subheader("Alterar Telefone")
                id_alt_pac = st.number_input("ID do Paciente", min_value=1, step=1, key="id_alt_pac")
                novo_tel = st.text_input("Novo Telefone", key="tel_pac")
                if st.button("Alterar Telefone"):
                    if db_manager.execute_query(cadastros_queries.ATUALIZAR_TELEFONE_PACIENTE, (novo_tel, id_alt_pac)):
                        st.success(f"Telefone do paciente ID {id_alt_pac} alterado!")
                        st.rerun()
                    else:
                        st.error("Falha ao alterar. Verifique se o ID do paciente existe.")
            with col_rem:
                st.subheader("Remover Paciente")
                id_rem_pac = st.number_input("ID do Paciente", min_value=1, step=1, key="id_rem_pac")
                if st.button("Remover Paciente", type="primary"):
                    st.session_state.confirm_delete = {'type': 'paciente', 'id': id_rem_pac}

                if st.session_state.confirm_delete['type'] == 'paciente':
                    st.warning(f"Tem a certeza de que quer apagar o paciente com ID {st.session_state.confirm_delete['id']}? Esta ação não pode ser desfeita e apagará todos os registos associados (consultas, pagamentos).")
                    confirm_col, cancel_col = st.columns(2)
                    with confirm_col:
                        if st.button("Sim, apagar permanentemente"):
                            paciente_id = st.session_state.confirm_delete['id']
                            if db_manager.execute_query(cadastros_queries.REMOVER_PACIENTE, (paciente_id,)):
                                st.success(f"Paciente ID {paciente_id} removido com sucesso.")
                                st.session_state.confirm_delete = {'type': None, 'id': None}
                                st.rerun()
                            else:
                                st.error("Falha ao remover o paciente.")
                    with cancel_col:
                        if st.button("Cancelar"):
                            st.session_state.confirm_delete = {'type': None, 'id': None}
                            st.rerun()
            with col_desc:
                st.subheader("Alterar Critérios de Desconto")
                _, pacientes_opts_desc = carregar_dados_para_selectbox(cadastros_queries.LISTAR_TODOS_PACIENTES)
                
                # Usamos uma chave única para este selectbox para não conflitar com outros
                paciente_sel_desc = st.selectbox("Selecione o Paciente", pacientes_opts_desc, key="sel_pac_desc")

                if "Nenhum" not in paciente_sel_desc:
                    pac_id_desc = int(paciente_sel_desc.split(" - ")[0])
                    # Busca os dados atuais do paciente
                    dados_pac_desc, _ = db_manager.fetch_query("SELECT torce_flamengo, assiste_one_piece, nasceu_sousa FROM cadastros.pacientes WHERE id=%s", (pac_id_desc,))

                    if dados_pac_desc:
                        torce_flamengo_atual = st.checkbox("Torce para o Flamengo", value=dados_pac_desc[0][0], key="flamengo_edit")
                        assiste_one_piece_atual = st.checkbox("Assiste One Piece", value=dados_pac_desc[0][1], key="op_edit")
                        nasceu_sousa_atual = st.checkbox("Nasceu em Sousa-PB", value=dados_pac_desc[0][2], key="sousa_edit")
                        
                        if st.button("Salvar Critérios de Desconto"):
                            dados_update = (torce_flamengo_atual, assiste_one_piece_atual, nasceu_sousa_atual, pac_id_desc)
                            if db_manager.execute_query(cadastros_queries.ATUALIZAR_CRITERIOS_DESCONTO_PACIENTE, dados_update):
                                st.success("Critérios de desconto atualizados com sucesso!")
                                st.rerun()
        else:
            st.info("Nenhum paciente encontrado.")

    # --- SEPARADOR DE MÉDICOS ---
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
        
        st.subheader("Buscar e Listar Médicos")
        
        search_type = st.radio("Buscar por:", ["Listar Todos", "Nome", "Especialidade", "CRM"], horizontal=True, key="med_search")
        
        medicos = None
        desc = None

        if search_type == "Nome":
            nome_med = st.text_input("Digite o nome do médico:", key="med_search_name")
            if nome_med:
                medicos, desc = db_manager.fetch_query(cadastros_queries.PESQUISAR_MEDICO_POR_NOME, (f"%{nome_med}%",))
        elif search_type == "Especialidade":
            espec_med = st.text_input("Digite a especialidade:", key="med_search_spec")
            if espec_med:
                medicos, desc = db_manager.fetch_query(cadastros_queries.PESQUISAR_MEDICO_POR_ESPECIALIDADE, (f"%{espec_med}%",))
        elif search_type == "CRM":
            crm_med = st.text_input("Digite o CRM do médico:", key="med_search_crm")
            if crm_med:
                medicos, desc = db_manager.fetch_query(cadastros_queries.SELECIONAR_MEDICO_POR_CRM, (crm_med,))

        if search_type == "Listar Todos":
             medicos, desc = db_manager.fetch_query(cadastros_queries.LISTAR_MEDICOS_COM_ESPECIALIDADE)

        if medicos:
            df_medicos = pd.DataFrame(medicos, columns=[d[0] for d in desc])
            st.dataframe(df_medicos, use_container_width=True)
        elif search_type != "Listar Todos":
            st.info("Nenhum médico encontrado com o critério fornecido.")

        st.markdown("---")
        
        col_alt_salario, col_rem_med = st.columns(2)

        with col_alt_salario:
            st.subheader("Alterar Salário")
            id_med_salario = st.number_input("ID do Médico", min_value=1, step=1, key="id_med_salario")
            novo_salario = st.number_input("Novo Salário", min_value=0.0, format="%.2f", key="novo_salario")
            if st.button("Alterar Salário"):
                if db_manager.execute_query(cadastros_queries.ATUALIZAR_SALARIO_MEDICO, (novo_salario, id_med_salario)):
                    st.success("Salário atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Falha ao atualizar. Verifique o ID do médico.")
        
        with col_rem_med:
            st.subheader("Remover Médico")
            id_rem_med = st.number_input("ID do Médico", min_value=1, step=1, key="id_rem_med")
            if st.button("Remover Médico", type="primary"):
                st.session_state.confirm_delete = {'type': 'médico', 'id': id_rem_med}

            if st.session_state.confirm_delete['type'] == 'médico':
                st.warning(f"Tem a certeza de que quer apagar o médico com ID {st.session_state.confirm_delete['id']}?")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Sim, apagar", key="confirm_med"):
                        med_id = st.session_state.confirm_delete['id']
                        if safe_remover(med_id, cadastros_queries.REMOVER_MEDICO, "", "médico"):
                            st.session_state.confirm_delete = {'type': None, 'id': None}
                            st.rerun()
                with cancel_col:
                    if st.button("Cancelar", key="cancel_med"):
                        st.session_state.confirm_delete = {'type': None, 'id': None}
                        st.rerun()

    # --- SEPARADOR DE FUNCIONÁRIOS ---
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
        
        st.subheader("Buscar e Listar Funcionários")

        search_type_func = st.radio("Buscar por:", ["Listar Todos", "Nome", "Tipo de Contrato"], horizontal=True, key="func_search")

        funcionarios = None
        desc = None

        if search_type_func == "Nome":
            nome_func_search = st.text_input("Digite o nome do funcionário:", key="func_search_name")
            if nome_func_search:
                funcionarios, desc = db_manager.fetch_query(cadastros_queries.PESQUISAR_FUNCIONARIO_POR_NOME, (f"%{nome_func_search}%",))
        elif search_type_func == "Tipo de Contrato":
            contrato_search = st.selectbox("Selecione o tipo de contrato:", ["CLT", "PJ", "Estágio"], key="func_search_contract")
            if contrato_search:
                funcionarios, desc = db_manager.fetch_query(cadastros_queries.PESQUISAR_FUNCIONARIO_POR_TIPO_DE_CONTRATO, (contrato_search,))
        
        if search_type_func == "Listar Todos":
            funcionarios, desc = db_manager.fetch_query(cadastros_queries.LISTAR_TODOS_FUNCIONARIOS)
        
        if funcionarios:
            df_func = pd.DataFrame(funcionarios, columns=[d[0] for d in desc])
            st.dataframe(df_func, use_container_width=True)
        elif search_type_func != "Listar Todos":
            st.info("Nenhum funcionário encontrado com o critério fornecido.")

        st.markdown("---")

        col_alt_perfil, col_rem_func = st.columns(2)

        with col_alt_perfil:
            st.subheader("Alterar Perfil de Acesso")
            id_func_perfil = st.number_input("ID do Funcionário", min_value=1, step=1, key="id_func_perfil")
            novo_perfil_selecionado = st.selectbox("Novo Perfil de Acesso*", perfis_opts, key="new_profile")
            if st.button("Alterar Perfil"):
                if "Nenhum" in novo_perfil_selecionado:
                    st.warning("Selecione um perfil válido.")
                else:
                    novo_perfil_id = int(novo_perfil_selecionado.split(" - ")[0])
                    if db_manager.execute_query(cadastros_queries.ATUALIZAR_PERFIL_ACESSO_FUNCIONARIO, (novo_perfil_id, id_func_perfil)):
                        st.success("Perfil de acesso atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Falha ao atualizar. Verifique o ID do funcionário.")

        with col_rem_func:
            st.subheader("Remover Funcionário")
            id_rem_func = st.number_input("ID do Funcionário", min_value=1, step=1, key="id_rem_func")
            if st.button("Remover Funcionário", type="primary"):
                st.session_state.confirm_delete = {'type': 'funcionário', 'id': id_rem_func}

            if st.session_state.confirm_delete['type'] == 'funcionário':
                st.warning(f"Tem a certeza de que quer apagar o funcionário com ID {st.session_state.confirm_delete['id']}?")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Sim, apagar", key="confirm_func"):
                        func_id = st.session_state.confirm_delete['id']
                        if safe_remover(func_id, cadastros_queries.REMOVER_FUNCIONARIO, "", "funcionário"):
                            st.session_state.confirm_delete = {'type': None, 'id': None}
                            st.rerun()
                with cancel_col:
                    if st.button("Cancelar", key="cancel_func"):
                        st.session_state.confirm_delete = {'type': None, 'id': None}
                        st.rerun()

    # --- SEPARADOR DE ESPECIALIDADES ---
    with tab_especialidades:
        st.subheader("Gerenciamento de Especialidades")
        
        with st.expander("➕ Cadastrar Nova Especialidade"):
            with st.form("nova_especialidade_form", clear_on_submit=True):
                nome_espec = st.text_input("Nome da Especialidade")
                ativa = st.checkbox("Ativa", value=True)
                if st.form_submit_button("Salvar Especialidade"):
                    res = db_manager.execute_and_fetch_one(cadastros_queries.INSERIR_ESPECIALIDADE, (nome_espec, ativa))
                    if res:
                        st.success(f"Especialidade '{nome_espec}' salva com ID {res[0]}.")
                    else:
                        st.error("Erro ao salvar especialidade.")

        st.subheader("Buscar e Listar Especialidades")

        nome_pesquisa_espec = st.text_input("Pesquisar por nome:", key="search_spec_name")
        if nome_pesquisa_espec:
            especialidades, desc = db_manager.fetch_query(cadastros_queries.PESQUISAR_ESPECIALIDADE_POR_NOME, (f"%{nome_pesquisa_espec}%",))
        else:
            especialidades, desc = db_manager.fetch_query(cadastros_queries.LISTAR_TODAS_ESPECIALIDADES)

        if especialidades:
            df_espec = pd.DataFrame(especialidades, columns=[d[0] for d in desc])
            st.dataframe(df_espec, use_container_width=True)
            
            st.markdown("---")
            col_alt_status, col_rem_esp = st.columns(2)

            with col_alt_status:
                st.subheader("Alterar Status (Ativa/Inativa)")
                id_alt_status = st.number_input("ID da Especialidade", min_value=1, step=1, key="id_alt_status_esp")
                espec_data, _ = db_manager.fetch_query(cadastros_queries.SELECIONAR_ESPECIALIDADE_POR_ID, (id_alt_status,))
                if espec_data:
                    status_atual = espec_data[0][2]
                    novo_status = st.selectbox("Novo Status", [True, False], index=0 if status_atual else 1, format_func=lambda x: "Ativa" if x else "Inativa")
                    if st.button("Alterar Status"):
                        if db_manager.execute_query(cadastros_queries.ATUALIZAR_STATUS_ESPECIALIDADE, (novo_status, id_alt_status)):
                            st.success("Status atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Falha ao atualizar o status.")
                else:
                    st.info("Digite um ID válido para alterar o status.")

            with col_rem_esp:
                st.subheader("Remover Especialidade")
                id_rem_esp = st.number_input("ID da Especialidade", min_value=1, step=1, key="id_rem_esp")
                if st.button("Remover Especialidade", type="primary"):
                    st.session_state.confirm_delete = {'type': 'especialidade', 'id': id_rem_esp}
            
            if st.session_state.confirm_delete['type'] == 'especialidade':
                st.warning(f"Tem a certeza de que quer apagar a especialidade com ID {st.session_state.confirm_delete['id']}?")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Sim, apagar"):
                        espec_id = st.session_state.confirm_delete['id']
                        if safe_remover(espec_id, cadastros_queries.REMOVER_ESPECIALIDADE, cadastros_queries.VERIFICAR_MEDICOS_POR_ESPECIALIDADE, "especialidade"):
                            st.session_state.confirm_delete = {'type': None, 'id': None}
                            st.rerun()
                with cancel_col:
                    if st.button("Cancelar", key="cancel_esp"):
                        st.session_state.confirm_delete = {'type': None, 'id': None}
                        st.rerun()
        else:
            st.info("Nenhuma especialidade encontrada.")


    # --- SEPARADOR DE PERFIS DE ACESSO ---
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
                        if res:
                            st.success(f"Perfil '{nome_perfil}' salvo com ID {res[0]}.")
                        else:
                             st.error("Erro ao salvar perfil. O nome pode já existir.")

        st.subheader("Buscar e Listar Perfis de Acesso")

        nome_pesquisa_perfil = st.text_input("Pesquisar por nome:", key="search_profile_name")
        if nome_pesquisa_perfil:
            perfis, desc = db_manager.fetch_query(cadastros_queries.PESQUISAR_PERFIL_ACESSO_POR_NOME, (f"%{nome_pesquisa_perfil}%",))
        else:
            perfis, desc = db_manager.fetch_query(cadastros_queries.LISTAR_TODOS_PERFIS_ACESSO)

        if perfis:
            df_perfis = pd.DataFrame(perfis, columns=[d[0] for d in desc])
            st.dataframe(df_perfis, use_container_width=True)

            st.markdown("---")
            col_alt_desc, col_rem_perfil = st.columns(2)

            with col_alt_desc:
                st.subheader("Alterar Descrição")
                id_alt_desc = st.number_input("ID do Perfil", min_value=1, step=1, key="id_alt_desc_perfil")
                nova_desc = st.text_area("Nova Descrição", key="new_desc_perfil")
                if st.button("Alterar Descrição"):
                    if db_manager.execute_query(cadastros_queries.ATUALIZAR_DESCRICAO_PERFIL_ACESSO, (nova_desc, id_alt_desc)):
                        st.success("Descrição atualizada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Falha ao atualizar a descrição.")
            
            with col_rem_perfil:
                st.subheader("Remover Perfil de Acesso")
                id_rem_perfil = st.number_input("ID do Perfil", min_value=1, step=1, key="id_rem_perfil")
                if st.button("Remover Perfil", type="primary"):
                    st.session_state.confirm_delete = {'type': 'perfil', 'id': id_rem_perfil}

            if st.session_state.confirm_delete['type'] == 'perfil':
                st.warning(f"Tem a certeza de que quer apagar o perfil com ID {st.session_state.confirm_delete['id']}?")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Sim, apagar", key="confirm_perfil"):
                        perfil_id = st.session_state.confirm_delete['id']
                        if safe_remover(perfil_id, cadastros_queries.REMOVER_PERFIL_ACESSO, cadastros_queries.VERIFICAR_FUNCIONARIOS_POR_PERFIL, "perfil de acesso"):
                            st.session_state.confirm_delete = {'type': None, 'id': None}
                            st.rerun()
                with cancel_col:
                    if st.button("Cancelar", key="cancel_perfil"):
                        st.session_state.confirm_delete = {'type': None, 'id': None}
                        st.rerun()
        else:
            st.info("Nenhum perfil de acesso encontrado.")


# --- PÁGINA CLÍNICA ---
def pagina_clinico():
    st.header("Módulo Clínico")

    tab_consultas, tab_receitas = st.tabs(["Consultas", "Receitas"])

    with tab_consultas:
        st.subheader("Gerenciamento de Consultas")
        
        _, medicos_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_MEDICOS_COM_ESPECIALIDADE)
        _, pacientes_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_TODOS_PACIENTES)
        
        with st.expander("🗓️ Agendar Nova Consulta"):
            with st.form("nova_consulta_form", clear_on_submit=True):
                paciente_selecionado = st.selectbox("Paciente*", pacientes_opts)
                medico_selecionado = st.selectbox("Médico*", medicos_opts)
                data_consulta = st.date_input("Data da Consulta")
                hora_consulta = st.time_input("Hora da Consulta")
                motivo = st.text_area("Motivo da Consulta")
                
                if st.form_submit_button("Agendar Consulta"):
                    if "Nenhum" in paciente_selecionado or "Nenhum" in medico_selecionado:
                        st.warning("É necessário selecionar um paciente e um médico.")
                    else:
                        paciente_id = int(paciente_selecionado.split(" - ")[0])
                        medico_id = int(medico_selecionado.split(" - ")[0])
                        data_hora_completa = datetime.combine(data_consulta, hora_consulta)
                        dados = (paciente_id, medico_id, data_hora_completa, motivo, 'Agendada')
                        res = db_manager.execute_and_fetch_one(clinico_queries.INSERIR_CONSULTA, dados)
                        if res: 
                            st.success(f"Consulta agendada com ID {res[0]}")
                        else: 
                            st.error("Falha ao agendar consulta.")

        st.subheader("Consultas Agendadas")
        
        pesquisa_consulta_paciente = st.text_input("Pesquisar consultas por nome do paciente:", key="search_consulta_pac")
        
        if pesquisa_consulta_paciente:
            consultas, desc = db_manager.fetch_query(clinico_queries.PESQUISAR_CONSULTA_POR_NOME_PACIENTE, (f"%{pesquisa_consulta_paciente}%",))
        else:
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
                    st.rerun()
                else:
                    st.error("Falha ao atualizar. Verifique o ID da consulta.")
        else:
            st.info("Nenhuma consulta encontrada.")

    with tab_receitas:
        st.subheader("Visualização de Receitas")
        
        pesquisa_receita_paciente = st.text_input("Pesquisar receitas por nome do paciente:", key="search_receita_pac")
        
        if pesquisa_receita_paciente:
            receitas, desc = db_manager.fetch_query(clinico_queries.PESQUISAR_RECEITA_POR_PACIENTE, (f"%{pesquisa_receita_paciente}%",))
        else:
            receitas, desc = db_manager.fetch_query(clinico_queries.PESQUISAR_RECEITA_POR_PACIENTE, ("%%",))

        if receitas:
            df_receitas = pd.DataFrame(receitas, columns=[d[0] for d in desc])
            st.dataframe(df_receitas, use_container_width=True)
        else:
            st.info("Nenhuma receita encontrada.")


# --- PÁGINA FINANCEIRA ---
def pagina_financeiro():
    st.header("Módulo Financeiro")

    st.subheader("Gerenciamento de Pagamentos")
    
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
        pag_pendentes, _ = db_manager.fetch_query("SELECT id, consulta_id, valor FROM financeiro.pagamentos WHERE pago = FALSE;")
        if pag_pendentes:
            _, pag_pendentes_opts = carregar_dados_para_selectbox("SELECT id, valor FROM financeiro.pagamentos WHERE pago = FALSE;")
            pag_a_quitar = st.selectbox("Selecione o Pagamento Pendente", pag_pendentes_opts)
            if st.button("Confirmar Recebimento"):
                pag_id = int(pag_a_quitar.split(" - ")[0])
                if db_manager.execute_query(financeiro_queries.ATUALIZAR_STATUS_PAGAMENTO, (pag_id,)):
                    st.success("Pagamento confirmado!")
                    st.rerun()
                else:
                    st.error("Falha ao confirmar pagamento.")
        else:
            st.info("Não há pagamentos pendentes.")

# --- PÁGINA DE VENDAS ---
def pagina_vendas():
    st.header("Módulo de Vendas")

    tab_produtos, tab_venda, tab_relatorios = st.tabs(["Produtos e Estoque", "Realizar Venda", "Relatórios de Vendas"])

    with tab_produtos:
        st.subheader("Gerenciamento de Produtos")
        
        col_cad_prod, col_cad_cat = st.columns(2)
        with col_cad_prod:
            with st.expander("➕ Cadastrar Novo Produto"):
                with st.form("novo_produto_form", clear_on_submit=True):
                    nome_prod = st.text_input("Nome do Produto*")
                    desc_prod = st.text_area("Descrição")
                    preco_prod = st.number_input("Preço (R$)", min_value=0.01, format="%.2f")
                    qtd_inicial = st.number_input("Quantidade em Estoque*", min_value=0, step=1)
                    
                    _, cat_opts = carregar_dados_para_selectbox(vendas_queries.LISTAR_CATEGORIAS)
                    cat_selecionada = st.selectbox("Categoria", cat_opts)
                    
                    fab_mari = st.checkbox("Fabricado em Mari?")
                    
                    if st.form_submit_button("Salvar Produto"):
                        if not nome_prod or "Nenhum" in cat_selecionada:
                            st.warning("Nome e Categoria são obrigatórios.")
                        else:
                            cat_id = int(cat_selecionada.split(" - ")[0])
                            res = db_manager.execute_and_fetch_one(vendas_queries.INSERIR_PRODUTO, (nome_prod, desc_prod, preco_prod, cat_id, fab_mari, True))
                            
                            if res:
                                novo_produto_id = res[0]
                                if db_manager.execute_query(vendas_queries.ATUALIZAR_ESTOQUE, (novo_produto_id, qtd_inicial)):
                                    st.success(f"Produto '{nome_prod}' salvo com ID {novo_produto_id} e estoque inicial de {qtd_inicial} unidades.")
                                else:
                                    st.warning(f"Produto '{nome_prod}' salvo com ID {novo_produto_id}, mas falha ao atualizar o estoque.")
                            else:
                                st.error("Erro ao salvar produto.")
        with col_cad_cat:
            with st.expander("➕ Cadastrar Nova Categoria"):
                with st.form("nova_cat_form", clear_on_submit=True):
                    nome_cat = st.text_input("Nome da Categoria*")
                    if st.form_submit_button("Salvar Categoria"):
                        if not nome_cat:
                            st.warning("Nome é obrigatório.")
                        else:
                            res = db_manager.execute_and_fetch_one(vendas_queries.INSERIR_CATEGORIA, (nome_cat,))
                            if res: st.success(f"Categoria '{nome_cat}' salva com ID {res[0]}.")
                            else: st.error("Erro ao salvar. Nome pode já existir.")
        with st.expander("✏️ Alterar Produto Cadastrado"):
            # Carrega os produtos para o selectbox
            _, produtos_opts_edit = carregar_dados_para_selectbox("SELECT id, nome FROM vendas.produtos WHERE ativo=TRUE ORDER BY nome;")
            
            if "Nenhum" in produtos_opts_edit[0]:
                st.info("Nenhum produto para editar.")
            else:
                produto_selecionado_edit = st.selectbox("Selecione um produto para alterar", produtos_opts_edit)
                produto_id_edit = int(produto_selecionado_edit.split(" - ")[0])

                # Busca os dados atuais do produto selecionado
                dados_atuais, _ = db_manager.fetch_query(vendas_queries.SELECIONAR_PRODUTO_POR_ID, (produto_id_edit,))

                if dados_atuais:
                    dados_atuais = dados_atuais[0] # Pega a primeira linha do resultado
                    
                    with st.form(key="edit_produto_form", clear_on_submit=True):
                        st.write(f"Editando: **{dados_atuais[0]}**")

                        novo_nome = st.text_input("Nome do Produto", value=dados_atuais[0])
                        nova_descricao = st.text_area("Descrição", value=dados_atuais[1])
                        novo_preco = st.number_input("Preço (R$)", min_value=0.01, format="%.2f", value=float(dados_atuais[2]))

                        # Lógica para o selectbox de categoria
                        categorias_map, cat_opts_edit = carregar_dados_para_selectbox(vendas_queries.LISTAR_CATEGORIAS)
                        id_categorias = list(categorias_map.keys())
                        try:
                            index_cat_atual = id_categorias.index(dados_atuais[3])
                        except ValueError:
                            index_cat_atual = 0 # Categoria padrão caso não encontre
                        
                        nova_cat_selecionada = st.selectbox("Categoria", cat_opts_edit, index=index_cat_atual)

                        nova_fab_mari = st.checkbox("Fabricado em Mari?", value=dados_atuais[4])

                        if st.form_submit_button("Salvar Alterações"):
                            nova_cat_id = int(nova_cat_selecionada.split(" - ")[0])
                            dados_update = (novo_nome, nova_descricao, novo_preco, nova_cat_id, nova_fab_mari, produto_id_edit)
                            
                            if db_manager.execute_query(vendas_queries.ATUALIZAR_PRODUTO, dados_update):
                                st.success(f"Produto '{novo_nome}' atualizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Falha ao atualizar o produto.")    
        with st.expander("🗑️ Remover Produto"):
            # Carrega os produtos para o selectbox
            _, produtos_opts_rem = carregar_dados_para_selectbox("SELECT id, nome FROM vendas.produtos WHERE ativo=TRUE ORDER BY nome;")

            if "Nenhum" in produtos_opts_rem[0]:
                st.info("Nenhum produto ativo para remover.")
            else:
                produto_selecionado_rem = st.selectbox("Selecione um produto para remover", produtos_opts_rem, key="rem_prod")
                
                if st.button("Remover Produto", type="primary"):
                    produto_id_rem = int(produto_selecionado_rem.split(" - ")[0])
                    st.session_state.confirm_delete = {'type': 'produto', 'id': produto_id_rem}

            # Lógica de confirmação que já existe em outras partes do app
            if st.session_state.get('confirm_delete', {}).get('type') == 'produto':
                produto_id_rem = st.session_state.confirm_delete['id']
                st.warning(f"Tem certeza de que deseja remover o produto com ID {produto_id_rem}? Ele ficará inativo e não aparecerá mais nas vendas.")
                
                col_conf, col_canc = st.columns(2)
                with col_conf:
                    if st.button("Sim, remover"):
                        if db_manager.execute_query(vendas_queries.REMOVER_PRODUTO, (produto_id_rem,)):
                            st.success("Produto removido (inativado) com sucesso!")
                            st.session_state.confirm_delete = {'type': None, 'id': None}
                            st.rerun()
                        else:
                            st.error("Falha ao remover o produto.")
                with col_canc:
                    if st.button("Cancelar"):
                        st.session_state.confirm_delete = {'type': None, 'id': None}
                        st.rerun()               

        st.markdown("---")

        # --- BLOCO PARA EXIBIR A TABELA DE ESTOQUE COM BUSCA E FILTROS ---
        st.subheader("Estoque de Produtos")
        busca_produto = st.text_input("🔎 Buscar produto por nome:")

        # Inicializa as variáveis
        estoque = None
        desc_est = None

        if busca_produto:
            # Se o campo de busca por nome estiver preenchido, ele tem prioridade
            estoque, desc_est = db_manager.fetch_query(vendas_queries.BUSCAR_PRODUTOS_POR_NOME, (f"%{busca_produto}%",))
        else:
            # Caso contrário, exibe os outros filtros
            st.markdown("---")
            tipo_filtro = st.radio(
                "Filtros Adicionais:",
                ["Listar Todos", "Por Categoria", "Fabricados em Mari", "Estoque Baixo (< 5)"],
                horizontal=True,
                key="filtro_produtos"
            )

            if tipo_filtro == "Listar Todos":
                estoque, desc_est = db_manager.fetch_query(vendas_queries.LISTAR_TODOS_PRODUTOS)
            
            elif tipo_filtro == "Por Categoria":
                _, cat_opts_filter = carregar_dados_para_selectbox(vendas_queries.LISTAR_CATEGORIAS)
                if "Nenhum" in cat_opts_filter[0]:
                    st.warning("Nenhuma categoria cadastrada.")
                else:
                    categoria_selecionada_filtro = st.selectbox("Selecione a categoria", cat_opts_filter)
                    cat_nome = categoria_selecionada_filtro.split(" - ")[1]
                    estoque, desc_est = db_manager.fetch_query(vendas_queries.BUSCAR_PRODUTOS_POR_CATEGORIA, (cat_nome,))

            elif tipo_filtro == "Fabricados em Mari":
                estoque, desc_est = db_manager.fetch_query(vendas_queries.BUSCAR_PRODUTOS_FAB_MARI)

            elif tipo_filtro == "Estoque Baixo (< 5)":
                estoque, desc_est = db_manager.fetch_query(vendas_queries.BUSCAR_PRODUTOS_ESTOQUE_BAIXO)

        # Exibe os resultados
        st.markdown("---")
        if estoque:
            df_est = pd.DataFrame(estoque, columns=[d[0] for d in desc_est])
            st.dataframe(df_est, use_container_width=True)
        else:
            st.info("Nenhum produto encontrado com os critérios selecionados.")

        # --- BLOCO PARA LISTAR AS CATEGORIAS CADASTRADAS ---
        st.markdown("---")
        st.subheader("Categorias Cadastradas")
        categorias, desc_cat = db_manager.fetch_query(vendas_queries.LISTAR_CATEGORIAS)

        if categorias:
            df_cat = pd.DataFrame(categorias, columns=[d[0] for d in desc_cat])
            st.dataframe(df_cat, use_container_width=True)
        else:
            st.info("Nenhuma categoria cadastrada.")

        # --- BLOCO PARA ATUALIZAR O ESTOQUE MANUALMENTE ---
        st.markdown("---")
        st.subheader("⚙️ Atualizar Estoque Manualmente")

        _, produtos_opts_update = carregar_dados_para_selectbox("SELECT id, nome FROM vendas.produtos WHERE ativo=TRUE ORDER BY nome;")

        if "Nenhum" in produtos_opts_update[0]:
            st.info("Nenhum produto cadastrado para atualizar.")
        else:
            col_prod_select, col_qtd_update, col_btn_update = st.columns([2, 1, 1])
            
            with col_prod_select:
                produto_selecionado_update = st.selectbox("Selecione o Produto", produtos_opts_update, key="prod_update_select")
            
            with col_qtd_update:
                nova_quantidade = st.number_input("Nova Quantidade", min_value=0, step=1, key="prod_update_qtd")
            
            with col_btn_update:
                st.write("") 
                st.write("")
                if st.button("Atualizar Estoque"):
                    if "Nenhum" in produto_selecionado_update:
                        st.warning("Por favor, selecione um produto.")
                    else:
                        produto_id_update = int(produto_selecionado_update.split(" - ")[0])
                        
                        if db_manager.execute_query(vendas_queries.ATUALIZAR_ESTOQUE, (produto_id_update, nova_quantidade)):
                            st.success(f"Estoque do produto ID {produto_id_update} atualizado para {nova_quantidade} unidades!")
                            st.rerun()
                        else:
                            st.error("Falha ao atualizar o estoque.")

    with tab_venda:
        st.subheader("Nova Venda")

        # --- NOVO BLOCO: EXPANDER PARA CADASTRO RÁPIDO ---
        with st.expander("👤 Cadastrar Novo Cliente (Rápido)"):
            with st.form("novo_cliente_rapido_form", clear_on_submit=True):
                st.info("Cadastre apenas o essencial. Detalhes podem ser adicionados depois no módulo de Cadastros.")
                novo_nome_cliente = st.text_input("Nome Completo*")
                novo_tel_cliente = st.text_input("Telefone")
                
                if st.form_submit_button("Salvar e Selecionar Cliente"):
                    if not novo_nome_cliente:
                        st.warning("O nome do cliente é obrigatório.")
                    else:
                        # Monta a tupla de dados para a query existente, preenchendo com None
                        dados_cliente_rapido = (
                            novo_nome_cliente, 'O', None, None, novo_tel_cliente,  # Info básica
                            None, None, None, None, None, None, None,             # Endereço
                            False, False, False                                  # Critérios de desconto
                        )
                        resultado = db_manager.execute_and_fetch_one(cadastros_queries.INSERIR_PACIENTE, dados_cliente_rapido)
                        if resultado:
                            novo_cliente_id = resultado[0]
                            st.success(f"Cliente '{novo_nome_cliente}' cadastrado com ID {novo_cliente_id}!")
                            # Usa o session_state para "lembrar" do ID do novo cliente para o selectbox principal
                            st.session_state.cliente_selecionado_id = novo_cliente_id
                            st.rerun()
                        else:
                            st.error("Erro ao cadastrar cliente.")

        # --- LÓGICA PRINCIPAL DA VENDA ---
        
        # Carrega os dados para os dropdowns
        clientes_map, clientes_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_TODOS_PACIENTES)
        _, vendedores_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_VENDEDORES)
        _, produtos_opts = carregar_dados_para_selectbox("SELECT id, nome FROM vendas.produtos WHERE ativo=TRUE ORDER BY nome;")
        
        # --- LÓGICA PARA AUTO-SELECIONAR O NOVO CLIENTE ---
        index_cliente = 0
        if 'cliente_selecionado_id' in st.session_state and st.session_state.cliente_selecionado_id is not None:
            try:
                # Encontra a string correspondente ao ID salvo na lista de opções
                opcao_alvo = next(opt for opt in clientes_opts if opt.startswith(f"{st.session_state.cliente_selecionado_id} -"))
                index_cliente = clientes_opts.index(opcao_alvo)
            except (StopIteration, ValueError):
                index_cliente = 0 # Se não encontrar, volta ao padrão
            # Limpa o session_state após o uso
            st.session_state.cliente_selecionado_id = None

        cliente_sel = st.selectbox("Cliente*", clientes_opts, index=index_cliente)
        vendedor_sel = st.selectbox("Vendedor*", vendedores_opts)
        
        st.markdown("---")
        st.subheader("Carrinho de Compras")

        prod_sel = st.selectbox("Adicionar Produto", produtos_opts)

        # --- LÓGICA DE VERIFICAÇÃO DE ESTOQUE PROATIVA ---
        estoque_disponivel = 0
        if "Nenhum" not in prod_sel:
            prod_id = int(prod_sel.split(" - ")[0])
            estoque_res, _ = db_manager.fetch_query(vendas_queries.CONSULTAR_ESTOQUE_PRODUTO, (prod_id,))
            if estoque_res:
                estoque_disponivel = estoque_res[0][0]

        # Exibe o estoque e limita o campo de quantidade
        st.caption(f"Estoque disponível: {estoque_disponivel} unidades")
        if estoque_disponivel > 0:
            qtd_sel = st.number_input("Quantidade", min_value=1, max_value=estoque_disponivel, value=1, step=1)
        else:
            st.warning("Este produto está sem estoque.")
        # --- FIM DA LÓGICA DE VERIFICAÇÃO ---

        if estoque_disponivel > 0 and st.button("Adicionar ao Carrinho"):
            # A lógica interna para adicionar ao carrinho não muda
            prod_nome = prod_sel.split(" - ")[1]
            preco_unit, _ = db_manager.fetch_query("SELECT preco FROM vendas.produtos WHERE id = %s", (prod_id,))
            
            st.session_state.carrinho.append({
                "produto_id": prod_id, "nome": prod_nome, "quantidade": qtd_sel,
                "preco_unitario": float(preco_unit[0][0])
            })
            st.rerun()
        
        if st.session_state.carrinho:
            st.dataframe(pd.DataFrame(st.session_state.carrinho), use_container_width=True)
            total_carrinho = sum(item['quantidade'] * item['preco_unitario'] for item in st.session_state.carrinho)
            st.metric("Total Bruto", f"R$ {total_carrinho:.2f}")

            if st.button("Limpar Carrinho"):
                st.session_state.carrinho = []; st.rerun()

            st.markdown("---"); st.subheader("Finalizar Venda")

            # --- LÓGICA DE EXIBIÇÃO DO DESCONTO ---
            desconto_aplicado = 0.0
            total_liquido = total_carrinho

            if "Nenhum" not in cliente_sel:
                cliente_id = int(cliente_sel.split(" - ")[0])
                # Verifica se o cliente tem desconto usando a nova query
                resultado_desconto, _ = db_manager.fetch_query(cadastros_queries.VERIFICAR_DESCONTO_CLIENTE, (cliente_id,))
                
                if resultado_desconto and resultado_desconto[0][0] is True:
                    desconto_aplicado = total_carrinho * 0.10
                    total_liquido = total_carrinho - desconto_aplicado
                    st.success("🎉 Desconto de 10% aplicado para este cliente!")

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Bruto", f"R$ {total_carrinho:.2f}")
            col2.metric("Desconto", f"R$ {desconto_aplicado:.2f}")
            col3.metric("✅ Total Líquido", f"R$ {total_liquido:.2f}")
            # --- FIM DA LÓGICA DE EXIBIÇÃO DO DESCONTO ---

            forma_pag = st.selectbox("Forma de Pagamento", ['Dinheiro','Cartão','Boleto','PIX','Berries'])

            if st.button("Efetivar Compra", type="primary"):
                if "Nenhum" in cliente_sel or "Nenhum" in vendedor_sel:
                    st.error("Cliente e Vendedor são obrigatórios.")
                else:
                    cliente_id = int(cliente_sel.split(" - ")[0]); vendedor_id = int(vendedor_sel.split(" - ")[0])
                    status_pag = "Confirmado" if forma_pag in ['Dinheiro', 'Cartão', 'PIX'] else "Pendente"
                    itens_json = json.dumps(st.session_state.carrinho)
                    
                    try:
                        res = db_manager.execute_and_fetch_one(vendas_queries.CHAMAR_EFETIVAR_COMPRA, (cliente_id, vendedor_id, forma_pag, itens_json, status_pag))
                        if res and res[0] > 0:
                            st.success(f"Venda finalizada com sucesso! ID da Venda: {res[0]}")
                            st.balloons()
                            st.session_state.carrinho = []
                            st.rerun()
                        else: 
                            # Este else é para casos onde a função do DB não retorna um ID, mas não gera exceção
                            st.error("Falha ao efetivar a compra. A venda não foi registrada.")

                    except Exception as e:
                        # Converte a exceção em texto para análise
                        error_message = str(e)
                        
                        # Verifica se a mensagem de erro é a de estoque insuficiente
                        if "sem estoque suficiente" in error_message:
                            # Extrai a parte útil da mensagem para exibir ao usuário
                            friendly_error = error_message.split('CONTEXT:')[0].replace('ERRO:', '').strip()
                            st.error(f"⚠️ Venda não realizada! {friendly_error}")
                        else:
                            # Para todos os outros tipos de erro, exibe uma mensagem mais genérica
                            st.error(f"Ocorreu um erro inesperado ao efetivar a compra: {error_message}")

    with tab_relatorios:
        st.subheader("Dashboard de Vendas Mensal por Vendedor")
        
        relatorio, desc_rel = db_manager.fetch_query(vendas_queries.REL_VENDAS_POR_VENDEDOR_MES)
        
        if not relatorio:
            st.info("Ainda não há dados de vendas para exibir.")
        else:
            df_rel = pd.DataFrame(relatorio, columns=[d[0] for d in desc_rel])
            # Converte a coluna de mês para um formato mais legível
            df_rel['mes'] = pd.to_datetime(df_rel['mes']).dt.strftime('%Y-%m')

            st.divider()

            # --- 1. FILTROS INTERATIVOS ---
            st.sidebar.header("Filtros do Relatório")
            
            # Filtro por Mês
            meses = sorted(df_rel['mes'].unique(), reverse=True)
            mes_selecionado = st.sidebar.multiselect("Filtrar por Mês:", options=meses, default=meses)
            
            # Filtro por Vendedor
            vendedores = sorted(df_rel['vendedor'].unique())
            vendedor_selecionado = st.sidebar.multiselect("Filtrar por Vendedor:", options=vendedores, default=vendedores)

            # Aplica os filtros no DataFrame
            df_filtrado = df_rel[
                (df_rel['mes'].isin(mes_selecionado)) &
                (df_rel['vendedor'].isin(vendedor_selecionado))
            ]

            if df_filtrado.empty:
                st.warning("Nenhum dado encontrado para os filtros selecionados.")
            else:
                # --- 2. KPIs (INDICADORES CHAVE) ---
                total_faturado = df_filtrado['valor_total_vendido'].sum()
                num_total_vendas = df_filtrado['total_vendas'].sum()
                
                st.subheader("Resumo do Período Selecionado")
                col1, col2 = st.columns(2)
                col1.metric("Faturamento Total", f"R$ {total_faturado:,.2f}")
                col2.metric("Número de Vendas", f"{num_total_vendas}")

                st.divider()

                # --- 3. GRÁFICOS ---
                st.subheader("Análise Gráfica")

                # Agrupa os dados por vendedor, mas desta vez MANTEMOS o reset_index()
                df_grafico = df_filtrado.groupby('vendedor').agg(
                    valor_total_vendido=('valor_total_vendido', 'sum'),
                    ticket_medio=('ticket_medio', 'mean')
                ).reset_index()

                col_graf1, col_graf2 = st.columns(2)
                with col_graf1:
                    st.write("Valor Total Vendido por Vendedor")
                    # Cria o gráfico usando Altair, dando instruções explícitas
                    chart_valor = alt.Chart(df_grafico).mark_bar().encode(
                        x=alt.X('vendedor', type='nominal', title='Vendedor', sort='-y'),
                        y=alt.Y('valor_total_vendido', type='quantitative', title='Valor Total Vendido (R$)'),
                        tooltip=['vendedor', 'valor_total_vendido']
                    ).interactive()
                    st.altair_chart(chart_valor, use_container_width=True)

                with col_graf2:
                    st.write("Ticket Médio por Vendedor")
                    # Cria o segundo gráfico com Altair
                    chart_ticket = alt.Chart(df_grafico).mark_bar().encode(
                        x=alt.X('vendedor', type='nominal', title='Vendedor', sort='-y'),
                        y=alt.Y('ticket_medio', type='quantitative', title='Ticket Médio (R$)'),
                        tooltip=['vendedor', 'ticket_medio']
                    ).interactive()
                    st.altair_chart(chart_ticket, use_container_width=True)

                # --- 4. DADOS DETALHADOS ---
                st.subheader("Dados Detalhados")
                st.dataframe(df_filtrado, use_container_width=True)

def pagina_cliente():
    st.header("👤 Portal do Cliente")
    st.write("Bem-vindo! Aqui você pode consultar seus dados e histórico de compras.")
    st.divider()

    # --- Simulação de Login: Cliente seleciona seu nome ---
    _, pacientes_opts = carregar_dados_para_selectbox(cadastros_queries.LISTAR_TODOS_PACIENTES)
    # Adiciona uma opção default para o selectbox
    pacientes_opts.insert(0, "Selecione seu nome para continuar...")
    
    cliente_selecionado = st.selectbox("Para começar, selecione seu nome na lista:", pacientes_opts)

    # Se um cliente foi selecionado (e não é a opção default)
    if "Selecione" not in cliente_selecionado:
        cliente_id = int(cliente_selecionado.split(" - ")[0])

        # --- 1. Exibir Dados Cadastrais ---
        st.subheader("Meus Dados Cadastrais")
        dados_cliente, desc_cliente = db_manager.fetch_query(cadastros_queries.CONSULTAR_DADOS_CLIENTE, (cliente_id,))
        
        if dados_cliente:
            cliente_info = pd.DataFrame(dados_cliente, columns=[d[0] for d in desc_cliente]).iloc[0]
            col1, col2 = st.columns(2)
            col1.text_input("Nome", value=cliente_info['nome'], disabled=True)
            col1.text_input("Email", value=cliente_info['email'], disabled=True)
            col2.text_input("CPF", value=cliente_info['cpf'], disabled=True)
            col2.text_input("Telefone", value=cliente_info['telefone'], disabled=True)

            # --- Lógica para exibir status de desconto ---
            st.write("") # Adiciona um espaço
            
            tem_desconto = cliente_info['torce_flamengo'] or cliente_info['assiste_one_piece'] or cliente_info['nasceu_sousa']
            
            if tem_desconto:
                st.success("🎉 **Status:** Você tem direito a 10% de desconto em suas compras!")
                
                # Lista os motivos do desconto
                razoes = []
                if cliente_info['torce_flamengo']:
                    razoes.append("torcer para o Flamengo")
                if cliente_info['assiste_one_piece']:
                    razoes.append("assistir One Piece")
                if cliente_info['nasceu_sousa']:
                    razoes.append("ser de Sousa-PB")
                
                st.markdown(f"**Motivo(s):** {', '.join(razoes).capitalize()}.")
            else:
                st.info("**Status:** Você ainda não possui descontos especiais ativos.")
        
        st.divider()

        # --- 2. Exibir Histórico de Pedidos ---
        st.subheader("Meus Pedidos")
        pedidos_cliente, desc_pedidos = db_manager.fetch_query(cadastros_queries.CONSULTAR_PEDIDOS_CLIENTE, (cliente_id,))
        
        if not pedidos_cliente:
            st.info("Você ainda não realizou nenhum pedido.")
        else:
            df_pedidos = pd.DataFrame(pedidos_cliente, columns=[d[0] for d in desc_pedidos])
            
            # Mostra os pedidos de forma interativa com expanders
            for index, row in df_pedidos.iterrows():
                data_formatada = row['data'].strftime('%d/%m/%Y às %H:%M')
                expander_title = f"Pedido #{row['venda_id']}  -  {data_formatada}  -  Valor: R$ {row['total_liquido']:.2f}"
                
                with st.expander(expander_title):
                    st.write(f"**Forma de Pagamento:** {row['forma_pagamento']}")
                    st.write(f"**Status:** {row['status_pagamento']}")
                    
                    # Busca os itens detalhados do pedido
                    itens_pedido, desc_itens = db_manager.fetch_query(vendas_queries.DETALHAR_ITENS_PEDIDO_CLIENTE, (row['venda_id'],))
                    if itens_pedido:
                        df_itens = pd.DataFrame(itens_pedido, columns=[d[0] for d in desc_itens])
                        st.dataframe(df_itens, use_container_width=True)

# --- NAVEGAÇÃO PRINCIPAL (SIDEBAR) ---
def main():
    st.sidebar.image("image_0b8972.jpg", use_container_width=True)
    
    # Seletor de Modo de Acesso (Funcionário ou Cliente)
    st.sidebar.header("Modo de Acesso")
    access_mode = st.sidebar.radio("Selecione o modo de visualização:", ["Funcionário", "Cliente"])
    
    if access_mode == "Funcionário":
        # Mantém a navegação completa para funcionários
        paginas = {
            "Cadastros": pagina_cadastros,
            "Clínico": pagina_clinico,
            "Financeiro": pagina_financeiro,
            "Vendas": pagina_vendas,
        }
        st.sidebar.divider()
        selecao = st.sidebar.radio("Navegue pelos Módulos", list(paginas.keys()))
        
        pagina_selecionada_func = paginas[selecao]
        pagina_selecionada_func()

    else: # Se o modo for "Cliente"
        # Chama a nova página exclusiva para clientes
        pagina_cliente()

    st.sidebar.divider()
    st.sidebar.info("Projeto de Banco de Dados\n\nDesenvolvido com Python, Streamlit e PostgreSQL.")

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == "__main__":
    if db_manager.conn:
        main()
    else:
        st.error("🔴 Falha na conexão com o banco de dados!")
        st.info("Por favor, verifique as seguintes opções:")
        st.markdown("""
        - O serviço do PostgreSQL está ativo na sua máquina?
        - As credenciais no ficheiro `db_config.py` (utilizador, senha, nome do banco) estão corretas?
        """)

