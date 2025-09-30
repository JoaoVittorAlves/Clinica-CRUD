import streamlit as st
import pandas as pd
from db_manager import DatabaseManager
from queries import cadastros_queries, clinico_queries, financeiro_queries
from datetime import datetime

st.set_page_config(page_title="Gestão da Clínica", layout="wide")

if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = {'type': None, 'id': None}


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
        st.error(f"Não é possível remover este(a) {tipo_registo}. Existem {dependentes[0][0]} registos que dependem dele(a).")
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

# --- NAVEGAÇÃO PRINCIPAL (SIDEBAR) ---
def main():
    st.sidebar.image("image_0b8972.jpg", use_container_width=True)
    
    paginas = {
        "Cadastros": pagina_cadastros,
        "Clínico": pagina_clinico,
        "Financeiro": pagina_financeiro,
    }
    
    st.sidebar.divider()
    
    selecao = st.sidebar.radio("Navegue pelos Módulos", list(paginas.keys()))
    
    st.sidebar.divider()
    st.sidebar.info("Projeto de Banco de Dados I\n\nDesenvolvido com Python, Streamlit e PostgreSQL.")
    
    pagina_selecionada_func = paginas[selecao]
    pagina_selecionada_func()

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

