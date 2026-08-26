# Komponenta: ConfirmDialogComponent

Fajlovi: `confirm-dialog.component.ts`, `.html`, `.css` — nema rutu; otvara se programski kroz `MatDialog`

## Namena

Dialog za potvrdu destruktivnih akcija — pokriva dodatnu funkcionalnost "potvrda brisanja kroz dialog prozor". Sprečava slučajno brisanje: DELETE zahtev se šalje tek nakon eksplicitne potvrde.

## Kako radi

1. Pozivalac (npr. `ZadaciComponent`) otvara dialog:
   ```ts
   const ref = this.dialog.open(ConfirmDialogComponent, {
     data: { naslov: 'Brisanje zadatka', poruka: '...' }
   });
   ```
2. Dialog kroz `@Inject(MAT_DIALOG_DATA)` prima `naslov` i `poruku` — zato je **generički** i upotrebljiv za potvrdu bilo koje akcije.
3. Dugmad koriste direktivu `[mat-dialog-close]="true/false"` — zatvaraju dialog i vraćaju vrednost.
4. Pozivalac se pretplati na `ref.afterClosed()`: `true` ⇒ izvrši akciju; `false`/`undefined` (klik van dialoga, Esc) ⇒ ništa.

## Ključne odluke

- **Generička komponenta umesto "DeleteZadatakDialog"** — tekst dolazi spolja kroz `MAT_DIALOG_DATA`, pa jedan dialog služi svim potvrdama u aplikaciji (princip ponovne upotrebljivosti).
- **Odluku donosi pozivalac, ne dialog** — dialog samo vraća `true`/`false`; ne zna ništa o zadacima niti šalje HTTP zahteve. Jasna podela odgovornosti: UI potvrde odvojen od poslovne logike.
- **`[mat-dialog-close]` direktiva umesto ručnog `dialogRef.close()`** — deklarativno, manje koda, standardni Material obrazac.

## Angular Material komponente

`MatDialog` (title/content/actions), `MatButton`, `MatIcon`.
