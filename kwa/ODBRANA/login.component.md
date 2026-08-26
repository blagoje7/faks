# Komponenta: LoginComponent

Fajlovi: `login.component.ts`, `.html`, `.css` — ruta `/login`

## Namena

Strana za prijavu korisnika — prva od obaveznih komponenti iz specifikacije. Nakon uspešne prijave: podaci o korisniku se čuvaju u aplikaciji (radi `AuthService`), korisnik se preusmerava na početnu stranu (`/projekti`) i dobija pristup zaštićenim rutama.

## Kako radi

1. **Reactive forma** (dodatna funkcionalnost iz specifikacije): `FormBuilder.group()` u konstruktoru pravi `FormGroup` sa kontrolama `korisnickoIme` i `lozinka` i validatorima (`required`, `minLength`). Šablon se vezuje kroz `[formGroup]` i `formControlName`.
2. Pri `ngSubmit` poziva se `prijaviSe()`:
   - nevalidna forma ⇒ `markAllAsTouched()` prikaže sve `<mat-error>` poruke, zahtev se ne šalje (validacija korisničkog unosa — tehnički zahtev);
   - validna ⇒ `AuthService.prijava()` šalje GET ka JSON Server-u.
3. Tri moguća ishoda, svaki sa snackbar porukom: uspeh (pozdrav + preusmerenje), pogrešni kredencijali, greška servera (JSON Server nije pokrenut).

## Ključne odluke

- **Reactive umesto template-driven forme** — validacija i struktura su u TypeScript kodu: lakše se testira, čita i proširuje; ujedno nosi bodove kao dodatna funkcionalnost.
- **Polje `uToku`** — dok HTTP zahtev traje, dugme je onemogućeno (`[disabled]="uToku"`); sprečava dvostruko slanje.
- **Razdvojena poruka "pogrešni kredencijali" od "server ne radi"** — `next` sa `null` naspram `error` callback-a; korisnik dobija tačnu informaciju šta nije u redu.

## Angular Material komponente

`MatCard`, `MatFormField` + `MatInput` (sa `MatError` porukama), `MatButton`, `MatIcon`, `MatSnackBar`.

## Test podaci

Iz `db.json`: korisnik `blagoje` / lozinka `blagoje123` (ili `test` / `test123`).
