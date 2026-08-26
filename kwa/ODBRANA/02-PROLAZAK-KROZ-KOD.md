# 02 — Prolazak kroz kod, fajl po fajl

Za svaki fajl: šta radi, koje mehanizme Angulara pokazuje i **rečenica koju izgovaraš**.

---

## `src/main.ts` — ulazna tačka

```ts
bootstrapApplication(AppComponent, appConfig).catch(err => console.error(err));
```

> „Aplikacija se pokreće bez ijednog `NgModule`-a: `bootstrapApplication` dobija korensku
> komponentu i konfiguraciju sa globalnim provajderima."

---

## `src/app/app.config.ts` — globalni provajderi

```ts
providers: [
  provideRouter(routes),        // ruter i definicije ruta
  provideHttpClient(),          // HttpClient dostupan svim servisima
  provideAnimationsAsync()      // animacije koje Material koristi, učitane lenjo
]
```

> „Ovo su tri stvari koje su potrebne celoj aplikaciji. Bez `provideHttpClient()` nijedan
> servis ne bi mogao da dobije `HttpClient` — to je zamena za nekadašnji `HttpClientModule`."

---

## `src/app/app.routes.ts` — rute i guard

```ts
{ path: 'projekti/:id', component: ProjekatDetaljiComponent, canActivate: [authGuard] }
```

> „Svaka ruta mapira URL na komponentu. Dvotačka označava parametar rute. `canActivate`
> prima listu guardova koje router poziva **pre** aktivacije rute."

Pripremi odgovor: zašto `redirectTo` sa `pathMatch: 'full'`?
> „Bez `pathMatch: 'full'` prazna putanja bi se poklapala sa prefiksom svake rute i sve bi
> se preusmeravalo u krug."

---

## `src/app/app.component.ts` + `.html` — korenska komponenta

```ts
korisnik$: Observable<Korisnik | null>;
constructor(private authService: AuthService, private router: Router) {
  this.korisnik$ = this.authService.korisnik$;
}
odjava(): void { this.authService.odjava(); this.router.navigate(['/login']); }
```

```html
<ng-container *ngIf="korisnik$ | async as korisnik">
  <span class="korisnik"><mat-icon>person</mat-icon> {{ korisnik.imeIPrezime }}</span>
  <button mat-button (click)="odjava()">Odjava</button>
</ng-container>
<router-outlet></router-outlet>
```

Tri stvari koje ovde pokazuješ:

1. **`async` pipe** — sam se pretplati na Observable i sam otkaže pretplatu kada se
   komponenta ukloni. Nema ručnog `subscribe`/`unsubscribe`.
2. **`as korisnik`** — rezultat se smešta u lokalnu promenljivu šablona, pa se koristi
   `korisnik.imeIPrezime`.
3. **`<router-outlet>`** — mesto gde router ubacuje komponentu aktivne rute.

> „Toolbar je zajednički za sve strane. Deo sa navigacijom i imenom se prikazuje samo kada
> `korisnik$` emituje korisnika različitog od `null` — zato se pri odjavi sam sakrije."

---

## `src/app/models/` — modeli

```ts
export interface Projekat { id: number; naziv: string; opis: string; rokRealizacije: string; }
```

> „Modeli su TypeScript interfejsi — postoje samo u vreme kompajliranja i služe za proveru
> tipova. Rok je string u ISO formatu jer JSON nema tip za datum; za prikaz koristim `DatePipe`."

`zadatak.model.ts` dodatno sadrži **enume** i **mape opisa** — vidi `01-ARHITEKTURA.md`, tačka 7.

> „Enum sam koristio jer specifikacija traži da se status i prioritet čuvaju kao brojevi.
> Enum daje čitljiva imena u kodu (`StatusZadatka.Zavrseno`), a u JSON-u ostaje broj 2."

---

## `src/app/services/auth.service.ts` — prijava i sesija

```ts
private korisnikSubject = new BehaviorSubject<Korisnik | null>(this.ucitajIzStorage());
korisnik$ = this.korisnikSubject.asObservable();

prijava(korisnickoIme: string, lozinka: string): Observable<Korisnik | null> {
  return this.http.get<Korisnik[]>(this.apiUrl, { params: { korisnickoIme, lozinka } })
    .pipe(map(korisnici => {
      const korisnik = korisnici.length > 0 ? korisnici[0] : null;
      if (korisnik) {
        this.korisnikSubject.next(korisnik);
        localStorage.setItem(this.storageKljuc, JSON.stringify(korisnik));
      }
      return korisnik;
    }));
}
```

Šta pokazati:

- `params: { … }` — Angular gradi `?korisnickoIme=blagoje&lozinka=blagoje123`;
  JSON Server podržava filtriranje po poljima, pa neprazan niz znači uspešnu prijavu.
- `map(...)` — RxJS operator koji **transformiše** ono što Observable emituje: niz → jedan
  korisnik ili `null`. Komponenta dobija gotov rezultat, bez logike o nizovima.
- `next()` + `localStorage` — dva mesta gde se pamti sesija: u memoriji (za reaktivnost)
  i u pregledaču (da preživi F5).
- `ucitajIzStorage()` u `try/catch` — ako je sadržaj u `localStorage` pokvaren, aplikacija
  se ne ruši nego kreće kao neprijavljena.

> „Prijava je jedini deo koji bih u pravoj aplikaciji uradio drugačije — vidi poglavlje 04,
> pitanje o bezbednosti."

---

## `src/app/services/projekat.service.ts` i `zadatak.service.ts` — REST

```ts
getZadaciZaProjekat(projekatId: number) {
  return this.http.get<Zadatak[]>(this.apiUrl, { params: { projekatId } });
}
dodajZadatak(zadatak: Omit<Zadatak, 'id'>) { return this.http.post<Zadatak>(this.apiUrl, zadatak); }
izmeniZadatak(zadatak: Zadatak)            { return this.http.put<Zadatak>(`${this.apiUrl}/${zadatak.id}`, zadatak); }
obrisiZadatak(id: number)                  { return this.http.delete<void>(`${this.apiUrl}/${id}`); }
```

> „`ZadatakService` pokriva sve četiri HTTP metode koje specifikacija traži.
> `Omit<Zadatak, 'id'>` je TypeScript tip koji kaže: isti objekat, ali bez `id` polja —
> jer identifikator dodeljuje server."

Ako pitaju PUT vs. PATCH:
> „PUT zamenjuje ceo resurs, pa šaljem kompletan objekat; PATCH bi menjao samo poslata polja.
> JSON Server podržava oba."

Ako pitaju zašto servis vraća `Observable`, a ne gotove podatke:
> „Zato što je poziv asinhron. Servis vraća „recept" za zahtev; zahtev se šalje tek kad se
> komponenta pretplati. Tako komponenta odlučuje kada i kako da reaguje na odgovor i grešku."

---

## `src/app/guards/auth.guard.ts` — zaštita ruta

```ts
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  if (authService.jePrijavljen()) return true;
  return router.createUrlTree(['/login']);
};
```

> „Guard je obična funkcija tipa `CanActivateFn`. Router je poziva pre aktivacije rute.
> Ako vrati `true`, navigacija ide dalje; ako vrati `UrlTree`, router preusmerava.
> Zavisnosti dobijam funkcijom `inject()`, jer u funkciji nema konstruktora."

Zašto `UrlTree`, a ne `router.navigate(['/login'])`?
> „Zato što je `navigate` sporedni efekat koji pokreće **novu** navigaciju dok stara još
> traje. Vraćanjem `UrlTree` router sam otkazuje tekuću i odmah izvršava preusmerenje —
> to je preporučeni način."

---

## `src/app/pipes/status.pipe.ts` i `prioritet.pipe.ts`

```ts
@Pipe({ name: 'status', standalone: true })
export class StatusPipe implements PipeTransform {
  transform(vrednost: StatusZadatka): string { return STATUS_OPISI[vrednost] ?? '?'; }
}
```

> „Pipe je transformacija vrednosti za prikaz. Klasa ima dekorator `@Pipe`, implementira
> `PipeTransform` i metodu `transform`. U šablonu se koristi kao `{{ zadatak.status | status }}`.
> Ovako korisnik nikad ne vidi broj, a model ostaje numerički — kako specifikacija traži."

Dodatak ako pitaju o vrstama pipe-ova:
> „Podrazumevano su pipe-ovi *pure* — izvršavaju se samo kada se ulazna vrednost promeni,
> što je efikasno. *Impure* pipe (`pure: false`) izvršava se pri svakoj proveri promena i
> koristi se retko, npr. za filtriranje liste koja se menja u mestu."

---

## `src/app/components/login/login.component.ts` — reactive forma

```ts
this.loginForma = this.fb.group({
  korisnickoIme: ['', [Validators.required, Validators.minLength(3)]],
  lozinka: ['', [Validators.required, Validators.minLength(6)]]
});

prijaviSe(): void {
  if (this.loginForma.invalid) { this.loginForma.markAllAsTouched(); return; }
  this.uToku = true;
  const { korisnickoIme, lozinka } = this.loginForma.value;
  this.authService.prijava(korisnickoIme, lozinka).subscribe({
    next: (korisnik) => { … router.navigate(['/projekti']) … },
    error: () => { … snackBar … }
  });
}
```

> „Reactive forma se definiše u TypeScript-u: `FormBuilder.group` pravi `FormGroup`, svaka
> kontrola dobija početnu vrednost i listu validatora. U šablonu se forma veže sa
> `[formGroup]`, a polja sa `formControlName`."

- `markAllAsTouched()` — bez toga Material ne prikazuje greške dok korisnik ne dodirne polje;
  pri praznoj formi i kliku na dugme ništa se ne bi videlo.
- `uToku` — sprečava dvostruko slanje; dugme je `[disabled]="uToku"`.
- `subscribe({ next, error })` — obavezno i `error`, jer server može biti ugašen.

Template-driven vs. reactive:
> „Template-driven forma se definiše u HTML-u kroz `ngModel` i brža je za jednostavne
> slučajeve; reactive forma živi u TypeScript-u, lakše se validira i testira. Ovde sam
> koristio reactive, što je i navedeno kao dodatna funkcionalnost."

---

## `src/app/components/projekti/projekti.component.ts` — lista i sortiranje

```ts
ngOnInit(): void {
  this.projekatService.getProjekti().subscribe({
    next: (projekti) => { this.projekti = projekti; this.sortiraj(); this.ucitavanje = false; },
    error: () => { this.ucitavanje = false; this.snackBar.open('Greška…'); }
  });
}

private sortiraj(): void {
  this.projekti.sort((a, b) => this.sortiranjePo === 'naziv'
    ? a.naziv.localeCompare(b.naziv, 'sr')
    : a.rokRealizacije.localeCompare(b.rokRealizacije));
}
```

> „Podaci se učitavaju u `ngOnInit` — to je lifecycle hook koji se poziva jednom, nakon što
> Angular napravi komponentu i postavi `@Input` vrednosti. U konstruktoru se to ne radi jer
> on služi samo za dependency injection."

> „`localeCompare` sa oznakom jezika ispravno poredi naša slova (č, ć, š, ž, đ). Rok je ISO
> datum `YYYY-MM-DD`, pa je poređenje stringova ujedno i hronološko."

`ucitavanje` zastavica + `<mat-spinner *ngIf="ucitavanje">` — pokazuje da si mislio na
korisnika dok traje zahtev.

---

## `src/app/components/projekat-detalji/projekat-detalji.component.ts`

```ts
const id = Number(this.route.snapshot.paramMap.get('id'));
this.projekatService.getProjekat(id).subscribe({ … });
```

```html
<app-zadaci [projekatId]="projekat.id"></app-zadaci>
```

> „Parametar rute čitam iz `ActivatedRoute`. `snapshot` je trenutna vrednost — dovoljna jer
> se pri promeni id-ja komponenta ponovo pravi. Da sam sa iste strane menjao id bez
> ponovnog kreiranja komponente, morao bih da se pretplatim na `route.paramMap`."

> „Parametri rute su uvek stringovi, zato `Number(...)`."

---

## `src/app/components/zadaci/zadaci.component.ts` — tabela, filter, sort, brisanje

```ts
@Input({ required: true }) projekatId!: number;

dataSource = new MatTableDataSource<Zadatak>([]);
prikazaneKolone = ['opis', 'status', 'prioritet', 'akcije'];

@ViewChild(MatSort) set matSort(sort: MatSort) { this.dataSource.sort = sort; }

ngOnInit(): void {
  this.dataSource.filterPredicate = (zadatak) => {
    const statusOk = this.filterStatus === null || zadatak.status === this.filterStatus;
    const prioritetOk = this.filterPrioritet === null || zadatak.prioritet === this.filterPrioritet;
    return statusOk && prioritetOk;
  };
  this.ucitajZadatke();
}

primeniFilter(): void { this.dataSource.filter = 'primeni'; }
```

Ovo je najgušća komponenta — pripremi četiri objašnjenja:

1. **`@Input({ required: true })`** — Angular prijavljuje grešku pri kompajliranju ako
   roditelj ne prosledi `projekatId`. Uzvičnik govori TypeScript-u da će vrednost postojati.
2. **`MatTableDataSource`** — umesto običnog niza, jer ima ugrađeno sortiranje, filtriranje
   i (po potrebi) paginaciju.
3. **`filterPredicate`** — funkcija koja za svaki red vraća `true`/`false`. Standardno
   Material filtrira po tekstu; ovde sam napisao svoj predikat koji gleda dva izabrana filtera.
   `dataSource.filter = 'primeni'` je okidač — Material pokreće filtriranje kada se to polje
   promeni, a vrednost mora biti neprazan string.
4. **`@ViewChild(MatSort) set …`** — setter, a ne obično polje. Angular ga poziva kada
   **razreši view query**, tj. kada se šablon iscrta (oko `ngAfterViewInit`), i **ponovo**
   ako element kasnije nestane ili se pojavi (npr. iza `*ngIf`/`@if`) — tada stiže i
   `undefined`. U ovoj komponenti tabela **nije** iza `*ngIf` (uvek je iscrtana), pa bi
   ekvivalentno radilo i obično polje uz dodelu u `ngAfterViewInit`:

   ```ts
   @ViewChild(MatSort) sort!: MatSort;
   ngAfterViewInit(): void { this.dataSource.sort = this.sort; }
   ```

   Setter je izabran kao odbrambena navika: radi i kad se tabela uslovno prikazuje, i ne
   zavisi od toga da li si zapamtio da dodaš `ngAfterViewInit`. Ako te pitaju — to je
   tačan odgovor, ne izmišljaj `*ngIf` koji ovde ne postoji.

Brisanje sa dialogom:

```ts
const dialogRef = this.dialog.open(ConfirmDialogComponent, { data: { naslov, poruka } });
dialogRef.afterClosed().subscribe((potvrdjeno: boolean) => {
  if (!potvrdjeno) return;
  this.zadatakService.obrisiZadatak(zadatak.id).subscribe({ next: … , error: … });
});
```

> „`dialog.open` vraća referencu na dialog; `afterClosed()` je Observable koji emituje
> rezultat kada se dialog zatvori. DELETE šaljem samo ako je korisnik potvrdio."

---

## `src/app/components/zadatak-forma/zadatak-forma.component.ts` — dve rute, jedna forma

```ts
this.projekatId = Number(this.route.snapshot.paramMap.get('projekatId'));
const idParam = this.route.snapshot.paramMap.get('id');
this.zadatakId = idParam !== null ? Number(idParam) : null;

get jeIzmena(): boolean { return this.zadatakId !== null; }

if (this.jeIzmena) {
  this.zadatakService.getZadatak(this.zadatakId!).subscribe({
    next: (zadatak) => this.forma.patchValue({ opis: zadatak.opis, status: zadatak.status, prioritet: zadatak.prioritet })
  });
}
```

> „Režim prepoznajem po tome da li ruta ima parametar `:id`. U režimu izmene dohvatim zadatak
> i popunim formu metodom `patchValue` — ona postavlja samo navedene kontrole, za razliku od
> `setValue` koja zahteva sve."

```ts
sacuvaj(): void {
  if (this.forma.invalid) { this.forma.markAllAsTouched(); return; }
  if (this.jeIzmena) { /* PUT sa kompletnim objektom */ }
  else { /* POST bez id polja */ }
}
```

> „Validacija je na dva nivoa: `Validators` u definiciji forme i provera `forma.invalid` pre
> slanja. Posle uspešnog čuvanja prikazujem snackbar i vraćam se na detalje projekta."

---

## `src/app/components/confirm-dialog/confirm-dialog.component.ts`

```ts
constructor(@Inject(MAT_DIALOG_DATA) public podaci: ConfirmDialogPodaci) {}
```

> „Dialog je generička komponenta — naslov i poruku prima kroz injection token
> `MAT_DIALOG_DATA`, pa se može koristiti za potvrdu bilo koje akcije. Rezultat vraća kroz
> `[mat-dialog-close]="true"` u šablonu."

---

## `src/app/components/statistika/statistika.component.ts`

```ts
private izracunaj(zadaci: Zadatak[], opisi: Record<number, string>, selektor: (z: Zadatak) => number) {
  return Object.entries(opisi).map(([broj, naziv]) => {
    const vrednost = Number(broj);
    const koliko = zadaci.filter(z => selektor(z) === vrednost).length;
    return { naziv, broj: koliko, procenat: this.ukupno > 0 ? Math.round(koliko / this.ukupno * 100) : 0 };
  });
}
```

> „Ista metoda računa statistiku i po statusu i po prioritetu — razlikuje se samo mapa opisa
> i funkcija koja iz zadatka izvlači polje. Funkcija kao parametar (`selektor`) je razlog
> zašto nema duplirane logike. Deljenje nulom je pokriveno proverom `ukupno > 0`."

---

## `db.json` — podaci

```json
{ "korisnici": [...], "projekti": [...], "zadaci": [...] }
```

> „Svaki ključ u `db.json` JSON Server pretvara u REST resurs sa svim CRUD rutama. Podaci
> su izabrani tako da pokrivaju sve statuse i prioritete — tri projekta i osam zadataka —
> da se sve funkcionalnosti mogu demonstrirati bez unosa novih podataka."
