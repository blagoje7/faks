# 01 — Arhitektura aplikacije

Ovo poglavlje treba da umeš da nacrtaš na papiru za dva minuta.

---

## 1. Slojevi

```
┌──────────────────────────────────────────────────────────────┐
│  ŠABLONI (HTML + Angular Material)                           │
│  prikaz podataka, hvatanje korisničkih akcija                │
└───────────────▲──────────────────────────────┬───────────────┘
                │ podaci                       │ događaji
┌───────────────┴──────────────────────────────▼───────────────┐
│  KOMPONENTE (.ts)                                            │
│  stanje ekrana, reagovanje na akcije, pozivanje servisa      │
│  Login · Projekti · ProjekatDetalji · Zadaci · ZadatakForma  │
│  Statistika · ConfirmDialog · AppComponent                   │
└───────────────▲──────────────────────────────┬───────────────┘
                │ Observable                   │ poziv metode
┌───────────────┴──────────────────────────────▼───────────────┐
│  SERVISI (@Injectable, providedIn: 'root')                   │
│  AuthService · ProjekatService · ZadatakService              │
│  jedina tačka koja zna adrese REST servisa                   │
└───────────────▲──────────────────────────────┬───────────────┘
                │ HTTP odgovor                 │ HttpClient
┌───────────────┴──────────────────────────────▼───────────────┐
│  JSON SERVER   http://localhost:3000                         │
│  /korisnici   /projekti   /zadaci     ← db.json              │
└──────────────────────────────────────────────────────────────┘

Poprečno kroz sve slojeve:
  MODELI (interfejsi + enumi)  ·  PIPE-OVI  ·  GUARD  ·  ROUTER
```

Pravilo koje treba izgovoriti:
**„Komponente ne znaju ništa o HTTP-u, a servisi ne znaju ništa o prikazu."**
Komponenta zove metodu servisa i pretplati se; servis vraća `Observable`.

---

## 2. Pokretanje aplikacije (bootstrap)

```
index.html            <app-root></app-root>
      │
main.ts               bootstrapApplication(AppComponent, appConfig)
      │
app.config.ts         providers: [
      │                  provideRouter(routes),        ← ruter + rute
      │                  provideHttpClient(),          ← HttpClient svuda
      │                  provideAnimationsAsync()      ← animacije za Material
      │               ]
      ▼
AppComponent          toolbar + <router-outlet>
      │
      ▼
Router               na osnovu URL-a bira komponentu i ubacuje je u outlet
```

Ključna rečenica: **aplikacija nema nijedan `NgModule`** — sve je standalone, a globalni
provajderi se navode u `app.config.ts` i prosleđuju funkciji `bootstrapApplication`.

---

## 3. Mapa ruta

| Putanja | Komponenta | Guard |
|---|---|---|
| `''` | → preusmerenje na `projekti` | — |
| `login` | `LoginComponent` | ne |
| `projekti` | `ProjektiComponent` | `authGuard` |
| `projekti/:id` | `ProjekatDetaljiComponent` | `authGuard` |
| `projekti/:projekatId/zadaci/novi` | `ZadatakFormaComponent` (dodavanje) | `authGuard` |
| `projekti/:projekatId/zadaci/:id/izmena` | `ZadatakFormaComponent` (izmena) | `authGuard` |
| `statistika` | `StatistikaComponent` | `authGuard` |
| `**` | → preusmerenje na `projekti` | — |

Dve stvari koje se pitaju:

- **Zašto jedna komponenta za dve rute?** Zato što su forma i validacija identične; razlika
  je samo POST vs. PUT i početno popunjavanje. Režim se prepoznaje po prisustvu `:id`.
- **Šta radi `**`?** Wildcard ruta — sve nepoznate adrese vodi na listu projekata
  (mora biti **poslednja** u nizu, jer router uzima prvo poklapanje).

---

## 4. Stablo komponenti

```
AppComponent  (toolbar: navigacija, ime korisnika, odjava)
└── router-outlet
    ├── LoginComponent
    ├── ProjektiComponent            (kartice projekata + sortiranje)
    ├── ProjekatDetaljiComponent     (detalji jednog projekta)
    │   └── ZadaciComponent          ← @Input() projekatId
    │       └── ConfirmDialogComponent  (otvara se kroz MatDialog)
    ├── ZadatakFormaComponent        (dodavanje / izmena)
    └── StatistikaComponent
```

`ZadaciComponent` je jedina komponenta-dete koja se ugnježdava u šablon druge komponente.
`ConfirmDialogComponent` se ne piše u šablonu — Material ga sam ubacuje kroz
`dialog.open(ConfirmDialogComponent, { data: … })`.

---

## 5. Tok podataka na primeru brisanja zadatka

```
[klik na ikonicu kante]
   │  (click)="obrisiZadatak(zadatak)"
   ▼
ZadaciComponent.obrisiZadatak()
   │  dialog.open(ConfirmDialogComponent, { data: { naslov, poruka } })
   ▼
ConfirmDialogComponent   ← podaci stižu kroz MAT_DIALOG_DATA
   │  korisnik klikne "Obriši" → [mat-dialog-close]="true"
   ▼
dialogRef.afterClosed().subscribe(potvrdjeno => …)
   │  ako je false → izlaz, ništa se ne dešava
   ▼
ZadatakService.obrisiZadatak(id)  →  HttpClient.delete('/zadaci/5')
   │
   ▼
JSON Server briše zapis iz db.json
   │
   ▼
next: → snackBar.open('Zadatak je obrisan') + ucitajZadatke()
   │
   ▼
dataSource.data = novi niz  →  Material tabela se ponovo iscrtava
```

Isti obrazac važi za sve operacije: **komponenta → servis → HttpClient → server →
`subscribe` → osvežavanje stanja → prikaz.**

---

## 6. Stanje prijavljenog korisnika

```
              ┌────────────── AuthService ──────────────┐
              │                                          │
              │  korisnikSubject: BehaviorSubject<K|null>│  ← privatan
              │        │                                 │
              │        └── korisnik$ : Observable        │  ← javan
              │                                          │
              │  localStorage['prijavljeniKorisnik']     │
              └───────▲──────────────────┬───────────────┘
                      │                  │
       prijava()/odjava()          .value (sinhrono)
                      │                  │
        LoginComponent│                  │authGuard.jePrijavljen()
                      │                  │
                AppComponent (korisnik$ | async) → toolbar
```

Zašto `BehaviorSubject`, a ne obična promenljiva?

1. **Pamti poslednju vrednost** i odmah je šalje svakom novom pretplatniku — toolbar dobija
   trenutnog korisnika čim se pretplati, bez čekanja na sledeću promenu.
2. **Obaveštava sve zainteresovane** o promeni — prijava na jednom mestu automatski menja
   toolbar na drugom.
3. Ima `.value` za sinhrono čitanje — to koristi guard, koji mora da odgovori odmah.

Zašto je `Subject` privatan, a napolju stoji `korisnik$: Observable`?
Da niko spolja ne može da pozove `.next()` i „ubaci" lažnog korisnika — spolja se sme samo
slušati. To je standardni obrazac i lepo zvuči na odbrani.

---

## 7. Model podataka i veza sa `db.json`

```ts
// zadatak.model.ts
export enum StatusZadatka    { Novo = 0, UToku = 1, Zavrseno = 2 }
export enum PrioritetZadatka { Nizak = 0, Srednji = 1, Visok = 2 }

export interface Zadatak {
  id: number;
  projekatId: number;        // strani ključ ka projektu
  opis: string;
  status: StatusZadatka;     // broj
  prioritet: PrioritetZadatka;
}
```

```json
// db.json
{ "id": 2, "projekatId": 1, "opis": "Implementirati responzivnu navigaciju",
  "status": 1, "prioritet": 1 }
```

Brojevi u bazi ↔ enumi u modelu ↔ tekst u prikazu (pipe).
Mape `STATUS_OPISI` i `PRIORITET_OPISI` u istom fajlu su **jedini izvor prevoda** — koriste
ih i pipe-ovi i padajuće liste u formi i filteri i statistika. Ako sutra dodaš status
`Otkazano = 3`, menjaš samo taj fajl.

Veze: `Zadatak.projekatId → Projekat.id` (jedan projekat ima više zadataka).
JSON Server podržava filtriranje po polju, pa je GET `/zadaci?projekatId=1` dovoljan da se
dobiju zadaci jednog projekta — nema potrebe da se povlače svi pa filtriraju na klijentu.
