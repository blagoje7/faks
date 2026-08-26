# Komponenta: ProjekatDetaljiComponent

Fajlovi: `projekat-detalji.component.ts`, `.html`, `.css` — ruta `/projekti/:id` (zaštićena guardom)

## Namena

Prikaz detalja pojedinačnog projekta — obavezna komponenta iz specifikacije. Ispod detalja ugrađuje `<app-zadaci>`, komponentu koja prikazuje i uređuje zadatke tog projekta.

## Kako radi

1. `ActivatedRoute.snapshot.paramMap.get('id')` čita `:id` iz URL-a; `Number(...)` konvertuje string u broj.
2. `ProjekatService.getProjekat(id)` → **GET** `/projekti/:id`; do odgovora se vrti spinner.
3. Detalji se prikazuju u Material kartici; rok kroz `DatePipe`.
4. Projekat prosleđuje detetu: `<app-zadaci [projekatId]="projekat.id">`.

## Ključne odluke

- **Kompozicija komponenti (roditelj–dete)** — detalji projekta i lista zadataka su odvojene odgovornosti u odvojenim komponentama; specifikacija ih i traži kao zasebne. Komunikacija ide standardnim Angular mehanizmom `@Input` (roditelj → dete). `ZadaciComponent` tako ostaje ponovo upotrebljiva — bilo koja strana joj samo prosledi `projekatId`.
- **`snapshot` umesto pretplate na `paramMap`** — dovoljan je, jer se sa strane detalja jednog projekta ne prelazi direktno na drugi projekat bez ponovnog kreiranja komponente (nema linka "sledeći projekat"). Da postoji takva navigacija, koristila bi se pretplata na `route.paramMap` Observable.
- **Obrada nepostojećeg id-a** — JSON Server vraća 404, `error` callback gasi spinner i prikazuje poruku; korisnik može nazad dugmetom "Nazad na projekte".

## Angular Material komponente

`MatCard`, `MatButton`, `MatIcon`, `MatProgressSpinner`, `MatSnackBar`.
