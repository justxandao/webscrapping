-- Script para Criação do Data Warehouse (PixTur) - Versão PostgreSQL

DROP TABLE IF EXISTS Fato_Hospedagem;
DROP TABLE IF EXISTS Dim_Tempo;
DROP TABLE IF EXISTS Dim_Hotel;
DROP TABLE IF EXISTS Dim_Localizacao;

CREATE TABLE Dim_Localizacao (
    sk_local SERIAL PRIMARY KEY,
    cidade VARCHAR(100),
    estado VARCHAR(50),
    pais VARCHAR(50)
);

CREATE TABLE Dim_Hotel (
    sk_hotel SERIAL PRIMARY KEY,
    nome VARCHAR(255),
    tipo VARCHAR(50), -- Hotel, Pousada, Aluguel por temporada, Resort
    estrelas DECIMAL(2, 1)
);

CREATE TABLE Dim_Tempo (
    sk_tempo SERIAL PRIMARY KEY,
    data_completa DATE,
    dia INT,
    mes INT,
    ano INT,
    trimestre INT,
    semestre INT
);

CREATE TABLE Fato_Hospedagem (
    fk_local INT,
    fk_hotel INT,
    fk_tempo INT,
    preco_diaria DECIMAL(10, 2),
    qtd_avaliacoes INT,
    nota_media DECIMAL(3, 1),
    PRIMARY KEY (fk_local, fk_hotel, fk_tempo),
    FOREIGN KEY (fk_local) REFERENCES Dim_Localizacao(sk_local),
    FOREIGN KEY (fk_hotel) REFERENCES Dim_Hotel(sk_hotel),
    FOREIGN KEY (fk_tempo) REFERENCES Dim_Tempo(sk_tempo)
);

-- Populando Dim_Localizacao
INSERT INTO Dim_Localizacao (cidade, estado, pais) VALUES
('Rio de Janeiro', 'RJ', 'Brasil'),
('São Paulo', 'SP', 'Brasil'),
('Salvador', 'BA', 'Brasil');

-- Populando Dim_Hotel
INSERT INTO Dim_Hotel (nome, tipo, estrelas) VALUES
('Copacabana Palace', 'Hotel', 5.0),
('Pousada Mar e Sol', 'Pousada', 3.5),
('Apartamento Moderno Av. Paulista', 'Aluguel por temporada', 4.0),
('Grand Hotel Stella Maris', 'Resort', 4.5),
('Ibis Budget SP', 'Hotel', 2.0),
('Hostel da Vila', 'Pousada', 3.0),
('Casa com Piscina no Pelourinho', 'Aluguel por temporada', 4.2);

-- Populando Dim_Tempo
INSERT INTO Dim_Tempo (data_completa, dia, mes, ano, trimestre, semestre) VALUES
('2025-08-15', 15, 8, 2025, 3, 2),
('2025-09-20', 20, 9, 2025, 3, 2),
('2025-10-01', 1, 10, 2025, 4, 2);

INSERT INTO Fato_Hospedagem (fk_local, fk_hotel, fk_tempo, preco_diaria, qtd_avaliacoes, nota_media) VALUES
-- Dados para o Rio de Janeiro (fk_local=1)
(1, 1, 1, 1500.00, 2500, 9.8),  -- Copacabana Palace
(1, 2, 2, 350.50, 450, 8.5),   -- Pousada Mar e Sol
(1, 1, 3, 1650.00, 2510, 9.8),  -- Copacabana Palace

-- Dados para São Paulo (fk_local=2)
(2, 3, 1, 420.00, 120, 9.2),   -- Apto Av. Paulista
(2, 5, 2, 210.00, 800, 7.8),   -- Ibis Budget SP
(2, 3, 3, 450.00, 125, 9.3),   -- Apto Av. Paulista

-- Dados para Salvador (fk_local=3)
(3, 4, 1, 890.00, 1800, 8.9),  -- Grand Hotel
(3, 6, 2, 150.00, 300, 8.0),   -- Hostel da Vila
(3, 7, 3, 600.00, 85, 9.5);   -- Casa no Pelourinho