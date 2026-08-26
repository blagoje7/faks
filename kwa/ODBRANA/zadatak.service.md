# Servis: ZadatakService (`zadatak.service.ts`)

## Namena

Enkapsulira svu HTTP komunikaciju vezanu za **zadatke**. Ovde su pokrivena sva četiri tipa zahteva koje specifikacija traži u odeljku "REST komunikacija".

## Metode i mapiranje na zahteve specifikacije

| Metoda | HTTP zahtev | Zahtev iz specifikacije |
|---|---|---|
| `getZadaciZaProjekat(projekatId)` | `GET /zadaci?projekatId=X` | GET zahtevi; pregled zadataka izabranog projekta |
| `getSviZadaci()` | `GET /zadaci` | GET zahtevi; podaci za statistiku |
| `getZadatak(id)` | `GET /zadaci/:id` | popunjavanje forme za izmenu |
| `dodajZadatak(zadatak)` | `POST /zadaci` | POST zahtevi; dodavanje novih zadataka |
| `izmeniZadatak(zadatak)` | `PUT /zadaci/:id` | PUT zahtevi; izmena postojećih zadataka |
| `obrisiZadatak(id)` | `DELETE /zadaci/:id` | DELETE zahtevi; brisanje zadataka |

## Ključne odluke

- **Filtriranje na serveru query parametrom** — `GET /zadaci?projekatId=X` prepušta JSON Server-u da vrati samo zadatke jednog projekta, umesto da povlačimo sve pa filtriramo u klijentu. (Filtriranje po statusu/prioritetu je, s druge strane, namerno klijentsko — u `ZadaciComponent` — da bi se demonstrirala obrada podataka u Angular-u i trenutna reakcija UI-ja bez novog zahteva.)
- **`Omit<Zadatak, 'id'>` kod POST-a** — TypeScript utility tip: "objekat Zadatak bez polja id". `id` dodeljuje JSON Server, pa klijent i ne sme da ga šalje. Ovim tip sistema tačno izražava ugovor sa serverom.
- **PUT a ne PATCH** — specifikacija dozvoljava bilo koji; izabran je PUT jer forma za izmenu uvek raspolaže kompletnim objektom, pa je semantika "zameni ceo resurs" prirodna.

## Gde se koristi

- `ZadaciComponent` — učitavanje i brisanje zadataka.
- `ZadatakFormaComponent` — dodavanje i izmena.
- `StatistikaComponent` — svi zadaci za statistiku.
