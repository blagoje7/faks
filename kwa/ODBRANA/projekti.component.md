# Komponenta: ProjektiComponent

Fajlovi: `projekti.component.ts`, `.html`, `.css` — ruta `/projekti` (zaštićena guardom)

## Namena

Pregled liste svih projekata — obavezna "komponenta za prikaz projekata" iz specifikacije. Ujedno je početna strana aplikacije (ruta `/` preusmerava ovde).

## Kako radi

1. U `ngOnInit` poziva `ProjekatService.getProjekti()` → **GET** `/projekti` ka JSON Server-u.
2. Dok odgovor ne stigne prikazuje se `mat-spinner` (polje `ucitavanje`).
3. Projekti se prikazuju kao **Material kartice** u responzivnoj CSS grid mreži; svaka kartica ima naziv, rok (formatiran `DatePipe`-om — `dd.MM.yyyy.`), opis i dugme "Detalji" (`routerLink` na `/projekti/:id`).
4. **Sortiranje** (dodatna funkcionalnost): `mat-button-toggle-group` menja kriterijum (naziv/rok), lista se sortira na klijentu.

## Ključne odluke

- **Učitavanje u `ngOnInit`, ne u konstruktoru** — Angular konvencija: konstruktor služi samo za dependency injection; `ngOnInit` se poziva kada je komponenta spremna, i tu pripada inicijalna komunikacija sa serverom.
- **Kartice umesto tabele** — projekata je malo i imaju opisni tekst, pa je vizuelno bogatiji prikaz prikladniji; tabela je iskorišćena tamo gde ima smisla (zadaci).
- **`localeCompare(..., 'sr')`** — ispravno sortiranje srpske latinice (š, č, ć...); ISO datumi se ispravno sortiraju običnim poređenjem stringova.
- **Obrada greške** — ako JSON Server nije pokrenut, korisnik dobija snackbar poruku, a spinner se gasi (aplikacija ne "visi").

## Angular Material komponente

`MatCard`, `MatButton`, `MatIcon`, `MatProgressSpinner`, `MatButtonToggle`, `MatSnackBar`.
