-- SCRIPT DE INSERÇÃO CORRIGIDO (COM TRUNCATE PARA RESETAR OS IDs)

TRUNCATE Dim_Localizacao, Dim_Hotel, Dim_Tempo, Fato_Hospedagem RESTART IDENTITY CASCADE;

-- Dim_Localizacao com mais cidades
INSERT INTO Dim_Localizacao (cidade, estado, pais) VALUES
('Rio de Janeiro', 'RJ', 'Brasil'),      -- Agora será sk_local = 1
('São Paulo', 'SP', 'Brasil'),           -- Agora será sk_local = 2
('Salvador', 'BA', 'Brasil'),            -- Agora será sk_local = 3
('Florianópolis', 'SC', 'Brasil'),       -- Agora será sk_local = 4
('Gramado', 'RS', 'Brasil'),             -- Agora será sk_local = 5
('Fortaleza', 'CE', 'Brasil');            -- Agora será sk_local = 6

-- Dim_Hotel com muito mais variedade
INSERT INTO Dim_Hotel (nome, tipo, estrelas) VALUES
('Copacabana Palace', 'Hotel', 5.0),                         -- sk_hotel = 1
('Pousada Mar e Sol', 'Pousada', 3.5),                       -- sk_hotel = 2
('Ipanema Beach Hostel', 'Pousada', 3.0),
('Apartamento Vista Mar', 'Aluguel por temporada', 4.5),
('Grand Hyatt SP', 'Hotel', 5.0),
('Ibis Budget SP', 'Hotel', 2.0),
('Apartamento Moderno Av. Paulista', 'Aluguel por temporada', 4.0),
('Blue Tree Faria Lima', 'Hotel', 4.0),
('Grand Hotel Stella Maris', 'Resort', 4.5),
('Hostel da Vila', 'Pousada', 3.0),
('Casa com Piscina no Pelourinho', 'Aluguel por temporada', 4.2),
('Il Campanario Villaggio Resort', 'Resort', 5.0),
('Pousada dos Sonhos', 'Pousada', 4.0),
('Studio na Beira-Mar', 'Aluguel por temporada', 4.8),
('Hotel Ritta Höppner', 'Hotel', 5.0),
('Pousada Tissiani Gramado', 'Pousada', 3.8),
('Cabana Romântica na Serra', 'Aluguel por temporada', 4.9),
('Vila Galé Fortaleza', 'Hotel', 4.5),
('Beach Park Resort', 'Resort', 4.8),
('Praiano Hotel', 'Hotel', 4.0);


-- Dim_Tempo cobrindo 12 meses para mostrar sazonalidade
INSERT INTO Dim_Tempo (data_completa, dia, mes, ano, trimestre, semestre) VALUES
('2025-01-15', 15, 1, 2025, 1, 1),
('2025-02-20', 20, 2, 2025, 1, 1),
('2025-03-10', 10, 3, 2025, 1, 1),
('2025-04-25', 25, 4, 2025, 2, 1),
('2025-05-05', 5, 5, 2025, 2, 1),
('2025-06-15', 15, 6, 2025, 2, 1),
('2025-07-20', 20, 7, 2025, 3, 2),
('2025-08-18', 18, 8, 2025, 3, 2),
('2025-09-22', 22, 9, 2025, 3, 2),
('2025-10-30', 30, 10, 2025, 4, 2),
('2025-11-12', 12, 11, 2025, 4, 2),
('2025-12-28', 28, 12, 2025, 4, 2);


-- POPULA A TABELA FATO COM DADOS VARIADOS E SAZONAIS
INSERT INTO Fato_Hospedagem (fk_local, fk_hotel, fk_tempo, preco_diaria, qtd_avaliacoes, nota_media) VALUES
(5, 15, 1, 1800.00, 2200, 9.9),
(5, 16, 12, 950.00, 850, 9.2),
(4, 12, 1, 1650.00, 3100, 9.4),
(4, 14, 12, 1100.00, 450, 9.8),
(6, 19, 1, 2200.00, 4500, 9.1),
(6, 18, 12, 850.00, 2800, 8.8),

(5, 15, 5, 950.00, 2250, 9.9),
(5, 16, 9, 400.00, 870, 9.2),
(4, 12, 5, 800.00, 3150, 9.4),
(6, 19, 9, 1300.00, 4580, 9.1),

(2, 5, 3, 980.00, 4200, 9.3),
(2, 5, 10, 1050.00, 4350, 9.3),
(2, 6, 4, 280.00, 5100, 7.6),
(2, 6, 11, 295.00, 5230, 7.6),

(1, 1, 2, 2500.00, 3500, 9.8),
(1, 1, 8, 1400.00, 3600, 9.8),
(1, 4, 7, 950.00, 320, 9.5),
(3, 9, 6, 880.00, 1900, 8.9),
(3, 11, 10, 650.00, 95, 9.6);