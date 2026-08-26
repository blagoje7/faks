# 06 — Mapa zahteva iz specifikacije → mesto u kodu

Svaki red je provereno u kodu (putanja i broj linije), a ne prepisan iz plana.
Putanje su relativne u odnosu na koren projekta `upravljanje-projektima/`.

---

## Osnovne funkcionalnosti aplikacije

| # | Zahtev | Gde je ispunjen |
|---|---|---|
| 1 | prijava korisnika na sistem | `src/app/components/login/login.component.ts:69` (`prijaviSe`) → `src/app/services/auth.service.ts:55` (`prijava`) |
| 2 | zaštita pojedinih ruta pomoću guardova | `src/app/guards/auth.guard.ts:17` + `canActivate` na rutama `app.routes.ts:28, 35, 42, 49, 56` |
| 3 | pregled liste projekata | `src/app/components/projekti/projekti.component.ts:58` (`ngOnInit` → GET) + `.html` (Material kartice) |
| 4 | prikaz detalja pojedinačnog projekta | `src/app/components/projekat-detalji/projekat-detalji.component.ts:50` (čita `:id` iz rute, GET) |
| 5 | pregled zadataka izabranog projekta | `src/app/components/zadaci/zadaci.component.ts:119` (`ucitajZadatke`) → `zadatak.service.ts:26` (`GET /zadaci?projekatId=`) |
| 6 | dodavanje novih zadataka | `zadatak-forma.component.ts:148` → `zadatak.service.ts:51` (`POST /zadaci`) |
| 7 | izmena postojećih zadataka | `zadatak-forma.component.ts:142` → `zadatak.service.ts:60` (`PUT /zadaci/:id`) |
| 8 | brisanje zadataka | `zadaci.component.ts:150` (`obrisiZadatak`) → `zadatak.service.ts:67` (`DELETE /zadaci/:id`) |
| 9 | filtriranje zadataka po statusu ili prioritetu | `zadaci.component.ts:107` (`filterPredicate`) + `:135` (`primeniFilter`); padajuće liste u `zadaci.component.html:18-37` |
| 10 | rad sa REST servisima kroz `HttpClient` | sva tri servisa u `src/app/services/`; `provideHttpClient()` u `app.config.ts:21` |

---

## Tehnički zahtevi

| # | Zahtev | Gde je ispunjen |
|---|---|---|
| 11 | Angular komponente | 7 komponenti u `src/app/components/` + korenska `app.component.ts` |
| 12 | Angular routing | `app.routes.ts` (7 ruta), `provideRouter` u `app.config.ts:20`, `<router-outlet>` u `app.component.html:45` |
| 13 | servisi za komunikaciju sa backend-om | `services/auth.service.ts`, `projekat.service.ts`, `zadatak.service.ts` |
| 14 | JSON Server | `db.json` u korenu + skripta `"server": "json-server --watch db.json --port 3000"` u `package.json:8` |
| 15 | Angular Material komponente | 13 modula: Toolbar, Card, Table, Sort, FormField, Input, Select, Button, ButtonToggle, Icon, Dialog, SnackBar, ProgressSpinner |
| 16 | validacija korisničkog unosa | `login.component.ts:58-61` i `zadatak-forma.component.ts:88-92` (`Validators`), poruke `<mat-error>` u šablonima |
| 17 | najmanje dva modela podataka | tri: `models/projekat.model.ts`, `zadatak.model.ts`, `korisnik.model.ts` |
| 18 | čuvanje podataka o prijavljenom korisniku | `auth.service.ts:33` (`BehaviorSubject`) + `:67` i `:96` (`localStorage`) |

---

## Model podataka

| # | Zahtev | Gde je ispunjen |
|---|---|---|
| 19 | Projekat: id, naziv, opis, rok realizacije | `models/projekat.model.ts:9, 11, 13, 19` |
| 20 | Zadatak: id, id projekta, opis, status, prioritet | `models/zadatak.model.ts:36, 38, 40, 42, 44` |
| 21 | status i prioritet kao **numeričke** vrednosti | `enum StatusZadatka` (`zadatak.model.ts:14`) i `PrioritetZadatka` (`:23`); u `db.json` stoje kao brojevi 0/1/2 |
| 22 | korisnik **nikada** ne vidi numeričke vrednosti | pipe-ovi `pipes/status.pipe.ts:14` i `prioritet.pipe.ts:13`; upotreba: `zadaci.component.html:62` i `:72`. Padajuće liste se pune iz mapa `STATUS_OPISI` / `PRIORITET_OPISI` (`zadatak.model.ts:52, 58`) — `zadaci.component.ts:84-87`, `zadatak-forma.component.ts:74-77` |

---

## Login i zaštita ruta

| # | Zahtev | Gde je ispunjen |
|---|---|---|
| 23 | login strana | `components/login/` + ruta `app.routes.ts:22` (jedina nezaštićena) |
| 24 | preusmeravanje na početnu nakon prijave | `login.component.ts:86` — `router.navigate(['/projekti'])` |
| 25 | podaci o prijavljenom korisniku se čuvaju | `auth.service.ts:66-67` (`korisnikSubject.next` + `localStorage.setItem`) |
| 26 | pristup zaštićenim rutama nakon prijave | `auth.guard.ts:22-23` — `jePrijavljen()` vraća `true` |
| 27 | guard sprečava pristup neprijavljenima | `auth.guard.ts:29` — `router.createUrlTree(['/login'])` |
| 28a | zaštićeno: prikaz projekata | `app.routes.ts:26-29` |
| 28b | zaštićeno: detalji projekta | `app.routes.ts:33-36` |
| 28c | zaštićeno: forme za dodavanje i izmenu zadataka | `app.routes.ts:40-43` i `:47-50` |
| 28d | (preko minimuma) zaštićena statistika | `app.routes.ts:54-57` |

---

## REST komunikacija

| # | Zahtev | Gde je ispunjen |
|---|---|---|
| 29a | GET | `auth.service.ts:57`, `projekat.service.ts:28` i `:36`, `zadatak.service.ts:27`, `:36`, `:43` |
| 29b | POST | `zadatak.service.ts:52` |
| 29c | PUT (ili PATCH) | `zadatak.service.ts:61` — korišćen PUT |
| 29d | DELETE | `zadatak.service.ts:68` |

---

## Organizacija aplikacije (minimalne komponente)

| # | Tražena komponenta | Realizovana kao |
|---|---|---|
| 30a | login komponenta | `components/login/` |
| 30b | komponenta za prikaz projekata | `components/projekti/` |
| 30c | komponenta za detalje projekta | `components/projekat-detalji/` |
| 30d | komponenta za prikaz zadataka | `components/zadaci/` |
| 30e | komponenta za formu dodavanje/izmena zadatka | `components/zadatak-forma/` |
| 30f | (preko minimuma) | `components/statistika/`, `components/confirm-dialog/`, korenska `app.component` |

---

## Dodatne funkcionalnosti za više ocene — svih šest je urađeno

| # | Funkcionalnost | Gde je ispunjena |
|---|---|---|
| 31 | prikaz statistike zadataka | `components/statistika/statistika.component.ts:56-62` + `:82` (`izracunaj`), ruta `/statistika` |
| 32 | čuvanje podataka u `localStorage` | `auth.service.ts:67, 77, 96` — prijava preživi F5 |
| 33 | reactive forme | `login.component.ts:58` i `zadatak-forma.component.ts:88` (`FormBuilder`, `FormGroup`, `Validators`) |
| 34 | sortiranje podataka | projekti: `projekti.component.ts:78-93` (`localeCompare`, po nazivu/roku); zadaci: `MatSort` — `zadaci.component.ts:90` + `mat-sort-header` u šablonu |
| 35 | poruke kroz snackbar | `MatSnackBar` u login, projekti, projekat-detalji, zadaci, zadatak-forma, statistika |
| 36 | potvrda brisanja kroz dialog | `components/confirm-dialog/` + `zadaci.component.ts:151` (`dialog.open`) i `:158` (`afterClosed`) |

---

## Predaja i odbrana

| # | Obaveza | Status |
|---|---|---|
| 37 | zip **bez** `node_modules` | `.gitignore:2` isključuje `node_modules`; pre pakovanja obrisati folder |
| 38 | naziv arhive: ime, prezime, broj indeksa | uraditi pri pakovanju |
| 39 | JSON server sa inicijalnim podacima za sve segmente | `db.json`: 2 korisnika, 3 projekta, 8 zadataka — pokriveni **svi statusi** (3 novo, 2 u toku, 3 završeno) i **svi prioriteti** (2 nizak, 2 srednji, 4 visok); nema zadataka bez projekta |
| 40 | demonstracija, objašnjenje strukture, odgovori, dopuna koda | `ODBRANA/00-DEMO-SCENARIO.md` (demo), `01`–`03` (struktura i mogućnosti), `04` (pitanja), `04` odeljak D (dopuna koda uživo) |

---

## Zaključak

Svi obavezni zahtevi su ispunjeni, i **svih šest** navedenih dodatnih funkcionalnosti.
Jedino što ostaje pred predaju: obrisati `node_modules`, zipovati i nazvati arhivu
*Ime Prezime BrojIndeksa*, i proveriti da je `db.json` u demonstracionom stanju
(bez test-zapisa nastalih tokom vežbanja).
