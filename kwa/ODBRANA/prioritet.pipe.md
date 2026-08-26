# Pipe: PrioritetPipe (`prioritet.pipe.ts`)

## Namena

Prevodi numerički prioritet zadatka (0, 1, 2) u opisni tekst ("Nizak", "Srednji", "Visok") u šablonu:

```html
{{ zadatak.prioritet | prioritet }}
```

## Metodologija

Identična kao kod `StatusPipe` (vidi `status.pipe.md` za punu argumentaciju): jedan centralizovan prevod numeričkih vrednosti u tekst, kroz mapu `PRIORITET_OPISI` iz `zadatak.model.ts`, čime se ispunjava zahtev da korisnik nikada ne vidi brojeve iz modela.

Namerno su napravljena **dva odvojena pipe-a** umesto jednog generičkog: svaki ima jasnu, jednu odgovornost, a upotreba u šablonu je čitljivija (`| prioritet` umesto `| enumOpis:'prioritet'`).

## Gde se koristi

- `ZadaciComponent` — kolona "Prioritet" u Material tabeli.
- `StatistikaComponent` — nazivi kategorija u statistici prioriteta.
