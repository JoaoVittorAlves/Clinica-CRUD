--
-- PostgreSQL database dump
--

\restrict 3xiUUr2cMVfx6Ov11bYhYatnhIa9qDbl5nhAmAJXcefEIvZ27FHrTAAaa37iR7v

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: consulta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.consulta (
    id integer NOT NULL,
    data date NOT NULL,
    hora time without time zone NOT NULL,
    paciente_id integer,
    profissional_id integer
);


ALTER TABLE public.consulta OWNER TO postgres;

--
-- Name: consulta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.consulta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.consulta_id_seq OWNER TO postgres;

--
-- Name: consulta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.consulta_id_seq OWNED BY public.consulta.id;


--
-- Name: paciente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.paciente (
    id integer NOT NULL,
    nome character varying(150) NOT NULL,
    idade integer NOT NULL,
    cpf character varying(11) NOT NULL,
    telefone character varying(15)
);


ALTER TABLE public.paciente OWNER TO postgres;

--
-- Name: paciente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.paciente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.paciente_id_seq OWNER TO postgres;

--
-- Name: paciente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.paciente_id_seq OWNED BY public.paciente.id;


--
-- Name: profissional; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profissional (
    id integer NOT NULL,
    nome character varying(150) NOT NULL,
    especialidade character varying(50) NOT NULL,
    registro character varying(60) NOT NULL,
    telefone character varying(15)
);


ALTER TABLE public.profissional OWNER TO postgres;

--
-- Name: profissional_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.profissional_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.profissional_id_seq OWNER TO postgres;

--
-- Name: profissional_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.profissional_id_seq OWNED BY public.profissional.id;


--
-- Name: consulta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consulta ALTER COLUMN id SET DEFAULT nextval('public.consulta_id_seq'::regclass);


--
-- Name: paciente id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paciente ALTER COLUMN id SET DEFAULT nextval('public.paciente_id_seq'::regclass);


--
-- Name: profissional id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profissional ALTER COLUMN id SET DEFAULT nextval('public.profissional_id_seq'::regclass);


--
-- Data for Name: consulta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.consulta (id, data, hora, paciente_id, profissional_id) FROM stdin;
\.


--
-- Data for Name: paciente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.paciente (id, nome, idade, cpf, telefone) FROM stdin;
\.


--
-- Data for Name: profissional; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.profissional (id, nome, especialidade, registro, telefone) FROM stdin;
\.


--
-- Name: consulta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.consulta_id_seq', 1, false);


--
-- Name: paciente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.paciente_id_seq', 1, false);


--
-- Name: profissional_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.profissional_id_seq', 1, false);


--
-- Name: consulta consulta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consulta
    ADD CONSTRAINT consulta_pkey PRIMARY KEY (id);


--
-- Name: paciente paciente_cpf_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paciente
    ADD CONSTRAINT paciente_cpf_key UNIQUE (cpf);


--
-- Name: paciente paciente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paciente
    ADD CONSTRAINT paciente_pkey PRIMARY KEY (id);


--
-- Name: profissional profissional_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profissional
    ADD CONSTRAINT profissional_pkey PRIMARY KEY (id);


--
-- Name: profissional profissional_registro_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profissional
    ADD CONSTRAINT profissional_registro_key UNIQUE (registro);


--
-- Name: consulta consulta_paciente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consulta
    ADD CONSTRAINT consulta_paciente_id_fkey FOREIGN KEY (paciente_id) REFERENCES public.paciente(id) ON DELETE CASCADE;


--
-- Name: consulta consulta_profissional_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consulta
    ADD CONSTRAINT consulta_profissional_id_fkey FOREIGN KEY (profissional_id) REFERENCES public.profissional(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 3xiUUr2cMVfx6Ov11bYhYatnhIa9qDbl5nhAmAJXcefEIvZ27FHrTAAaa37iR7v

