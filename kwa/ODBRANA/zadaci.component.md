# Komponenta: ZadaciComponent

Fajlovi: `zadaci.component.ts`, `.html`, `.css` — nema svoju rutu; ugrađuje se u `ProjekatDetaljiComponent` kao `<app-zadaci [projekatId]="...">`

## Namena

Obavezna "komponenta za prikaz zadataka": Material **tabela** zadataka izabranog projekta, sa filtriranjem po statusu/prioritetu, sortiranjem, brisanjem uz potvrdu i dugmadima ka formi za dodavanje/izmenu. Pokriva zahteve: pregled zadataka projekta, brisanje zadataka, filtriranje po statusu ili prioritetu.

## Kako radi

- **`@Input({ required: true }) projekatId`** — roditelj prosleđuje id projekta; komponenta u `ngOnInit` poziva **GET** `/zadaci?projekatId=X`.
- **`MatTableDataSource`** — umesto običnog niza, jer ima ugrađeno sortiranje (`dataSource.sort = matSort`) i filtriranje (`filterPredicate`).
- **Filtriranje** — dve `mat-select` liste (Status, Prioritet) sa opcijom "Svi" (`null`). `filterPredicate` prikazuje red samo ako zadovoljava **oba** izabrana uslova. Opcije lista se grade iz centralnih mapa `STATUS_OPISI` / `PRIORITET_OPISI`, pa korisnik bira tekst, a poredi se broj. Trik: dodela bilo kog nepraznog stringa u `dataSource.filter` okida ponovno filtriranje.
- **Sortiranje** (dodatna funkcionalnost) — `matSort` + `mat-sort-header` na kolonama; `@ViewChild(MatSort)` je **setter** jer tabela može nastati posle inicijalizacije view-a.
- **Brisanje** (dodatne funkcionalnosti: dialog + snackbar) — otvara se `ConfirmDialogComponent`; **DELETE** `/zadaci/:id` se šalje tek ako `afterClosed()` vrati `true`; zatim snackbar poruka i ponovno učitavanje sa servera.
- **Status/prioritet kroz pipe-ove** — u ćelijama `{{ z.status | status }}` — korisnik nikad ne vidi brojeve; obojene oznake (CSS klase `status-0`...) dodatno vizuelno razlikuju vrednosti.

## Ključne odluke

- **Klijentsko filtriranje** — svesna odluka: zadaci jednog projekta su već učitani, pa filter reaguje trenutno, bez novih HTTP zahteva; demonstrira i rad sa `MatTableDataSource`. (Filtriranje po projektu je, s druge strane, serversko — query parametar.)
- **Osvežavanje sa servera posle brisanja** umesto lokalnog uklanjanja iz niza — tabela uvek prikazuje stvarno stanje baze; jednostavnije za obrazloženje i otpornije na greške.

## Angular Material komponente

`MatTable`, `MatSort`, `MatSelect` + `MatFormField`, `MatButton`, `MatIcon`, `MatDialog`, `MatSnackBar`.
