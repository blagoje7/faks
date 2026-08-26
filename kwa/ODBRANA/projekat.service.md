# Servis: ProjekatService (`projekat.service.ts`)

## Namena

Enkapsulira svu HTTP komunikaciju vezanu za **projekte**. Komponente nikada ne pozivaju `HttpClient` direktno — uvek idu preko servisa. To je zahtev specifikacije ("servisi za komunikaciju sa backend-om") i dobra praksa: adresa API-ja i logika komunikacije su na jednom mestu.

## Metode

| Metoda | HTTP zahtev | Namena |
|---|---|---|
| `getProjekti()` | `GET /projekti` | lista svih projekata |
| `getProjekat(id)` | `GET /projekti/:id` | jedan projekat za stranicu detalja |

## Metodologija

- **`Observable` umesto `Promise`** — `HttpClient` prirodno vraća Observable; komponenta se pretplati u `ngOnInit` i ažurira svoje polje kad odgovor stigne. Observable se lako kombinuje sa RxJS operatorima i `async` pipe-om.
- **Generički tipovi** (`get<Projekat[]>`) — TypeScript zna tačan oblik odgovora, pa greške u nazivima polja hvata već pri kompajliranju.
- **Nema create/update/delete za projekte** — specifikacija traži CRUD samo nad **zadacima**; projekti se samo pregledaju. POST/PUT/DELETE zahtevi su implementirani u `ZadatakService`.

## Gde se koristi

- `ProjektiComponent` — `getProjekti()` za listu.
- `ProjekatDetaljiComponent` — `getProjekat(id)` za detalje.
