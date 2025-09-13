# Classe para gerenciar a conexão e as operações

import psycopg2
from psycopg2 import sql
from db_config import DB_SETTINGS

class DatabaseManager:
    """Gerencia a conexão e as operações com o banco de dados PostgreSQL."""

    def __init__(self):
        self.conn = None

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.conn = psycopg2.connect(**DB_SETTINGS)
            print("Conexão com o banco de dados bem-sucedida!")
        except psycopg2.OperationalError as e:
            print(f"Erro ao conectar com o banco de dados: {e}")
            self.conn = None

    def disconnect(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            print("Conexão com o banco de dados fechada.")

    def execute_query(self, query, params=None):
        """Executa uma query que não retorna dados (INSERT, UPDATE, DELETE)."""
        if not self.conn:
            print("Não há conexão com o banco.")
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Erro ao executar query: {e}")
            self.conn.rollback()
            return False

    def fetch_query(self, query, params=None):
        """Executa uma query que retorna dados (SELECT)."""
        if not self.conn:
            print("Não há conexão com o banco.")
            return None

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Erro ao buscar dados: {e}")
            self.conn.rollback() 
            return None
    
    def execute_and_fetch_one(self, query, params=None):
        """Executa uma query que modifica dados e retorna o primeiro resultado (ex: RETURNING id)."""
        if not self.conn:
            print("Não há conexão com o banco.")
            return None
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchone() # Pega o primeiro (e único) resultado retornado
                self.conn.commit()      # Salva a alteração no banco
                return result
        except psycopg2.Error as e:
            print(f"Erro ao executar e buscar dados: {e}")
            self.conn.rollback() # Desfaz a alteração em caso de erro
            return None
