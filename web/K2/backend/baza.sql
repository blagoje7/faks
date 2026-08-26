CREATE DATABASE IF NOT EXISTS k2_narudzbine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE k2_narudzbine;

DROP TABLE IF EXISTS stavka;
DROP TABLE IF EXISTS narudzbina;
DROP TABLE IF EXISTS proizvod;

CREATE TABLE proizvod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100) NOT NULL,
    opis TEXT NOT NULL,
    cena DECIMAL(10, 2) NOT NULL,
    jedinica_mere VARCHAR(20) NOT NULL,
    dostupan TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE narudzbina (
    id INT AUTO_INCREMENT PRIMARY KEY,
    broj VARCHAR(20) NOT NULL,
    kupac VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    datum DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'u_pripremi',
    CONSTRAINT uq_narudzbina_broj UNIQUE (broj)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE stavka (
    id INT AUTO_INCREMENT PRIMARY KEY,
    narudzbina_id INT NOT NULL,
    proizvod_id INT NOT NULL,
    kolicina INT NOT NULL,
    cena_po_komadu DECIMAL(10, 2) NOT NULL,

    -- Stavka je podređena narudžbini: briše se zajedno sa njom.
    CONSTRAINT fk_stavka_narudzbina FOREIGN KEY (narudzbina_id)
        REFERENCES narudzbina(id) ON DELETE CASCADE,

    -- Proizvod je šifarnik, a ne roditelj: ne sme nestati ispod stavke.
    CONSTRAINT fk_stavka_proizvod FOREIGN KEY (proizvod_id)
        REFERENCES proizvod(id) ON DELETE RESTRICT,

    CONSTRAINT uq_stavka_proizvod UNIQUE (narudzbina_id, proizvod_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO proizvod (naziv, opis, cena, jedinica_mere, dostupan) VALUES
('Mehanička tastatura', 'Tastatura sa plavim prekidačima i srpskim rasporedom.', 8900.00, 'kom', 1),
('Bežični miš', 'Optički miš sa punjivom baterijom i USB prijemnikom.', 3450.00, 'kom', 1),
('Monitor 27 inča', 'IPS panel rezolucije 2560x1440 sa nagibnim postoljem.', 42000.00, 'kom', 1),
('USB-C kabl', 'Kabl dužine dva metra za prenos podataka i punjenje.', 1200.00, 'kom', 1),
('Postolje za laptop', 'Aluminijumsko postolje sa podesivim uglom.', 4600.00, 'kom', 1),
('Slušalice sa mikrofonom', 'Naglavne slušalice sa poništavanjem buke.', 12500.00, 'kom', 0),
('Toner za štampač', 'Crni toner sa kapacitetom od tri hiljade strana.', 7800.00, 'kom', 1),
('Papir A4', 'Paket od petsto listova gramature osamdeset grama.', 650.00, 'pak', 1);

INSERT INTO narudzbina (broj, kupac, email, datum, status) VALUES
('NAR-2026-0001', 'Milica Jovanović', 'milica.jovanovic@primer.rs', '2026-07-14', 'isporucena'),
('NAR-2026-0002', 'Stefan Petrović', 'stefan.petrovic@primer.rs', '2026-07-28', 'potvrdjena'),
('NAR-2026-0003', 'Ana Nikolić', 'ana.nikolic@primer.rs', '2026-08-05', 'potvrdjena'),
('NAR-2026-0004', 'Marko Ilić', 'marko.ilic@primer.rs', '2026-08-11', 'u_pripremi');

-- cena_po_komadu je zapamćena cena iz trenutka poručivanja i namerno
-- se ne mora poklapati sa tekućom cenom u šifarniku.
INSERT INTO stavka (narudzbina_id, proizvod_id, kolicina, cena_po_komadu) VALUES
(1, 1, 1, 8500.00),
(1, 2, 2, 3450.00),
(1, 4, 3, 1150.00),
(2, 3, 2, 42000.00),
(2, 5, 2, 4600.00),
(3, 7, 4, 7800.00),
(3, 8, 10, 650.00),
(4, 2, 1, 3450.00);
