# Komponenta: AppComponent (korenska)

Fajlovi: `app.component.ts`, `.html`, `.css` (+ `app.config.ts` i `main.ts` kao ulazna tačka)

## Namena

Korenska komponenta — jedina koju `main.ts` direktno pokreće. Sadrži ono što je zajedničko za sve strane: **Material toolbar** (naziv aplikacije, navigacija, ime prijavljenog korisnika, dugme za odjavu) i **`<router-outlet>`** u koji Angular Router ubacuje komponentu aktivne rute.

## Kako radi

- Polje `korisnik$` je `Observable<Korisnik | null>` iz `AuthService`-a. U šablonu se koristi idiom `*ngIf="korisnik$ | async as korisnik"`:
  - `async` pipe se sam pretplaćuje i **sam otkazuje pretplatu** pri uništenju komponente (nema curenja memorije);
  - `*ngIf ... as` prikazuje navigaciju samo kada korisnik postoji i daje mu lokalno ime za prikaz `imeIPrezime`.
- `odjava()` poziva `AuthService.odjava()` (briše stanje + localStorage) pa `Router.navigate(['/login'])`.

## Ključne odluke

- **Toolbar u korenskoj komponenti, ne u svakoj strani** — piše se jednom, vidi se svuda; strane se bave samo svojim sadržajem.
- **`async` pipe umesto ručnog `subscribe`** — manje koda i automatsko upravljanje pretplatom; ovo je preporučeni Angular obrazac za prikaz Observable vrednosti u šablonu.
- **Standalone komponenta** — sve što šablon koristi (RouterLink, Material moduli, CommonModule) navodi se u `imports` nizu dekoratora. Nema NgModule-a; ovo je podrazumevani pristup u modernom Angular-u.

## Angular Material komponente

`MatToolbar`, `MatButton`, `MatIcon`.
