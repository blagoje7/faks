# K2 — Narudžbine i stavke (Flask REST API + Vue.js)

> Uputstvo za instalaciju i pokretanje. Za odbranu, plan demonstracije i
> očekivana pitanja vidi [ODBRANA.md](ODBRANA.md); za teorijsku pozadinu
> [teorija.html](teorija.html).

Web aplikacija za master-detail ažuriranje nad domenom **narudžbina → stavka**,
uz šifarnik proizvoda. Backend je Flask REST servis, klijent je Vue 3
aplikacija, baza je MySQL.

---

## Model podataka

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

Dva strana ključa namerno se ponašaju različito, i to je suština modela:

- **`narudzbina_id` → `ON DELETE CASCADE`.** Stavka je podređena narudžbini.
  Nema smisla van nje, pa se briše zajedno sa njom.
- **`proizvod_id` → `ON DELETE RESTRICT`.** Proizvod je šifarnik, a ne
  roditelj. Stavka ga referiše, ali ga ne posedeuje, i on ne sme nestati
  ispod postojećih narudžbina. Brisanje upotrebljenog proizvoda vraća
  `409 Conflict` sa objašnjenjem.

Izvedeni podaci se **računaju, a ne čuvaju**: `broj_stavki` i `ukupan_iznos`
narudžbine izvode se iz njenih stavki, a `iznos` stavke iz količine i cene.

---

## Arhitektura po MVP patternu

| Sloj | Gde živi | Odgovornost |
|---|---|---|
| **Model** | `backend/models.py` | Entiteti, relacije, izvedena polja, serijalizacija |
| **View** | `frontend/src/components/*.vue` | Prikaz i korisnički događaji; bez poslovnih pravila i bez SQL-a |
| **Presenter** | `backend/presenters/*.py` | Prima zahtev, validira ulaz, radi nad modelom, vraća stanje |

Modul `frontend/src/api.js` je jedini kanal između View-a i Presentera —
prevodi poziv u HTTP zahtev i odgovor u greške po poljima.

---

## Poslovna pravila

1. **Cena se pamti u trenutku poručivanja.** `stavka.cena_po_komadu` se
   prepisuje iz šifarnika kada se stavka kreira ili kada joj se promeni
   proizvod. Izmena količine ne dira zapamćenu cenu, a kasnija promena
   cenovnika ne menja iznose ranijih narudžbina.
2. **Proizvod se na jednoj narudžbini pojavljuje najviše jednom.** Umesto
   drugog reda, menja se količina postojeće stavke.
3. **Nedostupan proizvod ne može se poručiti**, ali stavke koje ga već
   sadrže ostaju netaknute.
4. **Datum narudžbine ne može biti u budućnosti.**
5. **Broj narudžbine je jedinstven.** Server predlaže sledeći slobodan broj
   u obliku `NAR-GGGG-NNNN`, a korisnik ga može promeniti.

---

## Preduslovi

- Python 3.10 ili noviji
- Node.js 18 ili noviji
- MySQL 8 (servis mora biti pokrenut)

---

## Podešavanje (jednom)

**1. Konfiguracija baze**

```bash
copy backend\.env.example backend\.env
```

Otvorite `backend\.env` i upišite svoju MySQL lozinku.

**2. Python okruženje**

```bash
cd backend && python -m venv venv && venv\Scripts\pip install -r requirements.txt
```

**3. Kreiranje baze i početnih podataka**

```bash
cd backend && venv\Scripts\python kreiraj_bazu.py
```

Skripta traži lozinku ako nije upisana u `.env`, i na kraju ispisuje broj
unetih redova.

**4. Build klijentske aplikacije**

```bash
cd frontend && npm install && npm run build
```

Build se upisuje u `backend/static/`, pa Flask servira i API i klijent.

---

## Pokretanje na prezentaciji

Jedan server, jedna komanda:

```bash
cd backend && venv\Scripts\python app.py
```

Aplikacija je na **http://localhost:5000**.

Provera pre izlaganja — `http://localhost:5000/api/stanje` mora vratiti
`{"baza": "povezana"}`.

---

## Pokretanje u razvoju

Dva terminala, sa automatskim osvežavanjem klijenta:

```bash
cd backend && venv\Scripts\python app.py
```

```bash
cd frontend && npm run dev
```

Klijent je na `http://localhost:5173` i prosleđuje `/api` zahteve Flask-u,
pa se putanje ne razlikuju od produkcijskih.

---

## REST API

### Proizvodi

| Metoda | Putanja | Opis |
|---|---|---|
| `GET` | `/api/proizvodi` | Lista; parametri `pretraga`, `sortiranje`, `smer`, `samo_dostupni` |
| `GET` | `/api/proizvodi/jedinice-mere` | Dozvoljene jedinice mere |
| `GET` | `/api/proizvodi/<id>` | Jedan proizvod |
| `POST` | `/api/proizvodi` | Nov proizvod |
| `PUT` | `/api/proizvodi/<id>` | Izmena |
| `DELETE` | `/api/proizvodi/<id>` | Brisanje; `409` ako se koristi na stavkama |

### Narudžbine

| Metoda | Putanja | Opis |
|---|---|---|
| `GET` | `/api/narudzbine` | Lista; parametri `pretraga`, `status`, `sortiranje`, `smer` |
| `GET` | `/api/narudzbine/statusi` | Dozvoljeni statusi sa nazivima |
| `GET` | `/api/narudzbine/sledeci-broj` | Predlog broja za novu narudžbinu |
| `GET` | `/api/narudzbine/<id>` | Narudžbina sa ugnježdenim stavkama |
| `GET` | `/api/narudzbine/<id>/stavke` | Samo stavke |
| `POST` | `/api/narudzbine` | Nova narudžbina |
| `PUT` | `/api/narudzbine/<id>` | Izmena |
| `DELETE` | `/api/narudzbine/<id>` | Brisanje, kaskadno i stavke |

### Stavke

| Metoda | Putanja | Opis |
|---|---|---|
| `GET` | `/api/stavke/<id>` | Jedna stavka |
| `POST` | `/api/stavke` | Nova stavka; `narudzbina_id` i `proizvod_id` iz select polja |
| `PUT` | `/api/stavke/<id>` | Izmena, uključujući premeštanje na drugu narudžbinu |
| `DELETE` | `/api/stavke/<id>` | Brisanje |

### Statusni kodovi

| Kod | Značenje |
|---|---|
| `200` | Uspeh |
| `201` | Resurs je kreiran |
| `400` | Neispravan unos; telo sadrži `greske` po poljima |
| `404` | Traženi entitet ne postoji |
| `409` | Radnja je u sukobu sa stanjem podataka (brisanje upotrebljenog proizvoda) |
| `503` | Baza nije dostupna |

Greške validacije vraćaju se po poljima, pa klijent svaku ispisuje ispod
odgovarajućeg polja:

```json
{ "greske": { "kolicina": "Količina ne može biti manja od 1." } }
```

---

## Šta je implementirano

- CRUD nad sva tri entiteta, u celini preko REST API-ja
- Izbor vezanih entiteta preko **select polja** — stavka bira i narudžbinu i
  proizvod, i pri dodavanju i pri izmeni
- Potvrda brisanja kao **Vue komponenta generisana na klijentu**, sa porukom
  koja navodi koliko će stavki biti obrisano
- Validacija na serveru sa greškama po poljima; neispravno polje se boji
  crveno i poruka se ispisuje ispod njega
- Pretraga bez razlike malih i velikih slova, filtriranje po statusu i
  sortiranje klikom na zaglavlje tabele
- Živ obračun u formi stavke koji pokazuje koja cena važi i zašto
- Statusi prikazani kao obojene oznake, sa zbirnim redom u tabeli stavki

---

## Samoprovera

```bash
cd backend && venv\Scripts\python provera_api.py
```

Pokreće 52 provere nad celim API-jem (CRUD, kaskadno brisanje, RESTRICT,
zapamćena cena, premeštanje stavki, validacija, statusni kodovi, SPA
rutiranje). Radi nad privremenom SQLite bazom, pa ne dira MySQL podatke.

---

## Ako nešto ne radi

| Simptom | Uzrok i rešenje |
|---|---|
| `{"baza": "nedostupna"}` | MySQL servis ne radi ili je lozinka u `.env` pogrešna |
| `{"poruka": "Vue klijent nije izgrađen."}` | Nije pokrenut `npm run build` u `frontend/` |
| `Server nije dostupan` u pretraživaču | Flask nije pokrenut ili ne sluša na portu 5000 |
| `Access denied for user 'root'` | Pogrešna lozinka u `backend/.env` |
