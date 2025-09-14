# managers/paciente_manager.py
import sql_queries as queries

class PacienteManager:
    def __init__(self, db):
        self.db = db

    def inserir(self, paciente):
        """Insere um novo paciente."""
        return self.db.execute_and_fetch_one(
            queries.INSERIR_PACIENTE, paciente
        )

    def listar_todos(self):
        """Lista todos os pacientes."""
        return self.db.fetch_query(queries.LISTAR_TODOS_PACIENTES)

    def buscar_por_id(self, paciente_id):
        """Retorna paciente pelo ID."""
        return self.db.fetch_query(
            queries.SELECIONAR_PACIENTE_POR_ID, (paciente_id,)
        )

    def buscar_por_nome(self, nome):
        """Pesquisa pacientes pelo nome."""
        return self.db.fetch_query(
            queries.PESQUISAR_PACIENTE_POR_NOME, (f"%{nome}%",)
        )

    def atualizar_telefone(self, paciente_id, novo_telefone):
        """Atualiza telefone do paciente."""
        return self.db.execute_query(
            queries.ATUALIZAR_TELEFONE_PACIENTE,
            (novo_telefone, paciente_id)
        )

    def remover(self, paciente_id):
        """Remove paciente pelo ID."""
        return self.db.execute_query(
            queries.REMOVER_PACIENTE, (paciente_id,)
        )
