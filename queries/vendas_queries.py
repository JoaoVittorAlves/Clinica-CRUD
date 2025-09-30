# queries/vendas_queries.py

LISTAR_TODOS_PRODUTOS = "SELECT p.id, p.nome, p.descricao, p.preco, c.nome AS categoria, p.fabricado_em_mari, e.quantidade FROM vendas.produtos p LEFT JOIN vendas.categorias c ON p.categoria_id = c.id LEFT JOIN vendas.estoque e ON p.id = e.produto_id WHERE p.ativo = TRUE ORDER BY p.nome;"

BUSCAR_PRODUTOS_POR_NOME = "SELECT p.id, p.nome, p.preco, c.nome AS categoria, e.quantidade FROM vendas.produtos p LEFT JOIN vendas.categorias c ON p.categoria_id = c.id LEFT JOIN vendas.estoque e ON p.id = e.produto_id WHERE lower(p.nome) LIKE lower(%s) AND p.ativo = TRUE ORDER BY p.nome;"

BUSCAR_PRODUTOS_POR_FAIXA_PRECO = "SELECT p.id, p.nome, p.preco, c.nome AS categoria, e.quantidade FROM vendas.produtos p LEFT JOIN vendas.categorias c ON p.categoria_id = c.id LEFT JOIN vendas.estoque e ON p.id = e.produto_id WHERE p.preco BETWEEN %s AND %s AND p.ativo = TRUE ORDER BY p.preco;"

BUSCAR_PRODUTOS_POR_CATEGORIA = "SELECT p.id, p.nome, p.preco, e.quantidade FROM vendas.produtos p JOIN vendas.categorias c ON p.categoria_id = c.id LEFT JOIN vendas.estoque e ON p.id = e.produto_id WHERE c.nome = %s AND p.ativo = TRUE;"

BUSCAR_PRODUTOS_FAB_MARI = "SELECT p.id, p.nome, p.preco, e.quantidade FROM vendas.produtos p LEFT JOIN vendas.estoque e ON p.id = e.produto_id WHERE p.fabricado_em_mari = TRUE AND p.ativo = TRUE;"

BUSCAR_PRODUTOS_ESTOQUE_BAIXO = "SELECT p.id, p.nome, p.preco, e.quantidade FROM vendas.produtos p JOIN vendas.estoque e ON p.id = e.produto_id WHERE e.quantidade < 5 AND p.ativo = TRUE;"

LISTAR_CATEGORIAS = "SELECT id, nome FROM vendas.categorias ORDER BY nome;"

# chamada a função (usar json.dumps para items em Python)
CHAMAR_EFETIVAR_COMPRA = "SELECT * FROM vendas.efetivar_compra(%s, %s, %s, %s::jsonb, %s);"

# Relatório mensal por vendedor (usando a view criada)
REL_VENDAS_POR_VENDEDOR_MES = "SELECT * FROM vendas.vendas_por_vendedor_mes ORDER BY mes DESC;"
