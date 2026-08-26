# Pipe: StatusPipe (`status.pipe.ts`)

## Namena

Prevodi numerički status zadatka iz modela (0, 1, 2) u opisni tekst ("Novo", "U toku", "Završeno") direktno u HTML šablonu:

```html
{{ zadatak.status | status }}
```

## Zašto pipe?

Specifikacija kaže: *"Korisnik aplikacije nikada ne treba da vidi numeričke vrednosti iz modela, već samo opisne vrednosti."*

Moguće alternative i zašto nisu izabrane:

- **Metoda u komponenti** (`getStatusTekst(z.status)`) — radila bi, ali bi se morala kopirati u svaku komponentu koja prikazuje status (tabela zadataka, statistika...). Pipe se piše jednom i importuje gde treba.
- **Čuvanje teksta u bazi** — direktno krši specifikaciju (traži se numerička vrednost u modelu).

Pipe je i **čist (pure)** po podrazumevanom podešavanju: Angular ga ponovo izračunava samo kada se ulazna vrednost promeni, što je efikasno.

## Kako radi

Metoda `transform` prima broj i vraća tekst iz mape `STATUS_OPISI` definisane u `zadatak.model.ts`. Time je prevod centralizovan — ako se doda novi status, menja se samo model.

## Gde se koristi

- `ZadaciComponent` — kolona "Status" u Material tabeli.
- `StatistikaComponent` — nazivi kategorija u statistici.
