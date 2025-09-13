# Sistema de Gestão de Clínica (CRUD Básico)

Este projeto é uma aplicação desenvolvida em **Python** para gerenciar as operações básicas (CRUD - Create, Read, Update, Delete) de uma clínica.  
O sistema interage com um banco de dados **PostgreSQL** para persistir os dados.

O foco do projeto é demonstrar uma arquitetura com separação de responsabilidades entre a lógica da aplicação (Python) e o armazenamento de dados (SQL).

---

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3  
- **Banco de Dados:** PostgreSQL  
- **Driver de Conexão:** psycopg2  

---

## 📌 Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados e em execução na sua máquina:

- **Python 3.8** ou superior  
- **PostgreSQL** (o serviço do banco deve estar ativo)  

---

## ⚙️ Passo a Passo da Instalação e Execução

### 1. Obtenha o Código-Fonte
Clone este repositório ou baixe e descompacte os arquivos do projeto em um diretório de sua preferência.

### 2. Configure o Banco de Dados PostgreSQL
Crie o banco de dados que será utilizado pela aplicação:

1. Abra o seu cliente SQL preferido (**psql**, **DBeaver**, **pgAdmin**).  
2. Execute o comando SQL:  
   ```sql
   CREATE DATABASE projetoBD;

### 3. Configure o Ambiente Virtual e Instale as Dependências
1. Navegue até a pasta raiz do projeto no terminal.
2. Crie o ambiente virtual:
      ```bash
   python -m venv venv
3. Ative o ambiente virtual:
    - **Windows (PowerShell):**
      ```bash
       .\venv\Scripts\Activate.ps1
    - **Linux/macOS:**
      ```bash
       source venv/bin/activate
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   
### 4. Configure a Conexão com o Banco
Edite o arquivo ```db_config.py``` e altere os valores para corresponder às suas credenciais do PostgreSQL.

### 5. Crie a Estrutura do Banco (Tabelas e Dados Iniciais)
1. Certifique-se de que o ambiente virtual está ativado.
2. Na raiz do projeto, execute:
      ```bash
   psql -U seu_usuario_aqui -d clinica_db -f schema_clinica.sql

### 6. Execute a Aplicação
   ```psql -U seu_usuario_aqui -d clinica_db -f schema_clinica.sql```

---

## 📋 Funcionalidades

- A aplicação de console permite gerenciar a tabela de Pacientes, oferecendo as seguintes operações:

- Listar todos os pacientes cadastrados

- Exibir detalhes de um paciente específico pelo ID

- Inserir um novo paciente

- Alterar o telefone de um paciente existente

- Pesquisar pacientes pelo nome

- Remover um paciente (com confirmação)
