# managers/consulta_manager.py
import sql_queries as queries

class ConsultaManager:
    def __init__(self, db):
        self.db = db

    def inserir(self, consulta):
        return self.db.execute_and_fetch_one(
            queries.INSERIR_CONSULTA, consulta
        )

    def listar_todas(self):
        return self.db.fetch_query(queries.LISTAR_TODAS_CONSULTAS)

    def buscar_por_id(self, consulta_id):
        return self.db.fetch_query(
            queries.SELECIONAR_CONSULTA_POR_ID, (consulta_id,)
        )

    def atualizar_status(self, consulta_id, novo_status):
        return self.db.execute_query(
            queries.ATUALIZAR_STATUS_CONSULTA,
            (novo_status, consulta_id)
        )

    def remover(self, consulta_id):
        return self.db.execute_query(
            queries.REMOVER_CONSULTA, (consulta_id,)
        )
