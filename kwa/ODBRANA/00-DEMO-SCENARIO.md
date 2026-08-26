# 00 — Priprema i demo scenario odbrane

Skripta za odbranu projekta **Upravljanje projektima** (Klijentske veb aplikacije).
Pet dokumenata:

| Fajl | Kada ga čitaš |
|---|---|
| `00-DEMO-SCENARIO.md` | pred samu odbranu — šta klikćeš i šta pričaš |
| `01-ARHITEKTURA.md` | da razumeš celinu i nacrtaš je na papiru |
| `02-PROLAZAK-KROZ-KOD.md` | fajl po fajl, sa rečenicama za objašnjenje |
| `03-ANGULAR-MOGUCNOSTI.md` | šta Angular sve može, šta si upotrebio i zašto |
| `04-PITANJA-I-ODGOVORI.md` | pitanja koja se očekuju, uključujući neprijatna |
| `05-BACKEND-JE-DUMMY.md` | zašto je backend samo JSON Server i kako se to brani |
| `06-MAPA-ZAHTEVA.md` | mapa: svaki zahtev iz specifikacije → tačan fajl i linija u kodu |

---

## 1. Priprema pre odbrane (10 minuta)

```bash
# terminal 1 — backend
npm run server        # json-server na http://localhost:3000

# terminal 2 — aplikacija
npm start             # Angular na http://localhost:4200
```

Provera pre nego što uđeš:

- [ ] `http://localhost:3000/projekti` u pregledaču vraća JSON — server radi
- [ ] `http://localhost:4200` otvara login stranu
- [ ] prijava `blagoje` / `blagoje123` prolazi
- [ ] `db.json` je u početnom stanju (ako si brisao zadatke tokom vežbanja, vrati ih)
- [ ] otvoreni tabovi u editoru: `app.routes.ts`, `auth.service.ts`, `auth.guard.ts`,
      `zadatak.service.ts`, `zadaci.component.ts`, `zadatak-forma.component.ts`
- [ ] pripremljen `db.json` da pokažeš gde se podaci zaista čuvaju

Test nalozi: `blagoje` / `blagoje123` i `test` / `test123`.

---

## 2. Uvodna rečenica (30 sekundi)

> „Aplikacija služi za upravljanje projektima i zadacima. Napisana je u Angularu 20,
> sa standalone komponentama i Angular Material bibliotekom. Backend je simuliran
> JSON Server-om preko `db.json` fajla, a sva komunikacija ide REST pozivima kroz
> `HttpClient`. Aplikacija ima prijavu korisnika, rute zaštićene guardom, pregled
> projekata, pregled i CRUD nad zadacima sa filtriranjem i sortiranjem, i stranu sa
> statistikom."

Time si u jednoj rečenici pokrio pola tehničkih zahteva iz specifikacije.

---

## 3. Demo — redosled klikova i šta se govori

### Korak 1 — zaštita ruta (ne prijavljuj se odmah!)

U adresu ukucaj `http://localhost:4200/projekti`.

> „Ruta `projekti` ima `canActivate: [authGuard]`. Pošto nisam prijavljen, guard vraća
> `UrlTree` ka `/login`, pa me router preusmerava. Ista zaštita stoji i na detaljima
> projekta, formama i statistici."

*(Pokaži `app.routes.ts` i `auth.guard.ts` na ekranu.)*

### Korak 2 — validacija forme

Na login strani klikni **Prijavi se** sa praznim poljima.

> „Ovo je reactive forma. Struktura i validatori su definisani u TypeScript-u —
> `FormBuilder.group` sa `Validators.required` i `Validators.minLength`. Kada je forma
> nevalidna, ne šaljem zahtev nego pozovem `markAllAsTouched()` da bi Material prikazao
> `mat-error` poruke."

Zatim unesi pogrešnu lozinku → snackbar „Pogrešno korisničko ime ili lozinka."

> „Prijava je GET zahtev ka `/korisnici` sa query parametrima; ako server vrati prazan niz,
> kredencijali nisu ispravni."

### Korak 3 — uspešna prijava

Prijavi se kao `blagoje` / `blagoje123`.

> „Nakon prijave `AuthService` upisuje korisnika u `BehaviorSubject` i u `localStorage`,
> pa router prelazi na `/projekti`. Toolbar se sam ažurirao jer je vezan na `korisnik$`
> kroz `async` pipe."

### Korak 4 — lista projekata i sortiranje

Prebaci **Po nazivu / Po roku**.

> „Projekti se učitavaju u `ngOnInit` GET zahtevom. Sortiranje je na klijentu:
> `localeCompare` za naziv, a rok je ISO datum pa se ispravno poredi i kao string."

### Korak 5 — detalji projekta i ugnježdena komponenta

Klikni **Detalji** na prvom projektu.

> „Ruta je `projekti/:id`; id čitam iz `route.snapshot.paramMap`. Ispod detalja je
> ugnježdena komponenta `<app-zadaci [projekatId]="projekat.id">` — to je komunikacija
> roditelj → dete kroz `@Input`. Zadaci se dohvataju posebnim GET zahtevom
> `/zadaci?projekatId=1`."

### Korak 6 — tabela, pipe-ovi, filtriranje, sortiranje

Pokaži kolone Status i Prioritet, pa filtriraj po statusu.

> „U modelu su status i prioritet **brojevi** — enumi `StatusZadatka` i `PrioritetZadatka`,
> i tako se čuvaju u `db.json`. Korisnik ih nikad ne vidi kao brojeve, jer u tabeli koristim
> sopstvene pipe-ove `| status` i `| prioritet`. Filtriranje radi preko
> `MatTableDataSource.filterPredicate`, a sortiranje klikom na zaglavlje kolone kroz `MatSort`."

*(Otvori `db.json` i pokaži `"status": 2` — dokaz da su brojevi.)*

### Korak 7 — dodavanje zadatka (POST)

**Novi zadatak** → pošalji prazan → pokaži greške → popuni → sačuvaj.

> „Ista komponenta opslužuje i dodavanje i izmenu; režim prepoznajem po tome da li ruta
> ima parametar `:id`. Ovde je režim dodavanja pa ide POST bez `id` polja — identifikator
> dodeljuje JSON Server."

### Korak 8 — izmena (PUT)

Klikni olovku na nekom zadatku.

> „Forma se popunjava metodom `patchValue` nakon GET zahteva za taj zadatak. Čuvanje ide
> PUT-om na `/zadaci/:id`, i to celim objektom, jer PUT zamenjuje ceo resurs."

### Korak 9 — brisanje uz dialog (DELETE)

Klikni kantu → **Otkaži** → pa opet → **Obriši**.

> „Brisanje ide kroz `MatDialog`. Dialog vraća `true`/`false` kroz `afterClosed()`, i DELETE
> zahtev se šalje samo ako je korisnik potvrdio."

*(Osveži `db.json` u editoru — zadatak je stvarno nestao.)*

### Korak 10 — statistika

Otvori **Statistika**.

> „Dodatna funkcionalnost: učitavam sve zadatke i prebrojavam ih po statusu i prioritetu,
> uz procente prikazane trakama."

### Korak 11 — localStorage

Pritisni **F5**.

> „I dalje sam prijavljen — `AuthService` pri pokretanju čita korisnika iz `localStorage`,
> pa prijava preživi osvežavanje strane."

### Korak 12 — odjava

Klikni **Odjava**, pa probaj `/projekti`.

> „Odjava briše korisnika iz `BehaviorSubject`-a i iz `localStorage`; guard me odmah vraća
> na login."

---

## 4. Mapa zahteva → gde je urađeno (za brzo pokazivanje)

| Zahtev iz specifikacije | Fajl |
|---|---|
| Prijava korisnika | `components/login/login.component.ts`, `services/auth.service.ts` |
| Zaštita ruta guardom | `guards/auth.guard.ts` + `app.routes.ts` |
| Lista projekata | `components/projekti/` |
| Detalji projekta | `components/projekat-detalji/` |
| Zadaci projekta | `components/zadaci/` |
| Dodavanje / izmena zadatka | `components/zadatak-forma/` |
| Brisanje zadatka | `zadaci.component.ts` → `obrisiZadatak()` |
| Filtriranje po statusu/prioritetu | `zadaci.component.ts` → `filterPredicate` |
| REST kroz HttpClient | `services/*.service.ts` |
| Routing | `app.routes.ts`, `app.config.ts`, `<router-outlet>` |
| Angular Material | sve komponente (toolbar, card, table, dialog, snackbar…) |
| Validacija unosa | `login.component.ts`, `zadatak-forma.component.ts` |
| Bar dva modela | `models/projekat.model.ts`, `zadatak.model.ts`, `korisnik.model.ts` |
| Čuvanje prijavljenog korisnika | `auth.service.ts` (BehaviorSubject + localStorage) |
| **Dodatno:** statistika | `components/statistika/` |
| **Dodatno:** localStorage | `auth.service.ts` |
| **Dodatno:** reactive forme | login, zadatak-forma |
| **Dodatno:** sortiranje | `projekti.component.ts`, `zadaci.component.html` (MatSort) |
| **Dodatno:** snackbar | sve komponente sa HTTP pozivima |
| **Dodatno:** dialog potvrde | `components/confirm-dialog/` |

Detaljna tabela postoji i u `SPECIFIKACIJA.md` u korenu projekta — može se pokazati na ekranu
ako profesor traži mapiranje zahteva.

---

## 5. Tri stvari koje ne smeš da zaboraviš

1. **Status i prioritet su brojevi u modelu, tekst u prikazu** — to je izričit zahtev
   specifikacije i prvo što se proverava. Pipe-ovi `status.pipe.ts` i `prioritet.pipe.ts`.
2. **Guard + AuthService** — pokaži da guard vraća `UrlTree`, a ne da poziva `navigate`.
3. **Sve četiri HTTP metode** postoje: GET, POST, PUT, DELETE — sve u `zadatak.service.ts`.
