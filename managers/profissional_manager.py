# managers/profissional_manager.py
import sql_queries as queries

class ProfissionalManager:
    def __init__(self, db):
        self.db = db

    def inserir(self, profissional):
        return self.db.execute_and_fetch_one(
            queries.INSERIR_PROFISSIONAL, profissional
        )

    def listar_todos(self):
        return self.db.fetch_query(queries.LISTAR_TODOS_PROFISSIONAIS)

    def buscar_por_id(self, profissional_id):
        return self.db.fetch_query(
            queries.SELECIONAR_PROFISSIONAL_POR_ID, (profissional_id,)
        )

    def buscar_por_nome(self, nome):
        return self.db.fetch_query(
            queries.PESQUISAR_PROFISSIONAL_POR_NOME, (f"%{nome}%",)
        )

    def atualizar_telefone(self, profissional_id, novo_telefone):
        return self.db.execute_query(
            queries.ATUALIZAR_TELEFONE_PROFISSIONAL,
            (novo_telefone, profissional_id)
        )

    def remover(self, profissional_id):
        return self.db.execute_query(
            queries.REMOVER_PROFISSIONAL, (profissional_id,)
        )
