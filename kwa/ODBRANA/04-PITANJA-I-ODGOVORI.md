# 04 — Pitanja i odgovori

Podeljeno na: opšta, o projektu, „neprijatna" (slabosti rešenja) i „uradi uživo".

---

## A. Opšta pitanja o Angularu

**Zašto Angular, a ne čist JavaScript?**
Zato što daje gotovu strukturu: komponente, DI, rutiranje, HTTP klijent i detekciju promena.
Ne pišem ručno manipulaciju DOM-om niti sopstveni sistem za organizaciju koda.

**Šta je TypeScript i šta dobijam njime?**
Nadskup JavaScript-a sa tipovima. Greške tipa se otkrivaju pri kompajliranju, editor nudi
auto-dopunu, a interfejsi dokumentuju oblik podataka. U pregledaču se izvršava običan JS.

**Šta je komponenta?**
Klasa sa `@Component` dekoratorom koja spaja šablon, stil i logiku, i ima svoj selektor.

**Šta je servis i zašto ga koristim?**
Klasa sa `@Injectable` koja sadrži logiku nezavisnu od prikaza — kod mene komunikaciju sa
serverom. Deli se između komponenti (singleton), drži logiku na jednom mestu i lako se menja.

**Šta je dependency injection?**
Klasa ne pravi svoje zavisnosti sa `new`, nego ih traži kroz konstruktor ili `inject()`, a
Angular joj ih dostavlja iz injektora.

**Šta je Observable i po čemu se razlikuje od Promise-a?**
Tok vrednosti u vremenu. Promise kreće odmah i daje jednu vrednost; Observable je lenj
(kreće tek na `subscribe`), može emitovati više vrednosti, može se otkazati i podržava
operatore poput `map` i `filter`.

**Kako se komponente iscrtavaju ponovo kada se podaci promene?**
Angular kroz Zone.js prati asinhrone događaje (klik, HTTP odgovor, tajmer) i posle svakog
proverava stablo komponenti, pa osvežava ono što se promenilo. Postoje i `OnPush` strategija
i signali koji tu proveru sužavaju.

**Šta je SPA?**
Aplikacija na jednoj strani: HTML se učita jednom, a dalje JavaScript menja prikaz i dohvata
podatke REST pozivima, bez ponovnog učitavanja strane.

---

## B. Pitanja o ovom projektu

**Opiši arhitekturu.**
Četiri sloja: šabloni → komponente → servisi → JSON Server, uz modele, pipe-ove, guard i
router koji ih presecaju. Komponente ne znaju za HTTP, servisi ne znaju za prikaz.

**Koliko imaš komponenti i koje?**
Sedam plus korenska: login, projekti, projekat-detalji, zadaci, zadatak-forma, statistika,
confirm-dialog i `AppComponent`.

**Koje modele imaš?**
Tri: `Projekat`, `Zadatak`, `Korisnik` — specifikacija traži najmanje dva.

**Kako radi prijava?**
`LoginComponent` (reactive forma) šalje korisničko ime i lozinku `AuthService`-u; on radi GET
`/korisnici?korisnickoIme=…&lozinka=…`. Ako server vrati neprazan niz, korisnik se upisuje u
`BehaviorSubject` i u `localStorage`, a router prelazi na `/projekti`.

**Gde čuvaš prijavljenog korisnika i zašto na dva mesta?**
U `BehaviorSubject`-u — da bi delovi interfejsa reagovali na promenu; i u `localStorage` —
da prijava preživi osvežavanje strane. `BehaviorSubject` je privatan, spolja je izložen samo
`korisnik$` kao `Observable`, da niko ne može da mu „ubaci" vrednost.

**Kako funkcioniše zaštita ruta?**
Rute imaju `canActivate: [authGuard]`. Guard je funkcija koju router zove pre aktivacije:
vraća `true` ako je korisnik prijavljen, inače `router.createUrlTree(['/login'])`, što je
preusmerenje.

**Koje HTTP metode koristiš i gde?**
GET — korisnici, projekti, zadaci; POST — dodavanje zadatka; PUT — izmena zadatka;
DELETE — brisanje zadatka. Sve u `services/`.

**Kako dohvataš zadatke samo jednog projekta?**
GET `/zadaci?projekatId=1` — JSON Server filtrira po polju, pa ne povlačim sve pa filtriram
na klijentu.

**Kako je urađeno filtriranje po statusu i prioritetu?**
Kroz `MatTableDataSource.filterPredicate` — sopstvena funkcija koja za svaki red proverava
oba izabrana filtera. Promena padajuće liste postavi `dataSource.filter`, što okida
filtriranje.

**Zašto su status i prioritet brojevi?**
Tako traži specifikacija: u modelu numeričke vrednosti (enumi), a korisniku se uvek prikazuje
tekst. Prevod radi pipe (`| status`, `| prioritet`), a opisi su na jednom mestu u
`zadatak.model.ts`.

**Šta je pipe i zašto si napravio svoje?**
Transformacija vrednosti za prikaz. Svoje sam napravio da bih broj 2 prikazao kao „Završeno"
bez menjanja modela — i to jednom, za sve šablone.

**Kako jedna komponenta služi i za dodavanje i za izmenu?**
Dve rute vode na `ZadatakFormaComponent`; ako ruta ima parametar `:id`, komponenta dohvati
zadatak i popuni formu (`patchValue`) i čuva PUT-om, inače šalje POST bez `id` polja.

**Kako radi validacija?**
`FormBuilder.group` definiše kontrole sa validatorima (`required`, `minLength`, `maxLength`).
Pri slanju proveravam `forma.invalid` i pozivam `markAllAsTouched()` da se greške prikažu;
poruke su `mat-error` u šablonu.

**Kako komuniciraju `ProjekatDetaljiComponent` i `ZadaciComponent`?**
Roditelj → dete kroz `@Input() projekatId`. Dete samo dohvata svoje zadatke servisom.

**Kako je urađeno brisanje sa potvrdom?**
`MatDialog` otvara `ConfirmDialogComponent` kome kroz `MAT_DIALOG_DATA` prosleđujem naslov i
poruku. `afterClosed()` vraća `true`/`false`; DELETE se šalje samo na `true`.

**Šta je JSON Server?**
Alat koji od `db.json` fajla pravi REST API sa svim CRUD rutama; koristi se kao simulacija
backend-a. Pokreće se skriptom `npm run server`.

**Šta bi se desilo da server nije pokrenut?**
Svaki `subscribe` ima i `error` granu — korisnik dobije snackbar poruku, a aplikacija ne puca.

---

## C. „Neprijatna" pitanja — slabosti rešenja

Ova pitanja se postavljaju da provere razumeš li granice svog rešenja. Iskren odgovor
sa predlogom ispravke vredi više od izbegavanja.

**Šalješ lozinku kao query parametar u GET zahtevu — je li to bezbedno?**
Nije. Lozinka završi u URL-u, u istoriji pregledača i u logovima servera. Tako je urađeno
zato što JSON Server nema pravu autentifikaciju i podržava samo filtriranje po poljima. U
pravoj aplikaciji bio bi POST `/login` sa telom zahteva, lozinka čuvana kao heš (bcrypt), a
server bi vraćao JWT token koji se šalje u `Authorization` zaglavlju.

**Guard sprečava pristup, ali šta ako neko direktno pozove API?**
Dobio bi podatke — zaštita je samo na klijentu. Klijentski guard je stvar korisničkog
iskustva, prava zaštita mora biti na serveru. Server sa vežbi za Kolokvijum II upravo to radi:
proverava JWT token i uloge po putanji.

**Zašto nema interceptora?**
Zato što nema tokena koji bi se dodavao — prijava vraća objekat korisnika, ne token. Sa JWT
autentifikacijom dodao bih `HttpInterceptorFn` koji svakom zahtevu dodaje `Authorization`
zaglavlje i centralno obrađuje 401/403.

**Zašto se posle brisanja ponovo učitavaju svi zadaci?**
Radi sigurnosti — prikaz je tada sigurno usklađen sa serverom. Optimizacija bi bila lokalno
uklanjanje iz niza bez novog GET-a; kod ovako malih tabela razlika je zanemarljiva.

**`dataSource.filter = 'primeni'` izgleda kao trik. Zašto tako?**
Jeste trik, i namerno je. `MatTableDataSource` pokreće filtriranje tek kada se promeni polje
`filter`, a moj predikat ne koristi tu vrednost nego polja `filterStatus` i `filterPrioritet`.
Dodela bilo kog nepraznog stringa služi kao okidač. Alternativa bi bila da u `filter` upišem
JSON sa oba kriterijuma i da ga u predikatu parsiram.

**Zašto nema paginacije?**
Podataka je malo. `MatPaginator` se dodaje u dve linije: `<mat-paginator>` u šablonu i
`this.dataSource.paginator = paginator` kroz `@ViewChild`.

**Zašto nema CRUD-a nad projektima, nego samo nad zadacima?**
Specifikacija traži CRUD nad zadacima; projekti se samo pregledaju. `ProjekatService` je
pripremljen tako da se dodavanje i izmena dodaju istim obrascem kao u `ZadatakService`.

**Zašto nema `unsubscribe`?**
HTTP Observable emituje jednu vrednost i sam se završava, a `korisnik$` u toolbaru se koristi
kroz `async` pipe koji otkazuje pretplatu automatski. Ručno otkazivanje bi bilo potrebno kod
beskonačnih tokova (`valueChanges`, `interval`).

**Zašto nisi koristio signale, kad su noviji?**
Projekat je pisan klasičnim pristupom sa `BehaviorSubject`-om, koji je i dalje potpuno
podržan. Signale sam koristio na kolokvijumu I; ovde bih njima najlakše zamenio polja
`projekti` i `ucitavanje`, a sortiranu listu bih napravio kao `computed()`.

**Šta bi dodao da imaš još nedelju dana?**
1. JWT autentifikacija sa interceptorom i uloge (admin/korisnik).
2. CRUD nad projektima i brisanje projekta sa kaskadnim brisanjem zadataka.
3. Lazy loading ruta i `OnPush` detekciju.
4. Testove: `HttpTestingController` za servise, `TestBed` za komponente.

---

## D. „Uradi uživo" — male izmene koje mogu da traže

### 1. Dodaj novo polje u zadatak (npr. `rok`)

```ts
// zadatak.model.ts
export interface Zadatak { … rok: string; }
```
```ts
// zadatak-forma.component.ts — u fb.group
rok: ['', Validators.required]
```
```html
<!-- zadatak-forma.component.html -->
<mat-form-field appearance="outline">
  <mat-label>Rok</mat-label>
  <input matInput type="date" formControlName="rok">
</mat-form-field>
```
```ts
// zadaci.component.ts
prikazaneKolone = ['opis', 'rok', 'status', 'prioritet', 'akcije'];
```
```html
<!-- nova kolona u tabeli -->
<ng-container matColumnDef="rok">
  <th mat-header-cell *matHeaderCellDef mat-sort-header>Rok</th>
  <td mat-cell *matCellDef="let z">{{ z.rok | date:'dd.MM.yyyy.' }}</td>
</ng-container>
```
Ne zaboravi da polje dodaš i u objekte koji se šalju u `sacuvaj()`.

### 2. Dodaj novi status („Otkazano")

```ts
export enum StatusZadatka { Novo = 0, UToku = 1, Zavrseno = 2, Otkazano = 3 }
export const STATUS_OPISI: Record<StatusZadatka, string> = {
  …, [StatusZadatka.Otkazano]: 'Otkazano'
};
```
I to je sve — padajuće liste, filteri, pipe i statistika se pune iz iste mape.
**To je i poenta koju treba naglasiti: opisi su na jednom mestu.**

### 3. Zaštiti rutu ulogom (npr. samo admin vidi statistiku)

```ts
// korisnik.model.ts
export interface Korisnik { …; uloga: string; }

// guards/uloga.guard.ts
export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.trenutniKorisnik()?.uloga === 'admin' ? true : router.createUrlTree(['/projekti']);
};

// app.routes.ts
{ path: 'statistika', component: StatistikaComponent, canActivate: [authGuard, adminGuard] }
```
Guardovi se izvršavaju redom; prvi koji ne vrati `true` prekida navigaciju.

### 4. Dodaj pretragu zadataka po opisu

```ts
tekstPretrage = '';
// u filterPredicate dodaj:
const tekstOk = !this.tekstPretrage ||
  zadatak.opis.toLowerCase().includes(this.tekstPretrage.toLowerCase());
return statusOk && prioritetOk && tekstOk;
```
```html
<mat-form-field appearance="outline">
  <mat-label>Pretraga</mat-label>
  <input matInput [(ngModel)]="tekstPretrage" [ngModelOptions]="{standalone: true}"
         (ngModelChange)="primeniFilter()">
</mat-form-field>
```
(`[ngModelOptions]="{standalone: true}"` jer je polje van reactive forme; traži `FormsModule`.)

### 5. Prebaci rutu na lazy loading

```ts
{
  path: 'statistika',
  loadComponent: () => import('./components/statistika/statistika.component')
                        .then(m => m.StatistikaComponent),
  canActivate: [authGuard]
}
```
Uz to se uklanja `import` te komponente sa vrha `app.routes.ts`.

---

## E. Rečenice za izlaz iz neprilike

- Ako ne znaš odgovor:
  > „Nisam to koristio u projektu. Znam čemu služi — ... — ali nisam imao potrebu."
  Bolje nego pogađati.
- Ako nešto ne radi uživo:
  > „Proveriću da li je JSON Server pokrenut i da li je port 3000 zauzet."
  Devet od deset problema uživo su upravo to.
- Ako te pitaju za deo koda koji si zaboravio:
  > „Mogu da otvorim fajl i prođemo kroz njega."
  Uz svaki fajl u projektu stoji i `.md` sa objašnjenjem — slobodno ga otvori.
