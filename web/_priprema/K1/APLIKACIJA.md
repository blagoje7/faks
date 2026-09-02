# K1 — aplikacija: pokretanje i redosled izlaganja

Jednostavna web aplikacija nad domenom **narudžbina → stavka**, uz proizvod kao
šifarnik. Namena joj je da se na njoj, otvaranjem fajlova, objasni MVP podela —
zato je funkcionalnost svedena na minimum, a slojevi su razdvojeni po fajlovima.

Ista arhitektura, sprovedena u punom obimu sa Flask-om, Vue-om i MySQL-om, je
u folderu [`K2/`](../../K2).

---

## Pokretanje

```bash
cd K1 && python pokreni.py
```

Ništa se ne instalira — koriste se samo moduli standardne biblioteke Pythona
(`http.server`, `sqlite3`, `json`). Aplikacija se otvara na
`http://localhost:8000`.

Baza se pravi iznova pri svakom pokretanju, sa istim početnim podacima. Ako se
tokom demonstracije nešto obriše, dovoljno je zaustaviti (Ctrl+C) i pokrenuti
ponovo.

---

## Mapa fajlova

| Sloj | Fajl | Odgovornost |
|---|---|---|
| **Model** | `model.py` | Entiteti domena, izvedena polja, šema i pristup bazi |
| **Presenter** | `presenter.py` | Provera ulaza, rad nad modelom, statusni kod |
| Granica | `granica.py` | HTTP + JSON; prevodi zahtev u poziv Presentera |
| **View** | `view/index.html`, `view/view.js`, `view/stil.css` | Prikaz i korisnički događaji |
| Kanal | `view/api.js` | Jedini put od View-a do Presentera |
| Pokretanje | `pokreni.py` | Priprema bazu i pušta server |

Zavisnosti idu samo nadole: View zna za `api.js`, `api.js` zna za adrese,
Presenter zna za Model, Model ne zna ni za šta iznad sebe.

---

## Redosled otvaranja fajlova pri izlaganju

1. **`model.py`** — DDL na sredini fajla. Dva strana ključa u tabeli `stavka`
   namerno su različito podešena: `narudzbina_id` je `ON DELETE CASCADE` jer je
   narudžbina vlasnik svojih stavki, a `proizvod_id` je `ON DELETE RESTRICT`
   jer je proizvod šifarnik i ne sme nestati ispod postojeće stavke.
   Odmah iznad su i izvedena polja `iznos` i `ukupan_iznos` — računaju se, ne
   čuvaju se u tabeli.

2. **`presenter.py`**, funkcija `dodaj_stavku` — ceo pattern u jednoj funkciji:
   prvo provera ulaza, pa tek ako je ispravan, obraćanje modelu. Ako provera ne
   prođe, vraća se `400` sa greškama po poljima i **model se uopšte ne dodiruje**.
   Cena se čita iz šifarnika, a ne iz zahteva — da se uzima iz zahteva, klijent
   bi diktirao cenu i pravilo domena bi se preselilo u pretraživač.

3. **`granica.py`** — tabela `RUTE`. Ovde nema nijednog pravila domena, samo
   prevođenje HTTP zahteva u poziv funkcije Presentera i odgovora u JSON.

4. **`view/api.js`** — jedini kanal ka Presenteru. Ne zna šta je narudžbina,
   ništa ne računa i ništa ne odlučuje.

5. **`view/view.js`** — prikazuje ono što dobije. Nema proračuna iznosa, nema
   odluke šta sme da se obriše, nema SQL-a. Posle upisa ne računa novi zbir sam
   nego traži novo stanje od Presentera (`osveziIzabranu`).

---

## Šta se može pokazati u radu

| Radnja | Šta pokazuje |
|---|---|
| Klik na **Stavke** neke narudžbine | Master-detail: nadređeni zapis i njegovi podređeni |
| Brisanje narudžbine | `ON DELETE CASCADE` — stavke nestaju sa njom |
| Brisanje proizvoda koji stoji na stavci | `ON DELETE RESTRICT` — odbijeno sa `409` i objašnjenjem |
| Količina `0` pa **Sačuvaj** | Provera u Presenteru: `400`, greška ispod polja, model nedirnut |
| Dodavanje proizvoda koji je već na narudžbini | `UNIQUE (narudzbina_id, proizvod_id)` i provera u Presenteru |
| Kolona **Cena po komadu** | Zapamćena cena: `84,90` na stavci, `89,90` u šifarniku |

---

## Statusni kodovi

| Kod | Značenje |
|---|---|
| `200` | Uspeh |
| `201` | Stavka je kreirana |
| `400` | Neispravan unos; telo sadrži `greske` po poljima |
| `404` | Traženi entitet ili adresa ne postoje |
| `409` | Radnja je u sukobu sa stanjem podataka (brisanje upotrebljenog proizvoda) |
