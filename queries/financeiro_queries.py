# =============================================================================
# OPERAÇÕES NA TABELA PAGAMENTOS
# =============================================================================

INSERIR_PAGAMENTO = "" \
"INSERT INTO financeiro.pagamentos (consulta_id, valor, metodo, pago, data_pagamento) " \
"VALUES (%s, %s, %s, %s, %s) " \
"RETURNING id;"

ATUALIZAR_STATUS_PAGAMENTO = "" \
"UPDATE financeiro.pagamentos " \
"SET pago = TRUE, data_pagamento = CURRENT_TIMESTAMP " \
"WHERE id = %s;"

PESQUISAR_PAGAMENTO_POR_NOME_PACIENTE = "" \
"SELECT " \
"    pg.id, pg.valor, pg.metodo, pg.pago, p.nome AS nome_paciente, c.data AS data_consulta " \
"FROM " \
"    financeiro.pagamentos AS pg " \
"JOIN " \
"    clinico.consultas AS c ON pg.consulta_id = c.id " \
"JOIN " \
"    cadastros.pacientes AS p ON c.paciente_id = p.id " \
"WHERE " \
"    p.nome ILIKE %s " \
"ORDER BY " \
"    c.data DESC;"

REMOVER_PAGAMENTO = "" \
"DELETE FROM financeiro.pagamentos " \
"WHERE id = %s;"

LISTAR_TODOS_PAGAMENTOS = "" \
"SELECT id, consulta_id, valor, metodo, pago " \
"FROM financeiro.pagamentos " \
"ORDER BY id DESC;"

SELECIONAR_PAGAMENTO_POR_ID = "" \
"SELECT * " \
"FROM financeiro.pagamentos " \
"WHERE id = %s;"

VERIFICAR_PAGAMENTO_POR_CONSULTA = "" \
"SELECT COUNT(id) " \
"FROM financeiro.pagamentos " \
"WHERE consulta_id = %s;"