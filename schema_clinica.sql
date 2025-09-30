-- =============================================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS DA CLÍNICA
-- Descrição: Cria a estrutura de schemas, tabelas, relacionamentos e
--            insere dados de exemplo para o sistema de gerenciamento da clínica.
-- =============================================================================

-- Limpa o ambiente removendo schemas existentes
DROP SCHEMA IF EXISTS financeiro CASCADE;
DROP SCHEMA IF EXISTS clinico CASCADE;
DROP SCHEMA IF EXISTS cadastros CASCADE;
DROP SCHEMA IF EXISTS vendas CASCADE;

-- 1. CRIAÇÃO DOS SCHEMAS 

CREATE SCHEMA cadastros;
COMMENT ON SCHEMA cadastros IS 'Schema para tabelas de dados cadastrais, como pacientes e profissionais.';

CREATE SCHEMA clinico;
COMMENT ON SCHEMA clinico IS 'Schema para tabelas relacionadas à operação clínica, como consultas e receitas.';

CREATE SCHEMA financeiro;
COMMENT ON SCHEMA financeiro IS 'Schema para tabelas relacionadas a pagamentos e faturamento.';

CREATE SCHEMA vendas;
COMMENT ON SCHEMA vendas IS 'Schema para tabelas do módulo de vendas, como produtos, categorias, estoque, vendas, itens e pedidos.';


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
    telefone VARCHAR(20) UNIQUE,
    logradouro VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    sigla_estado CHAR(2),
    cep VARCHAR(9)
);

ALTER TABLE cadastros.pacientes
    ADD COLUMN IF NOT EXISTS torce_flamengo BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS assiste_one_piece BOOLEAN DEFAULT FALSE;
    ADD COLUMN IF NOT EXISTS nasceu_sousa BOOLEAN DEFAULT FALSE;


-- Tabela de Consultas (Schema: clinico)
CREATE TABLE clinico.consultas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES cadastros.pacientes(id) ON DELETE CASCADE,
    medico_id INTEGER NOT NULL REFERENCES cadastros.medicos(id) ON DELETE RESTRICT,
    funcionario_id INTEGER REFERENCES cadastros.funcionarios(id) ON DELETE SET NULL,
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
    consulta_id INTEGER NOT NULL REFERENCES clinico.consultas(id) ON DELETE RESTRICT,
    valor NUMERIC(10,2) NOT NULL,
    metodo VARCHAR(30) CHECK (metodo IN ('Dinheiro', 'Cartão', 'Transferência', 'Seguro')),
    pago BOOLEAN DEFAULT FALSE,
    data_pagamento TIMESTAMP WITHOUT TIME ZONE
);

-- Tabela de cartegorias (schema: vendas)
CREATE TABLE vendas.categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- Produtos (schema: vendas)
CREATE TABLE vendas.produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    preco NUMERIC(12,2) NOT NULL CHECK (preco >= 0),
    categoria_id INTEGER REFERENCES vendas.categorias(id) ON DELETE SET NULL,
    fabricado_em_mari BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE
);

-- Estoque (separado para permitir controle isolado, schema: vendas)
CREATE TABLE vendas.estoque (
    produto_id INTEGER PRIMARY KEY REFERENCES vendas.produtos(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0)
);

-- Vendas (schema: vendas)
CREATE TABLE vendas.vendas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES cadastros.pacientes(id) ON DELETE RESTRICT,
    vendedor_id INTEGER NOT NULL REFERENCES cadastros.funcionarios(id) ON DELETE RESTRICT,
    data TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_bruto NUMERIC(12,2) NOT NULL CHECK (total_bruto >= 0),
    desconto_aplicado NUMERIC(12,2) NOT NULL CHECK (desconto_aplicado >= 0),
    total_liquido NUMERIC(12,2) NOT NULL CHECK (total_liquido >= 0),
    forma_pagamento VARCHAR(30) NOT NULL CHECK (forma_pagamento IN ('Dinheiro','Cartão','Boleto','PIX','Berries')),
    status_pagamento VARCHAR(30) NOT NULL DEFAULT 'Pendente' CHECK (status_pagamento IN ('Pendente','Confirmado','Falhado'))
);

-- Itens da Venda (schema: vendas)
CREATE TABLE vendas.itens_venda (
    id SERIAL PRIMARY KEY,
    venda_id INTEGER NOT NULL REFERENCES vendas.vendas(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES vendas.produtos(id) ON DELETE RESTRICT,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(12,2) NOT NULL CHECK (preco_unitario >= 0)
);







-- 3. INSERÇÃO DE DADOS DE EXEMPLO

-- Perfis de Acesso
INSERT INTO cadastros.perfis_acesso (nome, descricao) VALUES
('Administrador', 'Acesso total ao sistema.'),
('Recepção', 'Acesso a agendamentos e cadastros de pacientes.'),
('Faturamento', 'Acesso a relatórios e gestão de pagamentos.'),
('Corpo Técnico', 'Acesso a prontuários e agendamentos clínicos.');

-- Especialidades da Clínica
INSERT INTO cadastros.especialidades (nome) VALUES
('Cardiologia'),
('Dermatologia'),
('Ortopedia'),
('Medicina Esportiva'),
('Fisioterapia'),
('Nutrição Esportiva');

-- Funcionários da Clínica
INSERT INTO cadastros.funcionarios (nome, email, salario, cargo, tipo_contrato, perfil_acesso_id, cidade, sigla_estado) VALUES
('Taylor Swift', 'taylor.swift@clinica.com', 2500.00, 'Recepcionista', 'CLT', 2, 'São Paulo', 'SP'),
('Harry Styles', 'harrystyles@clinica.com', 8500.00, 'Diretor Administrativo', 'CLT', 1, 'Recife', 'PE'),
('Márcio Tannure', 'marcio.tannure@clinica.com', 12000.00, 'Fisioterapeuta Chefe', 'PJ', 4, 'Rio de Janeiro', 'RJ'),
('Georgiana Maria', 'georgiana@hotmail.com', 30000.00, 'Diretora de Markting Digital', 'CLT', 1, 'João Pessoa', 'PB');

-- Médicos da Clínica
INSERT INTO cadastros.medicos (nome, email, crm, especialidade_id, cidade, sigla_estado) VALUES
('Dr. Tite', 'tite@clinica.com', 'CRM-RJ 1981', 4, 'Rio de Janeiro', 'RJ'),
('Dr. Zico', 'zico@clinica.com', 'CRM-RJ 1953', 3, 'Rio de Janeiro', 'RJ'),
('Dra. Kiara Maria Chihuahua', 'kiaramariachihuahua@clinica.com', 'CRM-RJ 2019', 6, 'João Pessoa', 'PB'),
('Dr. Joao Vittor de Araujo', 'joaovittor@gmail.com', 'CRM-PB 2020', 1, 'João Pessoa', 'PB');

-- Pacientes
INSERT INTO cadastros.pacientes (nome, sexo, email, cpf, telefone, cidade, sigla_estado) VALUES
('Gabriel Barbosa Almeida', 'M', 'gabigol@flamengo.com', '11111111111', '21999999999', 'Rio de Janeiro', 'RJ'),
('Giorgian De Arrascaeta', 'M', 'arrasca@flamengo.com', '22222222222', '21988888888', 'Rio de Janeiro', 'RJ'),
('Bruno Henrique Pinto', 'M', 'bh27@flamengo.com', '33333333333', '21977777777', 'Rio de Janeiro', 'RJ'),
('Pedro Guilherme', 'M', 'pedro9@flamengo.com', '44444444444', '21966666666', 'Cabo Frio', 'RJ');

-- Consultas Agendadas
-- As consultas são agendadas pela recepcionista (funcionario_id = 1)
INSERT INTO clinico.consultas (paciente_id, medico_id, funcionario_id, data, motivo, diagnostico, status) VALUES
(1, 1, 1, '2025-09-10 09:00:00', 'Avaliação de performance pré-temporada', 'Condicionamento físico excelente', 'Realizada'),
(2, 2, 1, '2025-09-12 11:30:00', 'Pancada no joelho esquerdo durante treino', 'Trauma leve, sem lesão ligamentar', 'Realizada'),
(3, 1, 1, '2025-10-15 15:00:00', 'Exames de rotina', NULL, 'Agendada'),
(2, 3, 1, '2025-10-18 10:00:00', 'Consulta com nutricionista', 'Planejamento de dieta para ganho de massa', 'Agendada');

-- Receitas geradas nas consultas
INSERT INTO clinico.receitas (consulta_id, medicamento, dosagem, instrucoes) VALUES
(1, 'Suplemento Vitamínico C e Zinco', '1 cápsula', 'Tomar 1 cápsula por dia, após o café da manhã, por 30 dias.'),
(2, 'Gelo e repouso', '20 minutos', 'Aplicar compressa de gelo no local, 3 vezes ao dia.'),
(4, 'Dieta Hipercalórica e Proteica', 'N/A', 'Seguir o plano alimentar entregue em anexo.');

-- Pagamentos das consultas realizadas
INSERT INTO financeiro.pagamentos (consulta_id, valor, metodo, pago, data_pagamento) VALUES
(1, 550.00, 'Seguro', TRUE, '2025-10-10 10:00:00'),
(2, 450.00, 'Transferência', TRUE, '2025-10-12 12:00:00'),
(4, 350.00, 'Cartão', TRUE, '2025-10-18 11:00:00');