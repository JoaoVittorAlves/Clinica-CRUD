-- =============================================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS DA CLÍNICA
-- Descrição: Cria a estrutura de schemas, tabelas, relacionamentos e
--            insere dados de exemplo para o sistema de gerenciamento da clínica.
-- =============================================================================

-- Limpa o ambiente removendo schemas existentes
DROP SCHEMA IF EXISTS financeiro CASCADE;
DROP SCHEMA IF EXISTS clinico CASCADE;
DROP SCHEMA IF EXISTS cadastros CASCADE;

-- 1. CRIAÇÃO DOS SCHEMAS 

CREATE SCHEMA cadastros;
COMMENT ON SCHEMA cadastros IS 'Schema para tabelas de dados cadastrais, como pacientes e profissionais.';

CREATE SCHEMA clinico;
COMMENT ON SCHEMA clinico IS 'Schema para tabelas relacionadas à operação clínica, como consultas e receitas.';

CREATE SCHEMA financeiro;
COMMENT ON SCHEMA financeiro IS 'Schema para tabelas relacionadas a pagamentos e faturamento.';


-- 2. CRIAÇÃO DAS TABELAS

-- Tabela de Perfis de Acesso (Schema: cadastros)
CREATE TABLE cadastros.perfis_acesso (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT
);

COMMENT ON TABLE cadastros.perfis_acesso IS 'Armazena os perfis de acesso do sistema, que definem permissões.';
COMMENT ON COLUMN cadastros.perfis_acesso.nome IS 'Nome único do perfil (Ex: Administrador, Recepção).';
COMMENT ON COLUMN cadastros.perfis_acesso.descricao IS 'Descrição detalhada das permissões do perfil.';

-- Tabela de Funcionários (Schema: cadastros)
CREATE TABLE cadastros.funcionarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) UNIQUE,
    email VARCHAR(120) UNIQUE,
    salario NUMERIC(10, 2) CHECK (salario >= 0),
    data_admissao DATE NOT NULL DEFAULT CURRENT_DATE,
    cargo VARCHAR(100) NOT NULL,
    tipo_contrato VARCHAR(20) NOT NULL CHECK (tipo_contrato IN ('CLT', 'PJ', 'Estágio')),
    perfil_acesso_id INTEGER NOT NULL REFERENCES cadastros.perfis_acesso(id) ON DELETE RESTRICT,
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    sigla_estado CHAR(2),
    cep VARCHAR(9)
);

COMMENT ON TABLE cadastros.funcionarios IS 'Armazena dados dos funcionários não-médicos da clínica.';
COMMENT ON COLUMN cadastros.funcionarios.cargo IS 'O cargo ocupado pelo funcionário (Ex: Recepcionista, Enfermeiro(a)).';
COMMENT ON COLUMN cadastros.funcionarios.tipo_contrato IS 'Tipo de vínculo empregatício (CLT, PJ, Estágio).';
COMMENT ON COLUMN cadastros.funcionarios.perfil_acesso_id IS 'Chave estrangeira que define o nível de permissão do funcionário no sistema.';

-- Tabela de Especialidades (Schema: cadastros)
CREATE TABLE cadastros.especialidades (
    id SERIAL PRIMARY KEY, -- Id único da especialidade que é preenchido automaticamente com um número sequencial
    nome VARCHAR(100) NOT NULL UNIQUE,
    especialidade_ativa BOOLEAN NOT NULL DEFAULT TRUE -- Indica se a especialidade está ativa e disponível para agendamentos ou não
);

COMMENT ON COLUMN cadastros.especialidades.especialidade_ativa
IS 'Indica se a especialidade está ativa (TRUE) ou inativa (FALSE) para novos agendamentos.';

-- Tabela de Médicos (Schema: cadastros)
CREATE TABLE cadastros.medicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) UNIQUE,
    email VARCHAR(120) UNIQUE,
    crm VARCHAR(20) UNIQUE,
    salario NUMERIC(10,2),
    data_admissao DATE NOT NULL DEFAULT CURRENT_DATE,
    especialidade_id INTEGER REFERENCES cadastros.especialidades(id),
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    sigla_estado CHAR(2),
    cep VARCHAR(9)
);

-- Tabela de Pacientes (Schema: cadastros)
CREATE TABLE cadastros.pacientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sexo CHAR(1) CHECK (sexo IN ('M', 'F', 'O')),
    email VARCHAR(120) UNIQUE,
    cpf VARCHAR(11) UNIQUE,
    data_registo TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    telefone VARCHAR(9) UNIQUE,
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    sigla_estado CHAR(2),
    cep VARCHAR(9)
);

-- Tabela de Consultas (Schema: clinico)
CREATE TABLE clinico.consultas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES cadastros.pacientes(id) ON DELETE CASCADE,
    medico_id INTEGER NOT NULL REFERENCES cadastros.medicos(id) ON DELETE SET NULL,
    data TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    motivo TEXT,
    diagnostico TEXT,
    status VARCHAR(20) DEFAULT 'Agendada' CHECK (status IN ('Agendada', 'Realizada', 'Cancelada'))
);

-- Tabela de Receitas (Schema: clinico)
CREATE TABLE clinico.receitas (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES clinico.consultas(id) ON DELETE CASCADE,
    medicamento VARCHAR(200) NOT NULL,
    dosagem VARCHAR(100),
    instrucoes TEXT
);

-- Tabela de Pagamentos (Schema: financeiro)
CREATE TABLE financeiro.pagamentos (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES clinico.consultas(id) ON DELETE CASCADE,
    valor NUMERIC(10,2) NOT NULL,
    metodo VARCHAR(30) CHECK (metodo IN ('Dinheiro', 'Cartão', 'Transferência', 'Seguro')),
    pago BOOLEAN DEFAULT FALSE,
    data_pagamento TIMESTAMP WITHOUT TIME ZONE
);


-- 3. INSERÇÃO DE DADOS DE EXEMPLO 

INSERT INTO cadastros.perfis_acesso (nome, descricao) VALUES
('Administrador', 'Acesso total a todas as funcionalidades do sistema.'),
('Recepção', 'Acesso ao agendamento, cadastro de pacientes e pagamentos.'),
('Faturamento', 'Acesso apenas aos módulos financeiros.');

INSERT INTO cadastros.funcionarios (nome, email, salario, cargo, tipo_contrato, perfil_acesso_id, cidade, sigla_estado) VALUES
('Julia Mendes', 'julia.mendes@clinica.com', 2500.00, 'Recepcionista', 'CLT', 2, 'João Pessoa', 'PB'),
('Marcos Batista', 'marcos.batista@clinica.com', 4500.00, 'Administrador Financeiro', 'CLT', 1, 'Cabedelo', 'PB');

INSERT INTO cadastros.especialidades (nome) VALUES
('Cardiologia'),
('Dermatologia'),
('Ortopedia');

INSERT INTO cadastros.medicos (nome, email, crm, especialidade_id, cidade, sigla_estado, cep) VALUES
('Dr. Carlos Andrade', 'carlos.andrade@med.com', 'CRM-SP 12345', 1, 'São Paulo', 'SP', '01000-000'),
('Dra. Ana Beatriz', 'ana.beatriz@med.com', 'CRM-PB 54321', 2, 'João Pessoa', 'PB', '58000-000');

INSERT INTO cadastros.pacientes (nome, sexo, email, cpf, telefone, cidade, sigla_estado) VALUES
('João da Silva', 'M', 'joao.silva@email.com', '11122233344', '988776655', 'João Pessoa', 'PB'),
('Maria Oliveira', 'F', 'maria.oliveira@email.com', '55566677788', '999887766', 'Bayeux', 'PB'),
('Pedro Souza', 'M', 'pedro.souza@email.com', '99988877766', '977665544', 'Santa Rita', 'PB');

INSERT INTO clinico.consultas (paciente_id, medico_id, data, motivo, diagnostico, status) VALUES
(1, 2, '2025-08-20 10:00:00', 'Check-up dermatológico', 'Sinais de exposição solar excessiva', 'Realizada'),
(2, 2, '2025-08-22 14:30:00', 'Manchas na pele', 'Dermatite de contato', 'Realizada'),
(3, 1, '2025-11-05 09:00:00', 'Check-up cardiológico anual', NULL, 'Agendada');

INSERT INTO clinico.receitas (consulta_id, medicamento, dosagem, instrucoes) VALUES
(1, 'Protetor Solar FPS 60', 'N/A', 'Aplicar no rosto e áreas expostas diariamente'),
(2, 'Hidrocortisona (pomada)', '1%', 'Aplicar na área afetada 2 vezes ao dia');

INSERT INTO financeiro.pagamentos (consulta_id, valor, metodo, pago, data_pagamento) VALUES
(1, 350.00, 'Cartão', TRUE, '2025-10-20 11:00:00'),
(2, 300.00, 'Seguro', TRUE, '2025-10-22 15:00:00');