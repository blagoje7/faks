# Priprema — materijal koji se ne pokazuje

Ovaj folder postoji samo radi pripreme. Na odbrani se otvaraju **isključivo**
[`K1/`](../K1) i [`K2/`](../K2) — u njima je samo kod, bez ijednog dokumenta.

```
web/
├── K1/          kod koji se pokazuje na K1
├── K2/          kod koji se pokazuje na K2
└── _priprema/   ovaj folder — ne otvarati pred profesorom
```

---

## Šta je gde

| Fajl | Za šta služi |
|---|---|
| [`K1/IZLAGANJE.md`](K1/IZLAGANJE.md) | **monolog za K1** bez prekida, pa 10 teorijskih pitanja, 5 o implementaciji i 2 u lošoj nameri |
| [`K1/ODBRANA.md`](K1/ODBRANA.md) | teorija za K1: master-detail, MVP, poređenje sa MVC, očekivana pitanja, plan izlaganja |
| [`K1/APLIKACIJA.md`](K1/APLIKACIJA.md) | pokretanje K1 aplikacije, mapa fajlova i **redosled njihovog otvaranja** pri izlaganju |
| [`K1/prezentacija.html`](K1/prezentacija.html) | ista sadržina kao `ODBRANA.md`, u obliku za ekran; otvara se dvoklikom |
| [`K1/dijagrami/`](K1/dijagrami) | tri SVG dijagrama: model podataka, slojevi, tok ažuriranja |
| [`K2/IZLAGANJE.md`](K2/IZLAGANJE.md) | **monolog za K2** uz demonstraciju, pa 10 teorijskih pitanja, 5 o implementaciji i 2 u lošoj nameri |
| [`K2/ODBRANA.md`](K2/ODBRANA.md) | izbor alata, mapa slojeva na fajlove, plan demonstracije CRUD-a |
| [`K2/README.md`](K2/README.md) | instalacija i pokretanje K2, opis REST API-ja, rešavanje problema |
| [`K2/teorija.html`](K2/teorija.html) | HTTP, REST, ORM, SPA, Vue, CORS |
| [`materijali/`](materijali) | skripte sa predavanja i pitanja iz teorije |

---

## Pokretanje

Obe komande se pokreću iz korena projekta (`web/`).

**K1** — ništa se ne instalira, dovoljan je Python:

```bash
cd K1 && python pokreni.py
```

**K2** — traži MySQL, `venv` i izgrađen Vue klijent (uputstvo u [`K2/README.md`](K2/README.md)):

```bash
cd K2\backend && venv\Scripts\python app.py
```

Provera pred izlaganje: `http://localhost:5000/api/stanje` mora vratiti
`{"baza": "povezana"}`.

---

## Redosled na dan odbrane

1. Teorija (usmeno).
2. **K1** — monolog iz [`K1/IZLAGANJE.md`](K1/IZLAGANJE.md), uz otvaranje fajlova redom
   `model.py` → `presenter.py` → `granica.py` → `view/api.js` → `view/view.js`.
   Aplikacija neka već radi u pretraživaču, da se uz kod odmah vidi posledica.
3. **K2** — monolog iz [`K2/IZLAGANJE.md`](K2/IZLAGANJE.md) uz demonstraciju CRUD-a uživo.
