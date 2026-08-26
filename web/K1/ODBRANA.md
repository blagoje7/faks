# K1 — Odbrana

**Predmet:** Veb programiranje
**Zadatak:** Izabrati domen za master-detail (parent-child) ažuriranja i prezentovati arhitekturu po principu implementacije MVP paterna.

**Izabrani domen:** evidencija narudžbina.

| | |
|---|---|
| Master (nadređeni) | `narudzbina` |
| Detail (podređeni) | `stavka` |
| Šifarnik | `proizvod` |
| Relacija | 1 : N |
| Pattern | Model – View – Presenter |

---

## 1. Zašto je ovo master-detail, a ne obična veza

Narudžbina postoji samostalno. Stavka ne postoji bez narudžbine — strani ključ `stavka.narudzbina_id` je `NOT NULL`, pa svaka stavka pripada tačno jednoj narudžbini. **Životni vek podređenog zapisa zavisi od nadređenog**, i to je ono što relaciju čini master-detail.

Proizvod je nešto treće. Stavka ga referiše, ali proizvod **nije** njen roditelj — postojao je pre nje i ostaje posle nje.

> **Ovo je najjača tačka celog rada.** U tabeli `stavka` postoje dva strana ključa i oni su namerno različito podešeni, jer izražavaju različite odnose. Ako profesor pita samo jednu stvar, verovatno će pitati ovu.

---

## 2. Model podataka

Dijagram: [`dijagrami/01-model-podataka.svg`](dijagrami/01-model-podataka.svg)

```
proizvod  (šifarnik)          narudzbina  (MASTER)
  id                            id
  naziv                         broj        UNIQUE
  opis                          kupac
  cena                          email
  jedinica_mere                 datum
  dostupan                      status
      │                             │ 1
      │ RESTRICT                    │ CASCADE
      │                             │ N
      └────────► stavka  (DETAIL) ◄─┘
                   id
                   narudzbina_id  FK
                   proizvod_id    FK
                   kolicina
                   cena_po_komadu
                   UNIQUE (narudzbina_id, proizvod_id)
```

### DDL

```sql
CREATE TABLE proizvod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    naziv VARCHAR(100) NOT NULL,
    opis TEXT NOT NULL,
    cena DECIMAL(10, 2) NOT NULL,
    jedinica_mere VARCHAR(20) NOT NULL,
    dostupan TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE narudzbina (
    id INT AUTO_INCREMENT PRIMARY KEY,
    broj VARCHAR(20) NOT NULL,
    kupac VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    datum DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'u_pripremi',
    CONSTRAINT uq_narudzbina_broj UNIQUE (broj)
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;
```

### Zašto `cena_po_komadu` nije suvišna kopija

`proizvod.cena` je **tekuća** cena u šifarniku. `stavka.cena_po_komadu` je cena **po kojoj je taj kupac tada poručio**. Bez te kolone, svaka izmena cenovnika retroaktivno bi promenila iznose svih ranijih narudžbina.

### Izvedeni podaci se računaju, ne čuvaju

`broj_stavki` i `ukupan_iznos` narudžbine nisu kolone — izvode se iz stavki pri svakom čitanju. Da su upisani, morali bi se ručno održavati pri svakoj izmeni stavke i pre ili kasnije bi se razišli sa stvarnim stanjem.

---

## 3. MVP pattern

Dijagram: [`dijagrami/02-mvp-slojevi.svg`](dijagrami/02-mvp-slojevi.svg)

| Sloj | Odgovornost |
|---|---|
| **Model** | Entiteti domena i njihova pravila. Ne zna da korisnički interfejs postoji. |
| **View** | Pasivan sloj. Prikazuje ono što dobije i prijavljuje korisničke događaje. Ne sadrži poslovna pravila i **nikada ne pristupa modelu**. |
| **Presenter** | Posrednik. Prima događaj od View-a, proverava ulaz, radi nad modelom i vraća stanje koje View prikazuje. |

### Mapa na kod

| Sloj | Gde živi |
|---|---|
| Model | `K2/backend/models.py` — SQLAlchemy entiteti |
| Presenter | `K2/backend/presenters/` — Flask blueprints |
| View | `K2/frontend/src/components/` — Vue komponente |
| Granica | HTTP + JSON; jedini kanal je `K2/frontend/src/api.js` |

Zavisnosti idu samo nadole. Presenter je jedini sloj koji zna za oba susedna — View ne zna za model, model ne zna za View. **Uklanjanje Presentera prekida svaku vezu između njih, i to je merilo da je podela sprovedena.**

### MVP vs MVC vs MVVM

| Pitanje | MVC | **MVP** | MVVM |
|---|---|---|---|
| Ko prima korisnički ulaz | Controller | **View, pa prosleđuje Presenteru** | View |
| Da li View čita model | Da, direktno | **Ne, nikada** | Ne, preko ViewModel-a |
| Odnos View-a i posrednika | Jedan Controller opslužuje više View-ova | **Presenter je vezan za svoj View** | ViewModel ne zna za View |
| Kako se View osvežava | Sam čita izmenjen model | **Presenter mu prosledi novo stanje** | Deklarativnim vezivanjem |
| Testiranje bez interfejsa | Otežano | **Lako — View se zameni stubom** | Lako |

**Odlučujuća razlika u odnosu na MVC je u drugom redu.** U MVC-u View sme da čita model direktno i sam se osvežava. U MVP-u ta veza ne postoji: sve što View prikaže prošlo je kroz Presenter.

---

## 4. Tok jednog ažuriranja

Dijagram: [`dijagrami/03-tok-azuriranja.svg`](dijagrami/03-tok-azuriranja.svg)

Dodavanje stavke postojećoj narudžbini:

| # | Ko → kome | Šta |
|---|---|---|
| 1 | Vue komponenta → `api.js` | `stavkaApi.dodaj(model)` |
| 2 | `api.js` → `stavka_presenter` | `POST /api/stavke` sa JSON telom |
| 3 | Presenter → Model | validacija, pa preuzimanje cene iz šifarnika i `INSERT` |
| 4 | Model → Presenter | dodeljen `id` |
| 5 | Presenter → `api.js` | `201` + JSON stavke |
| 6 | `api.js` → Vue komponenta | objekat stavke; prelazak na prikaz narudžbine |

**Dve stvari koje treba naglasiti:**

- U koraku 3 Presenter **ne uzima cenu iz zahteva** nego je čita iz šifarnika. Klijent ne sme da diktira cenu.
- Ako validacija ne prođe, Presenter se **uopšte ne obraća modelu** — vraća `400` sa greškama po poljima, a View ih ispisuje ispod odgovarajućih polja.

---

## 5. Master-detail operacije

| Operacija | Šta se dešava |
|---|---|
| **Brisanje narudžbine** | Briše i sve njene stavke. `ON DELETE CASCADE` u bazi je poslednja odbrana, `cascade="all, delete-orphan"` u modelu radi isto kroz sesiju. Korisnik pre toga dobija potvrdu sa brojem stavki. |
| **Brisanje proizvoda** | Ako stoji na nekoj stavci, odbija se sa `409` i porukom da ga označi kao nedostupnog. Kaskada bi ovde tiho uništila iznose ranijih narudžbina. |
| **Premeštanje stavke** | Narudžbina se pri izmeni bira u select polju; promena tog polja premešta stavku. Presenter proverava da izabrana narudžbina postoji. |
| **Zapamćena cena** | `cena_po_komadu` se prepisuje iz šifarnika samo kad se stavka kreira ili joj se promeni proizvod. Izmena količine ne dira cenu. |
| **Izvedeni podaci** | `broj_stavki` i `ukupan_iznos` računaju se iz stavki, u modelu. |
| **Pravilo u okviru roditelja** | Isti proizvod najviše jednom po narudžbini; Presenter vraća predlog da se izmeni količina. |

---

## 6. Očekivana pitanja

**Zašto MVP, a ne MVC?**
Zato što u MVP-u View nema pristup modelu. Sve što se prikaže prošlo je kroz Presenter, pa je poslovna logika na jednom mestu i može se testirati bez pokretanja interfejsa. U MVC-u View posmatra model direktno, čime se ta granica gubi.

**Zašto su dva strana ključa u istoj tabeli različito podešena?**
Jer izražavaju različite odnose. Narudžbina je vlasnik svojih stavki → `CASCADE`. Proizvod je šifarnik na koji se stavka poziva; postojao je pre nje i ne sme nestati ispod nje → `RESTRICT`. Kad bi i proizvod imao kaskadu, brisanje jednog artikla obrisalo bi stavke iz tuđih narudžbina.

**Zašto stavka pamti cenu kad proizvod već ima cenu?**
Zato što su to dva različita podatka: tekuća cena u šifarniku i cena po kojoj je kupac tada poručio. Bez zapamćene cene, izmena cenovnika menjala bi iznose svih ranijih narudžbina.

**Gde tačno prestaje View, a počinje Presenter?**
Na HTTP granici. Sve u `frontend/src/components/` je View, sve u `backend/presenters/` je Presenter. `api.js` je jedini kanal i ne sadrži nijedno poslovno pravilo.

**Zašto validacija na serveru kad je već ima u pretraživaču?**
Provera u pretraživaču je udobnost, ne zaštita — zahtev se može poslati i mimo interfejsa. Model bi inače zavisio od ispravnosti View-a, čime bi se srušila podela na kojoj pattern počiva.

**Zašto se ukupan iznos ne čuva u tabeli?**
Jer bi bio podatak koji se može razići sa izvorom. Izvodi se iz stavki pri svakom čitanju, pa je uvek tačan.

**Zašto REST API kada aplikacija ima samo jednog klijenta?**
Zato što razdvaja Presenter od načina prikaza. Isti Presenter opslužio bi i mobilnu aplikaciju bez izmena, a granica koja se ne može zaobići lakše se brani nego dogovor da se sloj neće preskakati.

**Kako biste dodali još jedan entitet, na primer dostavljača?**
Klasa u `models.py`, novi blueprint u `presenters/`, komponente za prikaz i formu. Postojeći slojevi se ne diraju — to je i svrha podele.

### Ako pita za Vue i MVVM

Vue interno koristi deklarativno vezivanje podataka, što je odlika MVVM-a. To ne menja arhitekturu: komponenta nema pristup bazi ni pravilima domena — ona poziva Presenter i prikazuje ono što dobije. **Vezivanje je tehnika prikaza unutar View sloja, a ne kanal ka modelu.**

Bolje je ovo reći sam nego čekati da bude izvučeno kao zamerka.

---

## 7. Plan izlaganja

| Min | Tema | Šta pokazati |
|---|---|---|
| 0–1 | Domen i zašto je master-detail | Zavisnost životnog veka stavke od narudžbine |
| 1–4 | Model podataka | Dijagram 01; naglasiti CASCADE vs RESTRICT i zapamćenu cenu |
| 4–7 | MVP pattern | Dijagram 02; tabela poređenja sa MVC |
| 7–9 | Tok ažuriranja | Dijagram 03; naglasiti da cenu upisuje server |
| 9–10 | Zaključak | Šta se može zameniti bez diranja ostalog |

**Prva rečenica:** „Domen je evidencija narudžbina. Narudžbina je nadređeni entitet, stavka podređeni, a proizvod je šifarnik koji namerno stoji van te veze — i ta razlika se vidi u tome kako su podešena dva strana ključa u istoj tabeli.”

---

## 8. Šta je u ovom folderu

| Fajl | Sadržaj |
|---|---|
| `ODBRANA.md` | ovaj dokument |
| `prezentacija.html` | ista sadržina u obliku za prikaz na ekranu; otvara se dvoklikom, radi bez interneta |
| `dijagrami/01-model-podataka.svg` | ER dijagram sa CASCADE i RESTRICT granama |
| `dijagrami/02-mvp-slojevi.svg` | Raspored odgovornosti po slojevima |
| `dijagrami/03-tok-azuriranja.svg` | Sekvenca dodavanja stavke |

SVG fajlovi se mogu ubaciti u PowerPoint (Insert → Pictures) i skaliraju se bez gubitka oštrine.

Implementacija koja prati ovu arhitekturu je u folderu [`../K2`](../K2).
