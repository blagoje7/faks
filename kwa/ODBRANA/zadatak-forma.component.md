# Komponenta: ZadatakFormaComponent

Fajlovi: `zadatak-forma.component.ts`, `.html`, `.css` — rute `/projekti/:projekatId/zadaci/novi` i `/projekti/:projekatId/zadaci/:id/izmena` (obe zaštićene guardom)

## Namena

Obavezna "komponenta za formu za dodavanje/izmenu zadataka". Jedna komponenta pokriva **oba režima** — dodavanje (POST) i izmenu (PUT).

## Kako radi

1. **Prepoznavanje režima** — u `ngOnInit` čita parametre rute: `projekatId` uvek postoji; ako postoji i `:id`, komponenta je u režimu izmene (`jeIzmena` getter).
2. **Režim izmene** — **GET** `/zadaci/:id` pa `forma.patchValue(...)` popuni kontrole postojećim vrednostima.
3. **Reactive forma sa validacijom** (tehnički zahtev + dodatna funkcionalnost):
   - `opis`: obavezan, 5–200 znakova (`required`, `minLength`, `maxLength`);
   - `status` i `prioritet`: obavezni, sa podrazumevanim vrednostima (Novo / Srednji).
4. **Čuvanje** — nevalidna forma ⇒ `markAllAsTouched()` (prikaz grešaka, bez zahteva). Validna ⇒ POST (novi, bez `id` — dodeljuje ga JSON Server) ili PUT (kompletan objekat sa `id`). Uspeh ⇒ snackbar + povratak na detalje projekta.

## Ključne odluke

- **Jedna komponenta za oba režima** — forma je identična, razlikuju se samo početne vrednosti i završni HTTP zahtev; dve komponente bi bile 90% kopirani kod. Ovo je i uobičajen obrazac u praksi.
- **Numeričke vrednosti u modelu, tekst za korisnika** — `mat-option [value]="o.vrednost"` nosi broj, a prikazuje tekst iz centralnih mapa (`STATUS_OPISI`); zahtev specifikacije ispunjen je na nivou forme bez ikakve konverzije pri čuvanju.
- **`patchValue` umesto `setValue`** — popunjava samo navedene kontrole i ne puca ako se struktura forme kasnije proširi.
- **Ruta umesto dialoga za formu** — specifikacija traži da forme za dodavanje/izmenu budu *zaštićene rute*, pa forma mora biti routabilna komponenta (dialog ne bi imao svoju rutu koju guard štiti).

## Angular Material komponente

`MatCard`, `MatFormField` + `MatInput` (textarea), `MatSelect`, `MatButton`, `MatIcon`, `MatSnackBar`.
