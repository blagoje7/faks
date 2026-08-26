# 03 — Mogućnosti Angulara i gde su upotrebljene

Tabela na kraju je „šlagvort": za svaku mogućnost okvira imaš kratko objašnjenje, primer iz
**ovog** projekta (ili iskrenu napomenu da nije korišćena) i rečenicu kako bi je dodao.

---

## 1. Komponente i šabloni

Komponenta = klasa sa `@Component` + šablon + stil. Aplikacija je stablo komponenti.

- **Enkapsulacija stilova**: CSS napisan u `zadaci.component.css` važi samo za tu komponentu
  (Angular dodaje atribute tipa `_ngcontent-abc`). Zato `.kartica` u jednoj komponenti ne
  kvari `.kartica` u drugoj.
- **Standalone** (ovde svuda): komponenta sama navodi zavisnosti u `imports`, bez `NgModule`.
- **Projekcija sadržaja** (`<ng-content>`) nije korišćena. Kada bi trebala: da napraviš
  „omotač" komponentu (npr. panel sa naslovom) u koji roditelj ubacuje proizvoljan HTML.

Vezivanje podataka — sve četiri vrste postoje u projektu:

| Vrsta | Primer iz projekta |
|---|---|
| Interpolacija | `{{ projekat.naziv }}` |
| Property binding | `[projekatId]="projekat.id"`, `[disabled]="uToku"` |
| Event binding | `(click)="obrisiZadatak(zadatak)"`, `(ngSubmit)="prijaviSe()"` |
| Dvosmerno | `[(ngModel)]` — **nije korišćeno**, jer su forme reactive |

---

## 2. Direktive

| Vrsta | Šta radi | U projektu |
|---|---|---|
| Komponenta | direktiva sa šablonom | sve komponente |
| Strukturna | dodaje/uklanja elemente | `*ngIf`, `*ngFor`, `*matCellDef`, `*matNoDataRow` |
| Atributska | menja izgled/ponašanje | `routerLink`, `matInput`, `mat-button`, `matSort` |

> „Material komponente su najvećim delom atributske direktive — `mat-raised-button` je atribut
> na običnom `<button>`, ne poseban tag."

Sopstvena direktiva nije pravljena u ovom projektu (nije bila potrebna), ali je pravljena na
vežbama i kolokvijumu I. Ako pitaju kako bi je dodao:

```ts
@Directive({ selector: '[appIstakniRok]', standalone: true })
export class IstakniRok {
  private el = inject(ElementRef<HTMLElement>);
  @Input() set appIstakniRok(rok: string) {
    const istekao = new Date(rok) < new Date();
    this.el.nativeElement.style.color = istekao ? 'red' : '';
  }
}
```
Upotreba: `<span [appIstakniRok]="projekat.rokRealizacije">…</span>`.

Nova sintaksa `@if` / `@for` (Angular 17+) je moderna zamena za `*ngIf` / `*ngFor`.
U projektu su korišćene stare direktive, što je potpuno ispravno i podržano.
Ekvivalent:

```html
<!-- staro -->
<mat-card *ngFor="let projekat of projekti">…</mat-card>
<!-- novo -->
@for (projekat of projekti; track projekat.id) { <mat-card>…</mat-card> }
```

---

## 3. Pipe-ovi

- **Ugrađeni**: `date` (`{{ rok | date:'dd.MM.yyyy.' }}`), `async` (u toolbaru).
- **Sopstveni**: `status` i `prioritet` — prevode brojeve u tekst.
- **Parametri**: pipe prima argumente posle dvotačke (`date:'dd.MM.yyyy.'`).
- **Pure vs. impure**: podrazumevano pure — izvršava se samo kad se promeni ulaz.

> „Pipe je najčistiji način da se podatak prikaže drugačije nego što je zapisan, bez menjanja
> modela — što je ovde bio izričit zahtev za status i prioritet."

---

## 4. Dependency injection

- `@Injectable({ providedIn: 'root' })` → jedna instanca (singleton) za celu aplikaciju,
  napravljena lenjo, pri prvom traženju.
- Ubrizgavanje kroz **konstruktor** (svi servisi i komponente ovde) ili funkcijom
  **`inject()`** (u `auth.guard.ts`, jer funkcija nema konstruktor).
- **Injection token**: `MAT_DIALOG_DATA` — način da se ubrizga vrednost koja nije klasa;
  koristi se u `confirm-dialog.component.ts`.
- Hijerarhija injektora: provajder naveden u `@Component({ providers: [...] })` daje
  **novu instancu po komponenti** — korisno kada svaka instanca treba svoje stanje.

> „Zahvaljujući DI, komponente ne prave servise sa `new`, nego ih traže. Zato sve komponente
> dele isti `AuthService`, pa toolbar zna ko je prijavljen iako je prijava obavljena u
> `LoginComponent`."

---

## 5. Servisi i deljenje stanja

Tri obrasca za deljenje podataka između komponenti:

1. **Roditelj → dete**: `@Input()` — `<app-zadaci [projekatId]="…">`.
2. **Dete → roditelj**: `@Output()` + `EventEmitter` — nije korišćeno ovde
   (dete samo dohvata svoje podatke), ali je obrazac sa kolokvijuma I.
3. **Bilo koje dve komponente**: **servis sa `BehaviorSubject`** — `AuthService.korisnik$`,
   koji sluša toolbar u `AppComponent`.

> „Treći način rešava komunikaciju komponenti koje nisu u odnosu roditelj-dete — kod mene su
> to `LoginComponent` i toolbar u `AppComponent`."

---

## 6. Rutiranje

Korišćeno u projektu:

| Mogućnost | Gde |
|---|---|
| definicija ruta | `app.routes.ts` |
| `<router-outlet>` | `app.component.html` |
| navigacija iz šablona | `routerLink="/projekti"`, `[routerLink]="['/projekti', id]"` |
| navigacija iz koda | `router.navigate(['/projekti', this.projekatId])` |
| parametri rute | `projekti/:id`, čitanje kroz `ActivatedRoute` |
| preusmerenja i wildcard | `redirectTo`, `path: '**'` |
| guard | `canActivate: [authGuard]` |

Postoji, a nije korišćeno (spremi jednu rečenicu za svako):

- **Query parametri** (`/projekti?strana=2`) — čitaju se iz `route.queryParamMap`.
- **Child rute** — ugnježdene rute sa sopstvenim `<router-outlet>`.
- **Lazy loading**: `{ path: 'statistika', loadComponent: () => import('./…').then(m => m.StatistikaComponent) }`
  — komponenta se preuzima tek kada korisnik ode na tu rutu, pa je početni paket manji.
- **Resolver** — dohvata podatke **pre** aktivacije rute, pa se komponenta prikaže već sa
  podacima (alternativa učitavanju u `ngOnInit`).
- **`CanDeactivate` guard** — upozorenje „imate nesačuvane izmene" pri napuštanju forme.

> „Sve rute su eagerno učitane jer je aplikacija mala. Da raste, prvo bih na `loadComponent`
> prebacio statistiku i forme."

---

## 7. Forme

| | Template-driven | Reactive |
|---|---|---|
| Definicija | u HTML-u (`ngModel`) | u TS-u (`FormBuilder`, `FormGroup`) |
| Modul | `FormsModule` | `ReactiveFormsModule` |
| Validacija | atributi (`required`) | `Validators.*` |
| U projektu | — | login i forma zadatka |

Iskorišćeno: `FormBuilder.group`, `Validators.required / minLength / maxLength`,
`forma.invalid`, `markAllAsTouched()`, `patchValue()`, `forma.value`, `mat-error`.

Postoji, a nije korišćeno:

- **`setValue`** (traži sve kontrole) — koristio sam `patchValue`.
- **Sopstveni validator**: funkcija `(control) => ValidationErrors | null`, npr. da rok ne
  sme biti u prošlosti.
- **Asinhroni validator** — provera na serveru (npr. da li korisničko ime već postoji).
- **`FormArray`** — dinamički broj polja (npr. lista podzadataka).
- **`valueChanges`** — Observable koji emituje pri svakoj izmeni forme; tipično se koristi sa
  `debounceTime` za pretragu „dok kucaš".

---

## 8. HttpClient i RxJS

Korišćeno: `get`, `post`, `put`, `delete`, `params`, generički tipovi (`get<Zadatak[]>`),
`subscribe({ next, error })`, operator `map`, `BehaviorSubject`, `Observable`, `async` pipe.

Postoji, a nije korišćeno:

| Mogućnost | Čemu služi |
|---|---|
| **Interceptor** | presreće svaki zahtev — dodavanje `Authorization` tokena, globalna obrada grešaka, indikator učitavanja |
| `catchError` | hvatanje greške unutar `pipe`-a i vraćanje zamenske vrednosti |
| `forkJoin` | čekanje više paralelnih zahteva (npr. brisanje više zadataka odjednom) |
| `switchMap` | zahtev koji zavisi od prethodnog, bez ugnježdenih `subscribe`-ova |
| `debounceTime` | pretraga „dok kucaš", da se ne šalje zahtev na svaki taster |
| `shareReplay` | keširanje odgovora između više pretplatnika |

Ako pitaju kako bi dodao token na svaki zahtev (to je gradivo Kolokvijuma II):

```ts
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('token');
  return token ? next(req.clone({ setHeaders: { Authorization: token } })) : next(req);
};
// app.config.ts: provideHttpClient(withInterceptors([authInterceptor]))
```

---

## 9. Detekcija promena i signali

- Angular podrazumevano koristi **Zone.js**: posle svakog događaja (klik, HTTP odgovor,
  tajmer) proverava stablo komponenti i osvežava ono što se promenilo.
- **`OnPush`** strategija (`changeDetection: ChangeDetectionStrategy.OnPush`) proverava
  komponentu samo kada se promeni `@Input`, emituje događaj ili se javi Observable kroz
  `async` pipe — brže na velikim ekranima. U ovom projektu nije korišćena jer nije bilo potrebe.
- **Signali** (Angular 16+): `signal()`, `computed()`, `effect()`, `input()`, `output()`.
  Signal obaveštava Angular o promeni tačno, pa se osvežava samo zavisni deo prikaza.
  Ovaj projekat koristi klasična polja i `BehaviorSubject`; primer sa Kolokvijuma I koristi
  signale — dobro je pomenuti da poznaješ oba pristupa.

> „Signalima bih zamenio `projekti: Projekat[]` i `ucitavanje: boolean` u `ProjektiComponent`;
> sortirana lista bi tada bila `computed()` i ne bi je trebalo ručno prepravljati."

---

## 10. Životni ciklus komponente

| Hook | Kada | U projektu |
|---|---|---|
| `ngOnChanges` | pri promeni `@Input`-a | nije korišćen |
| `ngOnInit` | jednom, posle prvog postavljanja ulaza | učitavanje podataka u 5 komponenti |
| `ngAfterViewInit` | posle iscrtavanja šablona | posredno kroz `@ViewChild` setter (`MatSort`) |
| `ngOnDestroy` | pre uklanjanja komponente | nije potreban — HTTP Observable se sam završava, a `async` pipe sam otkazuje pretplatu |

> „Ručno otkazivanje pretplate bi bilo neophodno da slušam beskonačan stream — npr.
> `valueChanges` forme ili `interval`. Tada bih koristio `takeUntilDestroyed()` ili
> otkazivanje u `ngOnDestroy`."

---

## 11. Angular Material i CDK

Korišćene komponente: `MatToolbar`, `MatCard`, `MatTable` + `MatSort`, `MatFormField`,
`MatInput`, `MatSelect`, `MatButton` / `MatIconButton` / `MatButtonToggle`, `MatIcon`,
`MatDialog`, `MatSnackBar`, `MatProgressSpinner`.

> „Material je zvanična biblioteka komponenti po Material Design smernicama. Daje gotove,
> pristupačne komponente i konzistentan izgled. Ispod njega je CDK — biblioteka ponašanja
> (overlay, drag&drop, a11y) bez izgleda."

Traži `provideAnimationsAsync()` u `app.config.ts` — bez toga dialog i snackbar ne rade
kako treba.

---

## 12. Ostalo što Angular nudi (jedna rečenica po stavci)

- **CLI**: `ng new`, `ng generate component|service|pipe|guard`, `ng serve`, `ng build`,
  `ng test` — generisanje koda i build.
- **Testiranje**: Karma/Jasmine ili Vitest; `TestBed` za komponente,
  `HttpTestingController` za servise.
- **SSR / hydration**: renderovanje na serveru radi brzine prvog prikaza i SEO-a
  (`ng add @angular/ssr`).
- **i18n**: podrška za više jezika kroz `i18n` atribute i prevodilačke fajlove.
- **Animacije**: `@angular/animations` — `trigger`, `state`, `transition`.
- **PWA**: `ng add @angular/pwa` — service worker, rad offline.
- **DevTools**: proširenje za pregledač; prikazuje stablo komponenti i profajler.
- **Sigurnost**: Angular automatski sanitizuje HTML u interpolaciji (zaštita od XSS);
  zaobilazi se samo eksplicitno kroz `DomSanitizer`.

---

## 13. Sažeta tabela: mogućnost → gde je u projektu

| Mogućnost | U projektu | Fajl |
|---|---|---|
| Standalone komponente | ✅ | sve komponente |
| Interpolacija / property / event binding | ✅ | svi šabloni |
| Dvosmerno vezivanje `[(ngModel)]` | ❌ (forme su reactive) | — |
| `*ngIf` / `*ngFor` | ✅ | `projekti`, `projekat-detalji`, `zadaci` |
| Nova sintaksa `@if` / `@for` | ❌ (ekvivalent starom) | — |
| Sopstvena direktiva | ❌ | (rađeno na vežbama) |
| Ugrađeni pipe-ovi | ✅ `date`, `async` | `projekti`, `app.component` |
| Sopstveni pipe | ✅ | `pipes/status.pipe.ts`, `prioritet.pipe.ts` |
| Servisi + DI | ✅ | `services/` |
| `inject()` | ✅ | `guards/auth.guard.ts` |
| Injection token | ✅ `MAT_DIALOG_DATA` | `confirm-dialog` |
| HttpClient GET/POST/PUT/DELETE | ✅ | `zadatak.service.ts` |
| RxJS `map`, `BehaviorSubject` | ✅ | `auth.service.ts` |
| `async` pipe | ✅ | `app.component.html` |
| Interceptor | ❌ | (nema tokena — vidi gradivo K2) |
| Routing + parametri | ✅ | `app.routes.ts` |
| Guard | ✅ | `auth.guard.ts` |
| Lazy loading | ❌ | (aplikacija je mala) |
| Resolver | ❌ | (učitavanje u `ngOnInit`) |
| Reactive forme + validacija | ✅ | `login`, `zadatak-forma` |
| `@Input` | ✅ | `zadaci.component.ts` |
| `@Output` | ❌ | (rađeno na kolokvijumu I) |
| `@ViewChild` | ✅ | `zadaci.component.ts` (`MatSort`) |
| Lifecycle hookovi | ✅ `ngOnInit` | 5 komponenti |
| Signali | ❌ | (rađeno na kolokvijumu I) |
| `OnPush` detekcija | ❌ | (nije bilo potrebe) |
| Angular Material | ✅ | sve komponente |
| localStorage | ✅ | `auth.service.ts` |

Kolona sa ❌ nije slabost — to je tvoja lista tema za koje imaš pripremljen odgovor
„nije bilo potrebe, a evo kako bih to uradio".
