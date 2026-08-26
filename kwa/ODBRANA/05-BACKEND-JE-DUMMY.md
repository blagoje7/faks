# 05 — Backend je namerno „dummy", fokus je frontend

Predmet se zove **Klijentske veb aplikacije**. Ocenjuje se ono što se dešava u pregledaču:
komponente, rutiranje, servisi, forme, validacija, stanje aplikacije. Backend je tu samo da
bi frontend imao sa čim da razgovara.

Ovo poglavlje ti daje rečenice kojima to braniš — i granicu do koje treba da ideš u
objašnjavanju.

---

## 1. Šta je backend u ovom projektu

**JSON Server** — alat koji od jednog `db.json` fajla napravi kompletan REST API.
Nema nijedne linije serverskog koda koju sam napisao:

```json
// package.json
"server": "json-server --watch db.json --port 3000"
```

```json
// db.json — tri kolekcije
{ "korisnici": [...], "projekti": [...], "zadaci": [...] }
```

Iz toga JSON Server automatski pravi rute:

| Metoda | Putanja | Efekat |
|---|---|---|
| GET | `/projekti`, `/projekti/1` | lista / jedan zapis |
| GET | `/zadaci?projekatId=1` | filtriranje po vrednosti polja |
| POST | `/zadaci` | dodaje, sam dodeljuje `id` |
| PUT / PATCH | `/zadaci/5` | zamena celog / delimična izmena |
| DELETE | `/zadaci/5` | brisanje |

To je **prava HTTP komunikacija** — pravi zahtevi, pravi statusi, podaci se stvarno upisuju
u `db.json`. Nije mock unutar Angulara, nije niz u memoriji.

Rečenica za odbranu:
> „Backend je JSON Server — alat koji od `db.json` fajla pravi REST API. Nisam pisao
> serverski kod, jer predmet ocenjuje klijentsku stranu. Frontend komunicira potpuno
> realno: `HttpClient`, GET/POST/PUT/DELETE, asinhrona obrada odgovora i grešaka."

---

## 2. Zašto je to dovoljno — i zašto je bolji izbor od pravog backenda

1. **Specifikacija to i traži.** U tehničkim zahtevima piše „JSON Server" kao backend.
2. **Ništa ne skriva.** Svi zahtevi se vide u Network tabu; `db.json` se menja pred
   profesorom. To je jači dokaz da REST komunikacija radi nego bilo kakav backend kod.
3. **Podiže se za dve sekunde** i uvek radi isto — nema baze, migracija, portova, Docker-a.
   Na odbrani je to razlika između demonstracije i traženja greške po logovima.
4. **Vreme je uloženo tamo gde se ocenjuje** — u komponente, rutiranje, forme, guardove,
   pipe-ove i stanje aplikacije.

---

## 3. Šta frontend radi — to je ono što braniš

Ovo je lista koju treba da izgovoriš ako te profesor pita „šta si ti tu zapravo uradio":

| Oblast | Šta je urađeno |
|---|---|
| Komponente | 7 standalone komponenti + korenska; ugnježdavanje (`<app-zadaci [projekatId]>`) |
| Rutiranje | 7 ruta, parametri (`:id`), preusmerenja, wildcard, zaštita guardom |
| Guard | funkcionalni `CanActivateFn` sa `inject()`, vraća `UrlTree` |
| Servisi + DI | tri servisa, `providedIn: 'root'`, `HttpClient` kroz konstruktor |
| REST | sve četiri metode: GET, POST, PUT, DELETE; query parametri |
| RxJS | `Observable`, `subscribe({ next, error })`, `map`, `BehaviorSubject`, `async` pipe |
| Stanje aplikacije | prijavljeni korisnik u `BehaviorSubject` + `localStorage` (preživi F5) |
| Forme | reactive forme, `FormBuilder`, `Validators`, `patchValue`, `markAllAsTouched` |
| Prikaz podataka | sopstveni pipe-ovi (`status`, `prioritet`), `DatePipe` |
| Tabela | `MatTableDataSource` sa `filterPredicate` i `MatSort`, `@ViewChild` setter |
| UI biblioteka | Angular Material: toolbar, kartice, tabela, dialog, snackbar, spinner |
| UX | indikator učitavanja, poruke o uspehu i grešci, potvrda brisanja |

Ništa sa te liste ne bi bilo bolje ni „ozbiljnije" da iza stoji Spring ili Node backend —
kod u `src/` bio bi identičan.

---

## 4. Odgovori na očekivana pitanja

**„Zašto nisi napisao pravi backend?"**
> Zato što je predmet klijentske veb aplikacije, a specifikacija kao backend navodi JSON
> Server. Frontend je pisan tako da ne zna kakav je server sa druge strane — komunicira
> preko `HttpClient`-a i REST konvencije. Zamena backenda značila bi promenu jedne
> konstante `apiUrl` u servisima, ništa više.

**„Je li ovo prava komunikacija ili si podatke zakucao u kod?"**
> Prava. Mogu da otvorim Network tab i pokažem zahteve, i da otvorim `db.json` — vidi se da
> se menja kad dodam ili obrišem zadatak. (I pokaži to — traje deset sekundi.)

**„Šta bi se promenilo sa pravim backendom?"**
> Četiri stvari, sve na tankom sloju oko servisa:
> 1. `apiUrl` bi pokazivao na pravi API (ili bi išao kroz `environment` fajl);
> 2. prijava bi bila POST `/login`, a odgovor JWT token, koji bi **interceptor**
>    (`HttpInterceptorFn`) dodavao svakom zahtevu u `Authorization` zaglavlje;
> 3. lozinke bi bile heširane na serveru, a validacija bi se ponovila serverski;
> 4. liste bi verovatno bile paginirane (`MatPaginator` + query parametri).
>
> Komponente, rute, forme i pipe-ovi ostali bi nepromenjeni — to je poenta razdvajanja
> slojeva. (Ako pitaju da vidi interceptor — imam ga urađenog u primerima za Kolokvijum II.)

**„Ova prijava nije bezbedna."**
> Tačno, i toga sam svestan: lozinka putuje kao query parametar jer JSON Server ne ume
> ništa drugo, a guard štiti samo klijentsku stranu — ko zna adresu API-ja, može da je
> pozove direktno. Klijentska zaštita je stvar korisničkog iskustva; prava zaštita mora biti
> na serveru. Vidi i poglavlje 04, odeljak C.

**„Zašto se podaci gube kad promenim `db.json`?"**
> Ne gube se — JSON Server upisuje u taj fajl. Ako ga ručno izmenim dok radi, `--watch`
> ga ponovo učita.

---

## 5. Trik za demonstraciju (deset sekundi, jak utisak)

Otvori `db.json` u editoru pored aplikacije i uradi jedno brisanje zadatka kroz interfejs.
Fajl se ažurira uživo, pred profesorom. Time si u jednom potezu pokazao:
DELETE zahtev → obradu odgovora → osvežavanje tabele → stvarnu promenu na „serveru".

Isto važi i za dodavanje: novi zadatak dobija `id` **od servera**, ne od tebe — dokaz da
POST radi kako treba.
