# =============================================================================
# CONSULTAS GERAIS 
# =============================================================================
# Queries mais complexas que unem várias tabelas para gerar relatórios.


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
# OPERAÇÕES NA TABELA CONSULTAS
# =============================================================================

INSERIR_CONSULTA = "" \
"INSERT INTO clinico.consultas (paciente_id, medico_id, data, motivo, status) " \
"VALUES (%s, %s, %s, %s, %s) " \
"RETURNING id;"

ATUALIZAR_CONSULTA = "" \
"UPDATE clinico.consultas " \
"SET status = %s, diagnostico = %s " \
"WHERE id = %s;"

PESQUISAR_CONSULTA_POR_NOME_PACIENTE = "" \
"SELECT " \
"    c.id, c.data, c.status, p.nome AS nome_paciente, m.nome AS nome_medico " \
"FROM " \
"    clinico.consultas AS c " \
"JOIN " \
"    cadastros.pacientes AS p ON c.paciente_id = p.id " \
"JOIN " \
"    cadastros.medicos AS m ON c.medico_id = m.id " \
"WHERE " \
"    p.nome ILIKE %s " \
"ORDER BY " \
"    c.data DESC;"

REMOVER_CONSULTA = "" \
"DELETE FROM clinico.consultas " \
"WHERE id = %s;"

LISTAR_TODAS_CONSULTAS = "" \
"SELECT id, data, status, paciente_id, medico_id " \
"FROM clinico.consultas " \
"ORDER BY data DESC;"

SELECIONAR_CONSULTA_POR_ID = "" \
"SELECT * " \
"FROM clinico.consultas " \
"WHERE id = %s;"

# =============================================================================
# OPERAÇÕES NA TABELA RECEITAS
# =============================================================================

INSERIR_RECEITA = "" \
"INSERT INTO clinico.receitas (consulta_id, medicamento, dosagem, instrucoes) " \
"VALUES (%s, %s, %s, %s) " \
"RETURNING id;"

ATUALIZAR_RECEITA = "" \
"UPDATE clinico.receitas " \
"SET medicamento = %s, dosagem = %s, instrucoes = %s " \
"WHERE id = %s;"

PESQUISAR_RECEITA_POR_PACIENTE = "" \
"SELECT " \
"    p.nome AS nome_paciente, " \
"    r.medicamento, " \
"    r.dosagem, " \
"    c.data AS data_da_consulta " \
"FROM " \
"    clinico.receitas AS r " \
"JOIN " \
"    clinico.consultas AS c ON r.consulta_id = c.id " \
"JOIN " \
"    cadastros.pacientes AS p ON c.paciente_id = p.id " \
"WHERE " \
"    p.nome ILIKE %s " \
"ORDER BY " \
"    c.data DESC;"

REMOVER_RECEITA = "" \
"DELETE FROM clinico.receitas " \
"WHERE id = %s;"

LISTAR_TODAS_RECEITAS = "" \
"SELECT id, consulta_id, medicamento " \
"FROM clinico.receitas " \
"ORDER BY id;"

SELECIONAR_RECEITA_POR_ID = "" \
"SELECT * " \
"FROM clinico.receitas " \
"WHERE id = %s;"