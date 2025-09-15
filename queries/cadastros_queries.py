# =============================================================================
# OPERAÇÕES NA TABELA PACIENTES
# =============================================================================

# 1. Inserir
INSERIR_PACIENTE = "" \
"INSERT INTO cadastros.pacientes (nome, sexo, email, cpf, telefone, logradouro, numero, complemento, bairro, cidade, sigla_estado, cep) " \
"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
"RETURNING id;"

# 2. Alterar
ATUALIZAR_TELEFONE_PACIENTE = "" \
"UPDATE cadastros.pacientes " \
"SET telefone = %s " \
"WHERE id = %s;"

# 3. Pesquisar por nome
PESQUISAR_PACIENTE_POR_NOME = "" \
"SELECT id, nome, email, telefone " \
"FROM cadastros.pacientes " \
"WHERE nome ILIKE %s;"

# 4. Remover
REMOVER_PACIENTE = "" \
"DELETE FROM cadastros.pacientes " \
"WHERE id = %s;"

# 5. Listar todos
LISTAR_TODOS_PACIENTES = "" \
"SELECT id, nome, email, telefone " \
"FROM cadastros.pacientes " \
"ORDER BY id;"

# 6. Exibir um
SELECIONAR_PACIENTE_POR_ID = "" \
"SELECT * " \
"FROM cadastros.pacientes " \
"WHERE id = %s;"

# =============================================================================
# OPERAÇÕES NA TABELA MEDICOS
# =============================================================================

INSERIR_MEDICO = "" \
"INSERT INTO cadastros.medicos (nome, telefone, email, crm, salario, especialidade_id, logradouro, numero, complemento, bairro, cidade, sigla_estado, cep) " \
"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
"RETURNING id;"

ATUALIZAR_SALARIO_MEDICO = "" \
"UPDATE cadastros.medicos " \
"SET salario = %s " \
"WHERE id = %s;"

PESQUISAR_MEDICO_POR_NOME = "" \
"SELECT id, nome, crm " \
"FROM cadastros.medicos " \
"WHERE nome ILIKE %s;"

PESQUISAR_MEDICO_POR_ESPECIALIDADE = "" \
"SELECT " \
"    m.id, " \
"    m.nome, " \
"    m.crm, " \
"    e.nome AS especialidade " \
"FROM " \
"    cadastros.medicos AS m " \
"JOIN " \
"    cadastros.especialidades AS e ON m.especialidade_id = e.id " \
"WHERE " \
"    e.nome ILIKE %s " \
"ORDER BY " \
"    m.nome;"

REMOVER_MEDICO = "" \
"DELETE FROM cadastros.medicos " \
"WHERE id = %s;"

LISTAR_TODOS_MEDICOS = "" \
"SELECT id, nome, crm, email " \
"FROM cadastros.medicos " \
"ORDER BY id;"

SELECIONAR_MEDICO_POR_CRM = "" \
"SELECT * " \
"FROM cadastros.medicos " \
"WHERE crm = %s;"


# =============================================================================
# OPERAÇÕES NA TABELA FUNCIONARIOS
# =============================================================================

INSERIR_FUNCIONARIO = "" \
"INSERT INTO cadastros.funcionarios (nome, telefone, email, salario, cargo, tipo_contrato, perfil_acesso_id) " \
"VALUES (%s, %s, %s, %s, %s, %s, %s) " \
"RETURNING id;"

ATUALIZAR_PERFIL_ACESSO_FUNCIONARIO = "" \
"UPDATE cadastros.funcionarios " \
"SET perfil_acesso_id = %s " \
"WHERE id = %s;"

PESQUISAR_FUNCIONARIO_POR_NOME = "" \
"SELECT id, nome, cargo " \
"FROM cadastros.funcionarios " \
"WHERE nome ILIKE %s;"

PESQUISAR_FUNCIONARIO_POR_TIPO_DE_CONTRATO = "" \
"SELECT " \
"    id, nome, cargo, tipo_contrato, email " \
"FROM " \
"    cadastros.funcionarios " \
"WHERE " \
"    tipo_contrato = %s " \
"ORDER BY " \
"    nome;"

REMOVER_FUNCIONARIO = "" \
"DELETE FROM cadastros.funcionarios " \
"WHERE id = %s;"

LISTAR_TODOS_FUNCIONARIOS = "" \
"SELECT id, nome, cargo, email " \
"FROM cadastros.funcionarios " \
"ORDER BY id;"

SELECIONAR_FUNCIONARIO_POR_ID = "" \
"SELECT * " \
"FROM cadastros.funcionarios " \
"WHERE id = %s;"

# =============================================================================
# OPERAÇÕES NA TABELA ESPECIALIDADES
# =============================================================================

INSERIR_ESPECIALIDADE = "" \
"INSERT INTO cadastros.especialidades (nome, especialidade_ativa) " \
"VALUES (%s, %s) " \
"RETURNING id;"

ATUALIZAR_STATUS_ESPECIALIDADE = "" \
"UPDATE cadastros.especialidades " \
"SET especialidade_ativa = %s " \
"WHERE id = %s;"

PESQUISAR_ESPECIALIDADE_POR_NOME = "" \
"SELECT id, nome, cargo " \
"FROM cadastros.especialidades " \
"WHERE nome ILIKE %s;"

VERIFICAR_MEDICOS_POR_ESPECIALIDADE = "" \
"SELECT COUNT(id) " \
"FROM cadastros.medicos " \
"WHERE especialidade_id = %s;"

# só será chamada se a verificação passar
REMOVER_ESPECIALIDADE = "" \
"DELETE FROM cadastros.especialidades " \
"WHERE id = %s;"

LISTAR_TODAS_ESPECIALIDADES = "" \
"SELECT id, nome, especialidade_ativa " \
"FROM cadastros.especialidades " \
"ORDER BY id;"

SELECIONAR_ESPECIALIDADE_POR_ID = "" \
"SELECT * " \
"FROM cadastros.especialidades " \
"WHERE id = %s;"

# =============================================================================
# OPERAÇÕES NA TABELA PERFIS_ACESSO
# =============================================================================

INSERIR_PERFIL_ACESSO = "" \
"INSERT INTO cadastros.perfis_acesso (nome, descricao) " \
"VALUES (%s, %s) " \
"RETURNING id;"

ATUALIZAR_DESCRICAO_PERFIL_ACESSO = "" \
"UPDATE cadastros.perfis_acesso " \
"SET descricao = %s " \
"WHERE id = %s;"

PESQUISAR_PERFIL_ACESSO_POR_NOME = "" \
"SELECT id, nome, descricao " \
"FROM cadastros.perfis_acesso " \
"WHERE nome ILIKE %s " \
"ORDER BY nome;"

VERIFICAR_FUNCIONARIOS_POR_PERFIL = "" \
"SELECT COUNT(id) " \
"FROM cadastros.funcionarios " \
"WHERE perfil_acesso_id = %s;"

REMOVER_PERFIL_ACESSO = "" \
"DELETE FROM cadastros.perfis_acesso " \
"WHERE id = %s;"

LISTAR_TODOS_PERFIS_ACESSO = "" \
"SELECT id, nome, descricao " \
"FROM cadastros.perfis_acesso " \
"ORDER BY id;"

SELECIONAR_PERFIL_ACESSO_POR_ID = "" \
"SELECT * " \
"FROM cadastros.perfis_acesso " \
"WHERE id = %s;"