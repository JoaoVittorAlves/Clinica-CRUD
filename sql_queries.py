# =============================================================================
# CONSULTAS GERAIS 
# =============================================================================

DETALHES_CONSULTAS = """
    SELECT
        c.id AS consulta_id, c.data, p.nome AS nome_paciente,
        m.nome AS nome_medico, e.nome AS especialidade, c.status
    FROM
        clinico.consultas AS c
    JOIN
        cadastros.pacientes AS p ON c.paciente_id = p.id
    JOIN
        cadastros.medicos AS m ON c.medico_id = m.id
    JOIN
        cadastros.especialidades AS e ON m.especialidade_id = e.id
    ORDER BY
        c.data DESC;
"""

# =============================================================================
# OPERAÇÕES NA TABELA PACIENTES
# =============================================================================

# 1. Inserir (Create)
INSERIR_PACIENTE = "" \
"INSERT INTO cadastros.pacientes (nome, sexo, email, cpf, telefone, logradouro, numero, complemento, bairro, cidade, sigla_estado, cep) " \
"VALUES (%s, %s, %s, %s, %s) " \
"RETURNING id;"

# 2. Alterar (Update)
ATUALIZAR_TELEFONE_PACIENTE = "" \
"UPDATE cadastros.pacientes " \
"SET telefone = %s " \
"WHERE id = %s;"

# 3. Pesquisar por nome (Read/Search)
PESQUISAR_PACIENTE_POR_NOME = "" \
"SELECT id, nome, email, telefone " \
"FROM cadastros.pacientes " \
"WHERE nome ILIKE %s;"

# 4. Remover (Delete)
REMOVER_PACIENTE = "" \
"DELETE FROM cadastros.pacientes " \
"WHERE id = %s;"

# 5. Listar todos (Read/List All)
LISTAR_TODOS_PACIENTES = "" \
"SELECT id, nome, email, telefone " \
"FROM cadastros.pacientes " \
"ORDER BY id;"

# 6. Exibir um (Read/Fetch One)
SELECIONAR_PACIENTE_POR_ID = "" \
"SELECT id, nome, email, telefone, cidade, sigla_estado " \
"FROM cadastros.pacientes " \
"WHERE id = %s;"