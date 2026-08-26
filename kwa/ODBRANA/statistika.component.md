# Komponenta: StatistikaComponent

Fajlovi: `statistika.component.ts`, `.html`, `.css` — ruta `/statistika` (zaštićena guardom)

## Namena

Dodatna funkcionalnost iz specifikacije: **prikaz statistike zadataka**. Prikazuje ukupan broj zadataka i raspodelu po statusu i po prioritetu, sa brojkama, procentima i animiranim procentualnim trakama.

## Kako radi

1. **GET** `/zadaci` — svi zadaci iz svih projekata (`ZadatakService.getSviZadaci()`).
2. Pomoćna metoda `izracunaj(zadaci, opisi, selektor)` za svaku vrednost iz mape opisa prebroji zadatke i izračuna procenat.
3. Šablon crta "bar chart" čistim CSS-om: spoljna siva traka je 100%, unutrašnja obojena dobija širinu vezivanjem `[style.width.%]="stavka.procenat"`.

## Ključne odluke

- **Jedna generička metoda za obe statistike** — `izracunaj` prima **funkciju-selektor** (`(z) => z.status` ili `(z) => z.prioritet`) i mapu opisa; ista logika služi za obe kartice, bez kopiranja koda (DRY princip + demonstracija funkcija višeg reda).
- **CSS trake umesto chart biblioteke** — bez novih zavisnosti, potpuno razumljiv kod koji se lako brani; `[style.width.%]` je ujedno primer Angular style binding-a.
- **Nazivi kategorija iz centralnih mapa** (`STATUS_OPISI`, `PRIORITET_OPISI`) — i ovde korisnik vidi samo opisne vrednosti, nikada brojeve iz modela.
- **Zaštita od deljenja nulom** — kada nema zadataka, procenat je 0, aplikacija ne puca.

## Angular Material komponente

`MatCard`, `MatIcon`, `MatProgressSpinner`, `MatSnackBar`.
