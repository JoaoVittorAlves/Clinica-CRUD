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
    ADD COLUMN IF NOT EXISTS torce_flamengo BOOLEAN DEFAULT FALSE;

ALTER TABLE cadastros.pacientes
    ADD COLUMN IF NOT EXISTS assiste_one_piece BOOLEAN DEFAULT FALSE;

ALTER TABLE cadastros.pacientes
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

-- Tabela de Categorias (schema: vendas)
CREATE TABLE vendas.categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- Tabela de Produtos (schema: vendas)
CREATE TABLE vendas.produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    preco NUMERIC(12,2) NOT NULL CHECK (preco >= 0),
    categoria_id INTEGER REFERENCES vendas.categorias(id) ON DELETE SET NULL,
    fabricado_em_mari BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE
);

-- Tabela de Estoque (separado para permitir controle isolado, schema: vendas)
CREATE TABLE vendas.estoque (
    produto_id INTEGER PRIMARY KEY REFERENCES vendas.produtos(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0)
);

-- Tabela de Vendas (schema: vendas)
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

-- Tabela de Itens da Venda (schema: vendas)
CREATE TABLE vendas.itens_venda (
    id SERIAL PRIMARY KEY,
    venda_id INTEGER NOT NULL REFERENCES vendas.vendas(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES vendas.produtos(id) ON DELETE RESTRICT,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(12,2) NOT NULL CHECK (preco_unitario >= 0)
);

-- === INSERÇÃO DE PRODUTOS DE EXEMPLO ===
INSERT INTO vendas.produtos (nome, preco, categoria_id) VALUES
('Produto Exemplo 1', 50.00, NULL),
('Produto Exemplo 2', 30.00, NULL);

-- 3.REGRA DE NEGÓCIO

-- 3. REGRA DE NEGÓCIO

-- Função para efetivar compra e retornar todas as vendas do cliente
CREATE OR REPLACE FUNCTION vendas.efetivar_compra(
    p_cliente_id INTEGER,
    p_vendedor_id INTEGER,
    p_forma_pagamento VARCHAR,
    p_itens JSONB,
    p_status_pagamento VARCHAR DEFAULT 'Pendente'
)
RETURNS TABLE(
    venda_id INTEGER,
    data_venda TIMESTAMP,
    total_bruto NUMERIC,
    desconto_aplicado NUMERIC,
    total_liquido NUMERIC,
    forma_pagamento VARCHAR,
    status_pagamento VARCHAR
) AS $$
DECLARE
    v_total_bruto NUMERIC := 0;
    v_desconto NUMERIC := 0;
    v_total_liquido NUMERIC := 0;
    v_venda_id INTEGER;
    v_cliente RECORD;
    v_item RECORD;
    v_status_pagamento_local VARCHAR := p_status_pagamento;
BEGIN
    -- Verifica se cliente existe
    SELECT * INTO v_cliente FROM cadastros.pacientes WHERE id = p_cliente_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cliente não encontrado.';
    END IF;

    -- Verifica se vendedor existe
    IF NOT EXISTS (SELECT 1 FROM cadastros.funcionarios WHERE id = p_vendedor_id) THEN
        RAISE EXCEPTION 'Vendedor não encontrado.';
    END IF;

    -- Verifica se a lista de itens não está vazia
    IF jsonb_typeof(p_itens) <> 'array' OR jsonb_array_length(p_itens) = 0 THEN
        RAISE EXCEPTION 'Uma venda deve ter pelo menos 1 item.';
    END IF;

    -- Calcula total bruto
    FOR v_item IN 
        SELECT * FROM jsonb_to_recordset(p_itens) AS (produto_id INTEGER, quantidade INTEGER, preco_unitario NUMERIC) 
    LOOP
        v_total_bruto := v_total_bruto + (v_item.quantidade * v_item.preco_unitario);
    END LOOP;

    -- Regra de desconto: Flamengo, One Piece, Sousa
    IF v_cliente.torce_flamengo OR v_cliente.assiste_one_piece OR v_cliente.nasceu_sousa THEN
        v_desconto := v_total_bruto * 0.10; -- 10% de desconto
    END IF;

    v_total_liquido := v_total_bruto - v_desconto;

    -- Status de pagamento para formas específicas
    IF p_forma_pagamento IN ('Cartão', 'Boleto', 'PIX', 'Berries') THEN
        v_status_pagamento_local := 'Pendente';
    ELSE
        v_status_pagamento_local := 'Confirmado';
    END IF;

    -- Cria venda
    INSERT INTO vendas.vendas (
        cliente_id, vendedor_id, data, total_bruto, desconto_aplicado, total_liquido, forma_pagamento, status_pagamento
    )
    VALUES (
        p_cliente_id, p_vendedor_id, NOW(), v_total_bruto, v_desconto, v_total_liquido, p_forma_pagamento, v_status_pagamento_local
    )
    RETURNING id INTO v_venda_id;

    -- Insere itens da venda
    FOR v_item IN 
        SELECT * FROM jsonb_to_recordset(p_itens) AS (produto_id INTEGER, quantidade INTEGER, preco_unitario NUMERIC) 
    LOOP
        INSERT INTO vendas.itens_venda (venda_id, produto_id, quantidade, preco_unitario)
        VALUES (v_venda_id, v_item.produto_id, v_item.quantidade, v_item.preco_unitario);
    END LOOP;

    -- Retorna todas as vendas do cliente (com dados resumidos)
    RETURN QUERY
    SELECT 
        v.id,
        v.data,
        v.total_bruto,
        v.desconto_aplicado,
        v.total_liquido,
        v.forma_pagamento,
        v.status_pagamento
    FROM vendas.vendas v
    WHERE v.cliente_id = p_cliente_id
    ORDER BY v.data DESC;

END;
$$ LANGUAGE plpgsql;


-- ==========================================
-- Função para consultar todas as vendas de um cliente com itens detalhados
CREATE OR REPLACE FUNCTION vendas.consultar_vendas_cliente(
    p_cliente_id INTEGER
)
RETURNS TABLE(
    venda_id INTEGER,
    data_venda TIMESTAMP,
    total_bruto NUMERIC,
    desconto_aplicado NUMERIC,
    total_liquido NUMERIC,
    forma_pagamento VARCHAR,
    status_pagamento VARCHAR,
    itens JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.id AS venda_id,
        v.data AS data_venda,
        v.total_bruto,
        v.desconto_aplicado,
        v.total_liquido,
        v.forma_pagamento,
        v.status_pagamento,
        (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'produto_id', iv.produto_id,
                    'nome_produto', p.nome,
                    'quantidade', iv.quantidade,
                    'preco_unitario', iv.preco_unitario
                )
            )
            FROM vendas.itens_venda iv
            JOIN vendas.produtos p ON p.id = iv.produto_id
            WHERE iv.venda_id = v.id
        ) AS itens
    FROM vendas.vendas v
    WHERE v.cliente_id = p_cliente_id
    ORDER BY v.data DESC;
END;
$$ LANGUAGE plpgsql;



-- 4. INSERÇÃO DE DADOS DE EXEMPLO

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

-- Teste da função efetivar_compra
SELECT * FROM vendas.efetivar_compra(
    1, -- cliente_id
    2, -- vendedor_id
    'Cartão', -- forma de pagamento
    '[{"produto_id":1,"quantidade":2,"preco_unitario":50.00}]'::jsonb -- itens
);

-- === 5. VIEWS E STORED PROCEDURES ===

-- View para o relatório mensal de vendas por vendedor
CREATE OR REPLACE VIEW vendas.vendas_por_vendedor_mes AS
SELECT
    date_trunc('month', v.data)::date AS mes,
    f.nome AS vendedor,
    COUNT(v.id) AS total_vendas,
    SUM(v.total_liquido) AS valor_total_vendido
FROM
    vendas.vendas v
JOIN
    cadastros.funcionarios f ON v.vendedor_id = f.id
GROUP BY
    mes, vendedor
ORDER BY
    mes DESC, valor_total_vendido DESC;


-- Stored Procedure para efetivar uma compra
CREATE OR REPLACE FUNCTION vendas.efetivar_compra(
    p_cliente_id INTEGER,
    p_vendedor_id INTEGER,
    p_forma_pagamento VARCHAR,
    p_itens JSONB,
    p_status_pagamento VARCHAR
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    item RECORD;
    estoque_atual INTEGER;
    total_bruto_venda NUMERIC(12,2) := 0;
    desconto_venda NUMERIC(12,2) := 0;
    total_liquido_venda NUMERIC(12,2);
    nova_venda_id INTEGER;
    cliente_tem_desconto BOOLEAN := FALSE;
BEGIN
    SELECT (torce_flamengo OR assiste_one_piece OR nasceu_sousa) INTO cliente_tem_desconto
    FROM cadastros.pacientes WHERE id = p_cliente_id;

    FOR item IN SELECT * FROM jsonb_to_recordset(p_itens) AS x(produto_id INTEGER, quantidade INTEGER, preco_unitario NUMERIC)
    LOOP
        SELECT quantidade INTO estoque_atual FROM vendas.estoque WHERE produto_id = item.produto_id FOR UPDATE;
        
        IF estoque_atual IS NULL OR estoque_atual < item.quantidade THEN
            RAISE EXCEPTION 'Produto ID % sem estoque suficiente. Disponível: %, Solicitado: %', item.produto_id, estoque_atual, item.quantidade;
        END IF;

        total_bruto_venda := total_bruto_venda + (item.quantidade * item.preco_unitario);
    END LOOP;

    IF cliente_tem_desconto THEN
        desconto_venda := total_bruto_venda * 0.10;
    END IF;
    total_liquido_venda := total_bruto_venda - desconto_venda;

    INSERT INTO vendas.vendas (cliente_id, vendedor_id, data, total_bruto, desconto_aplicado, total_liquido, forma_pagamento, status_pagamento)
    VALUES (p_cliente_id, p_vendedor_id, CURRENT_TIMESTAMP, total_bruto_venda, desconto_venda, total_liquido_venda, p_forma_pagamento, p_status_pagamento)
    RETURNING id INTO nova_venda_id;

    FOR item IN SELECT * FROM jsonb_to_recordset(p_itens) AS x(produto_id INTEGER, quantidade INTEGER, preco_unitario NUMERIC)
    LOOP
        INSERT INTO vendas.itens_venda (venda_id, produto_id, quantidade, preco_unitario)
        VALUES (nova_venda_id, item.produto_id, item.quantidade, item.preco_unitario);

        UPDATE vendas.estoque SET quantidade = quantidade - item.quantidade WHERE produto_id = item.produto_id;
    END LOOP;

    RETURN nova_venda_id;
END;
$$;