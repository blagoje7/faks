# K2 — Odbrana

**Zadatak:** Implementirati rešenje u izabranom programskom jeziku sa odobranim FE/BE alatima. Za bazu MySQL. **Web aplikacija treba da se pokrene i radi na prezentaciji.**

**Urađeno:** Flask REST API + Vue 3 klijent + MySQL, nad domenom `narudzbina → stavka` uz šifarnik `proizvod`. Arhitektura prati MVP podelu prezentovanu na K1.

---

## 1. Izabrani alati i zašto

| Sloj | Alat | Zašto baš to |
|---|---|---|
| Backend jezik | **Python 3** | Jezik korišćen na predavanjima |
| Backend okvir | **Flask 3.1** | Preporučen na predavanjima; mikro okvir kod kog je podela na slojeve vidljiva, a ne skrivena u konvencijama |
| ORM | **Flask-SQLAlchemy 3.1** | Mapira entitete na tabele i drži sesiju kao jedinicu posla |
| Drajver za bazu | **PyMySQL 1.1** | Čist Python konektor, bez potrebe za prevođenjem |
| Baza | **MySQL 8, InnoDB** | Traženo zadatkom; InnoDB zbog transakcija i stranih ključeva |
| Frontend okvir | **Vue 3** (Composition API) | Preporučen na predavanjima; referentni K2 traži Flask + Vue.js |
| Rutiranje na klijentu | **Vue Router 4** | Daje prave adrese za master i detail prikaz |
| Build alat | **Vite 6** | Zvanični build alat za Vue 3 |
| Konfiguracija | **python-dotenv** | Lozinka ide u `.env`, nikad u kod |
| CORS | **Flask-Cors** | Pojas sigurnosti ako se klijent pokrene odvojeno |

**Zašto REST API, a ne server-renderovani Jinja šabloni:** zato što REST razdvaja Presenter od načina prikaza. Granica koja se ne može zaobići lakše se brani nego dogovor da se sloj neće preskakati. Isti API opslužio bi i mobilnu aplikaciju bez ijedne izmene.

---

## 2. Arhitektura i mapa fajlova

| Sloj | Gde živi | Odgovornost |
|---|---|---|
| **Model** | `backend/models.py` | Entiteti, relacije, izvedena polja, serijalizacija |
| **View** | `frontend/src/components/*.vue` | Prikaz i korisnički događaji; bez poslovnih pravila i bez SQL-a |
| **Presenter** | `backend/presenters/*.py` | Prima zahtev, validira, radi nad modelom, vraća stanje |
| **Granica** | HTTP + JSON | Jedini kanal; sa klijentske strane `frontend/src/api.js` |

```
K2/
├── backend/
│   ├── app.py                  app factory, JSON greške, serviranje Vue klijenta
│   ├── config.py               čita .env
│   ├── database.py             SQLAlchemy instanca
│   ├── models.py               MODEL — Proizvod, Narudzbina, Stavka
│   ├── presenters/             PRESENTER
│   │   ├── proizvod_presenter.py
│   │   ├── narudzbina_presenter.py
│   │   ├── stavka_presenter.py
│   │   ├── validacija.py       provera ulaza
│   │   └── tekst.py            srpski oblici uz brojeve
│   ├── baza.sql                šema + početni podaci
│   ├── kreiraj_bazu.py         izvršava baza.sql
│   ├── provera_api.py          samoprovera, 52 provere
│   └── static/                 ovde Vite upisuje izgrađen klijent
└── frontend/
    ├── src/
    │   ├── api.js              jedini kanal ka Presenteru
    │   ├── router.js           klijentsko rutiranje
    │   ├── components/         VIEW — 8 komponenti
    │   ├── poruke.js           obaveštenja
    │   └── tekst.js            formatiranje
    └── vite.config.js          build u backend/static, proxy /api u razvoju
```

---

## 3. Poslovna pravila i gde su sprovedena

| Pravilo | Gde |
|---|---|
| Brisanje narudžbine briše i njene stavke | `ON DELETE CASCADE` + `cascade="all, delete-orphan"` |
| Proizvod koji stoji na stavci ne može se obrisati | `ON DELETE RESTRICT` + provera u `proizvod_presenter` → `409` |
| Cena se pamti u trenutku poručivanja | `stavka_presenter.procitaj_podatke` |
| Isti proizvod najviše jednom po narudžbini | `UNIQUE (narudzbina_id, proizvod_id)` + provera u presenteru |
| Nedostupan proizvod ne može se poručiti | `stavka_presenter` |
| Datum narudžbine ne sme biti u budućnosti | `validacija.datum(bez_buducnosti=True)` |
| Broj narudžbine je jedinstven | `UNIQUE (broj)` + provera u presenteru |
| Količina najmanje 1 | `min="1"` u formi, `validacija.ceo_broj(minimum=1)` u presenteru |

**Tri nivoa odbrane:** HTML atribut sprečava grešku iz nepažnje, provera u Presenteru sprečava neispravan zahtev odakle god došao, ograničenje u bazi sprečava neispravan podatak čak i ako aplikacija ima grešku.

---

## 4. REST API

| Metoda | Putanja | Opis |
|---|---|---|
| `GET` | `/api/proizvodi` | Lista; `pretraga`, `sortiranje`, `smer`, `samo_dostupni` |
| `POST` `PUT` `DELETE` | `/api/proizvodi[/<id>]` | CRUD; `DELETE` vraća `409` ako se koristi |
| `GET` | `/api/narudzbine` | Lista; `pretraga`, `status`, `sortiranje`, `smer` |
| `GET` | `/api/narudzbine/<id>` | Narudžbina sa ugnježdenim stavkama |
| `GET` | `/api/narudzbine/<id>/stavke` | Samo stavke — master-detail vidljiv u adresi |
| `GET` | `/api/narudzbine/sledeci-broj` | Predlog broja |
| `POST` `PUT` `DELETE` | `/api/narudzbine[/<id>]` | CRUD; `DELETE` kaskadno briše stavke |
| `POST` `PUT` `DELETE` | `/api/stavke[/<id>]` | CRUD; oba ključa iz select polja |
| `GET` | `/api/stanje` | Provera veze sa bazom |

**Statusni kodovi:** `200` uspeh · `201` kreirano · `400` neispravan unos · `404` ne postoji · `409` sukob sa stanjem podataka · `503` baza nedostupna.

Greške stižu **po poljima**, pa klijent svaku ispisuje ispod odgovarajućeg polja:

```json
{ "greske": { "kolicina": "Količina ne može biti manja od 1." } }
```

Teorijska pozadina svega ovoga je u [`teorija.html`](teorija.html) — HTTP, REST, ORM, SPA, Vue, CORS.

---

## 5. Priprema pred izlaganje

Uradite ovim redom, **pre nego što uđete u salu**:

1. MySQL servis radi (Services → `MySQL80` → Running)
2. `backend\.env` postoji i ima tačnu lozinku
3. Baza napunjena: `cd backend` pa `venv\Scripts\python kreiraj_bazu.py`
4. Klijent izgrađen: `cd frontend` pa `npm run build`
5. Server pokrenut: `cd backend` pa `venv\Scripts\python app.py`
6. Otvorite `http://localhost:5000/api/stanje` → mora pisati `{"baza": "povezana"}`
7. Otvorite `http://localhost:5000` → mora se videti početna strana

Komanda za pokretanje na dan odbrane:

```bash
cd K2\backend && venv\Scripts\python app.py
```

Ako želite da pokažete da API stvarno radi kako tvrdite:

```bash
cd K2\backend && venv\Scripts\python provera_api.py
```

Ispisuje 52 provere; radi nad privremenom SQLite bazom pa **ne dira MySQL podatke**.

---

## 6. Plan demonstracije

Redosled je namerno takav da svaka stavka zadatka bude pokrivena, a poslednje dve su najjače — ostavite ih za kraj.

| # | Šta uraditi | Šta time pokazujete |
|---|---|---|
| 1 | Početna strana | Zbirni podaci računati iz baze |
| 2 | **Narudžbine** → kucajte u polje za pretragu | Pretraga bez razlike malih i velikih slova, ide na server |
| 3 | Kliknite zaglavlje „Datum”, pa opet | Sortiranje po koloni i smeru |
| 4 | Izaberite status u filteru | Filtriranje |
| 5 | **Detalji** neke narudžbine | Master-detail: narudžbina + njene stavke, zbir u podnožju tabele |
| 6 | **Dodaj stavku** | **Dva select polja** — narudžbina i proizvod; obračun se menja dok birate |
| 7 | Ostavite naslov prazan → Sačuvaj | Validacija na serveru: crveno polje + poruka ispod |
| 8 | Popunite i sačuvajte | Zbir narudžbine se odmah osvežio |
| 9 | Dodajte **isti proizvod ponovo** | Pravilo jedinstvenosti u okviru roditelja |
| 10 | **Izmeni** stavku → promenite narudžbinu u select-u | Premeštanje podređenog zapisa |
| 11 | **Obriši narudžbinu** | Dijalog za potvrdu **generisan na klijentu**, sa brojem stavki |
| 12 | **Proizvodi** → izmenite cenu nekog proizvoda koji je već poručen | — |
| 13 | Vratite se na staru narudžbinu | **Iznos se NIJE promenio** — zapamćena cena |
| 14 | **Proizvodi** → pokušajte da obrišete taj proizvod | **409 sa objašnjenjem** — RESTRICT, za razliku od CASCADE na narudžbini |

Koraci 13 i 14 su ono što odvaja rad koji je „napravio CRUD” od rada koji je **razumeo model**. Nemojte ih preskočiti.

---

## 7. Očekivana pitanja

**Koje ste alate koristili i zašto?**
Vidi tabelu u odeljku 1. Ključno: Flask jer podela na slojeve ostaje vidljiva, Vue jer je preporučen i daje pasivan View, MySQL sa InnoDB zbog transakcija i stranih ključeva.

**Zašto REST API a ne obični Flask sa šablonima?**
Zato što HTTP granica fizički sprečava View da dodirne model. Sa šablonima ta podela ostaje stvar discipline.

**Gde je poslovna logika?**
Struktura i izvedeni podaci u modelu; provera ulaza u Presenteru. U View-u je nema.

**Kako klijent zna na koji server da se obrati?**
Ne zna — poziva relativnu putanju `/api/...`. Na prezentaciji Flask servira i API i klijent sa istog porta, a u razvoju Vite prosleđuje `/api` Flask-u. U oba slučaja isti izvor, pa CORS nije ni potreban.

**Šta se dešava kada osvežite stranicu na `/narudzbine/4`?**
Pretraživač tu adresu stvarno traži od servera. Flask ima pravilo koje sve nepoznate putanje vraća na `index.html`, pa se aplikacija podigne i Vue Router odluči šta da prikaže. Putanje koje počinju sa `api/` su izuzete, da pogrešna API adresa vrati `404` a ne HTML.

**Da li ste testirali?**
`provera_api.py` — 52 provere nad celim API-jem: CRUD, kaskada, RESTRICT, zapamćena cena, premeštanje stavki, validacija, statusni kodovi, SPA rutiranje.

---

## 8. Ako nešto pukne uživo

| Simptom | Šta uraditi |
|---|---|
| `{"baza": "nedostupna"}` | MySQL servis ne radi ili je lozinka u `.env` pogrešna |
| `{"poruka": "Vue klijent nije izgrađen."}` | `cd frontend` pa `npm run build` |
| `Server nije dostupan` u pretraživaču | Flask nije pokrenut ili ne sluša na 5000 |
| `Access denied for user 'root'` | Pogrešna lozinka u `backend\.env` |
| Port 5000 zauzet | U `app.py`, poslednja linija: promenite `port=5000` |
| Podaci zbrkani od probanja | `venv\Scripts\python kreiraj_bazu.py` vraća sve na početno stanje |

Poslednji red je i razlog zašto vredi **probati ceo plan demonstracije dan ranije**, pa zatim ponovo pokrenuti `kreiraj_bazu.py` da podaci na odbrani budu uredni.

---

Arhitektura koja se brani na K1 je u folderu [`../K1`](../K1). Uputstvo za instalaciju je u [`README.md`](README.md).
