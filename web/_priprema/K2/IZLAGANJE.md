# K2 — izlaganje i pitanja

Sve u ovom dokumentu odnosi se na aplikaciju u folderu [`K2/`](../../K2).
Instalacija i API su u [`README.md`](README.md), plan demonstracije i mapa
slojeva u [`ODBRANA.md`](ODBRANA.md), teorijska pozadina u
[`teorija.html`](teorija.html).

**Pre ulaska u salu:** MySQL radi, `K2\backend\.env` ima tačnu lozinku,
`kreiraj_bazu.py` je pokrenut, `npm run build` je urađen, server radi, a
`http://localhost:5000/api/stanje` vraća `{"baza": "povezana"}`.

---

# 1. Monolog

> Namenjeno da se izgovori bez prekida, uz otvorenu aplikaciju.
> Traje osam do deset minuta. Delovi u zagradama su radnje, ne tekst.

---

Na K2 sam implementirao arhitekturu koju sam prezentovao na K1, u punom obimu.

Backend je Flask REST servis sa SQLAlchemy ORM-om nad MySQL bazom. Klijent je Vue 3 aplikacija sa Vue Routerom, građena Vite-om. Domen je isti — narudžbina kao nadređeni entitet, stavka kao podređeni, proizvod kao šifarnik.

Podela na slojeve je ista kao na K1, samo raspoređena po folderima umesto po fajlovima. `backend/models.py` je Model — entiteti, relacije, izvedena polja. `backend/presenters/` je Presenter — tri blueprinta, po jedan za svaki entitet, plus modul za proveru ulaza. `frontend/src/components/` je View — osam Vue komponenti. Granica je HTTP i JSON, a sa klijentske strane `frontend/src/api.js`, koji je jedini kanal ka Presenteru.

*(otvoriti `http://localhost:5000`)*

---

Ovo je početna strana. Zbirni podaci ovde nisu izračunati u pretraživaču nad izmišljenim brojevima — komponenta traži liste od API-ja i sabira ono što je Presenter vratio.

*(kliknuti „Narudžbine")*

Ovo je master lista. Sada nekoliko stvari koje se dešavaju na klik.

*(kucati u polje za pretragu)*

Pretraga **ne filtrira već učitanu listu u pretraživaču**. Svaki otkucaj, uz kratko odlaganje da se ne šalje zahtev po karakteru, ide kao `GET /api/narudzbine?pretraga=...` — dakle server odlučuje šta se poklapa, bez obzira na velika i mala slova. Isto važi i za filter po statusu i za sortiranje.

*(kliknuti zaglavlje kolone „Datum", pa opet)*

Klik na zaglavlje kolone menja parametre `sortiranje` i `smer` i ponovo pita server. Razlog je isti kao kod pretrage: to je odluka o podacima, a odluke o podacima ne donosi View.

*(kliknuti „Detalji" na prvoj narudžbini)*

Ovo je detail strana. Adresa je sada `/narudzbine/1` — Vue Router je promenio putanju bez odlaska na server, a komponenta je pozvala `GET /api/narudzbine/1` i dobila narudžbinu sa ugnježdenim stavkama.

U podnožju tabele je zbirni red. Taj iznos nije kolona u bazi — model ga izračuna iz stavki pri svakom čitanju. Da je upisan, morao bi se održavati ručno pri svakoj izmeni i pre ili kasnije bi se razišao sa stvarnim stanjem.

*(kliknuti „Dodaj stavku")*

Ovde su **dva select polja** — i narudžbina i proizvod se biraju iz liste, i obe liste dolaze sa servera. Ispod se, dok birate, menja obračun i piše koja cena važi i zašto.

*(ostaviti količinu praznu, poslati formu)*

Ako pošaljem neispravan unos, server vraća `400`, a u telu odgovora greške **po poljima**:

```json
{ "greske": { "kolicina": "Kolicina je obavezan podatak." } }
```

Klijent svaku ispiše ispod odgovarajućeg polja i oboji ga crveno. Važno je da Presenter u tom slučaju modelu **uopšte nije pristupio** — provera ulaza je pre rada nad modelom.

*(popuniti ispravno i sačuvati)*

Sada je stavka upisana i zbir narudžbine se odmah osvežio. Primetite kolonu „Cena po komadu" — ona se ne uzima iz zahteva. Klijent šalje samo koji proizvod i koliko, a **cenu server čita iz šifarnika**. Da je uzima iz zahteva, klijent bi mogao da diktira cenu i pravilo domena bi se preselilo u pretraživač.

*(kliknuti „Ukloni" na stavci)*

Potvrda brisanja nije `confirm()` dijalog pretraživača nego Vue komponenta koju generišem na klijentu — zato u poruci mogu da napišem tačno šta se briše i koliko stavki odlazi sa tim.

---

Sada tri pravila koja se najbolje vide kroz brisanje.

*(vratiti se na listu narudžbina, obrisati narudžbinu)*

Brisanje narudžbine briše i sve njene stavke. To je master-detail veza: stavka ne postoji bez narudžbine. U bazi je `ON DELETE CASCADE`, a u modelu `cascade="all, delete-orphan"` — dva nivoa koja rade istu stvar, jedan kroz sesiju ORM-a, drugi kao poslednja odbrana ispod aplikacije.

*(otvoriti „Proizvodi", obrisati „Bežični miš")*

Proizvod je nešto drugo. On je šifarnik, a ne roditelj stavke. „Bežični miš" stoji na narudžbini koja je još u pripremi, pa server odbija brisanje sa `409` i objašnjenjem. Da sam i ovde stavio kaskadu, brisanje jednog artikla obrisalo bi stavke iz tuđih narudžbina i tiho izmenilo njihove iznose.

*(obrisati „Mehanička tastatura")*

A ovaj proizvod stoji samo na narudžbini koja je **isporučena**, i on se briše. To je poslovno pravilo: isporučena narudžbina je zaključena, pa artikal može da izađe iz ponude.

*(otvoriti tu isporučenu narudžbinu)*

Ali pogledajte šta se desilo sa istorijom. Stavka je i dalje tu, sa istim nazivom, istom količinom i istim iznosom — samo nosi oznaku da taj proizvod više nije u šifarniku. Presenter je pre brisanja prekinuo vezu, a stavka pamti naziv i cenu iz trenutka poručivanja. Isporučena narudžbina se ne menja time što je neko izbacio artikal iz ponude.

---

Sve to je pokriveno samoproverom.

*(opciono: pokrenuti `venv\Scripts\python provera_api.py`)*

`provera_api.py` pokreće šezdeset dve provere nad celim API-jem — CRUD nad sva tri entiteta, kaskadno brisanje, `RESTRICT`, brisanje proizvoda po statusu narudžbine, zapamćena cena, premeštanje stavki, validacija, statusni kodovi i rutiranje jednostraničnog klijenta. Radi nad privremenom SQLite bazom, pa ne dira MySQL podatke.

To je i najkraći dokaz da pravila zaista stoje u Presenteru: da su u interfejsu, ovako se ne bi mogla proveriti.

---
---

# 2. Deset najverovatnijih pitanja — teorija

### 1. Šta je REST i koja ograničenja ga definišu?

REST je **stil arhitekture** za komunikaciju distribuiranih sistema, koji je Roy Fielding definisao u doktorskoj disertaciji 2000. godine. Nije skup pravila, pa se realizuje na različite načine — zato se Facebook i Twitter API razlikuju.

Definiše ga šest ograničenja:

| Ograničenje | Šta znači |
|---|---|
| Uniform Interface | standardna reprezentacija, resursi se identifikuju preko URI, dovoljno metapodataka, i linkovi kojima klijent otkriva dodatne resurse |
| Client-Server | razdvojene odgovornosti; obe strane se menjaju i održavaju nezavisno |
| Statelessness | zahtevi se tretiraju nezavisno, server ne pamti prethodne — stanje čuva klijent |
| Cacheability | i klijent i server mogu keširati resurse koji se retko menjaju |
| Layered System | klijent ne mora znati da li razgovara sa krajnjim serverom ili posrednikom |
| Code-On-Demand | server može poslati izvršni kod (npr. JavaScript) i time proširiti klijenta |

Naziv *Representational State Transfer* Fielding objašnjava kao sliku mreže stranica koja se ponaša kao virtuelna mašina stanja: linkovi su prelazi, a svaka nova stranica je sledeće stanje preneto korisniku.

> **Pazite na broj.** Pitanja sa testa obrađivala su prvih pet. Ako slajd navodi
> pet, nabrojte tih pet i *Layered System* dodajte rečenicom „a Fielding u
> disertaciji navodi i slojevitost sistema" — tako pokazujete više, a ne
> protivrečite predavanju.

### 2. Kako izgleda tok jednog zahteva od klika do baze?

Vue komponenta uhvati događaj i pozove funkciju u `api.js`. `api.js` je jedini kanal — pretvara poziv u HTTP zahtev, recimo `POST /api/stavke` sa JSON telom. Flask po registrovanoj ruti prosledi zahtev funkciji u odgovarajućem blueprintu, a to je Presenter. Presenter proveri ulaz; ako nije ispravan, vraća `400` i modelu ne pristupa. Ako jeste, radi nad modelom, SQLAlchemy sesija prevede to u SQL i pošalje MySQL-u. Nazad ide `201` sa JSON-om nove stavke, a komponenta prikaže novo stanje.

### 3. Kako radi rutiranje kad server ne zna za adresu `/narudzbine/3`?

To je jednostranična aplikacija. Klijentsko rutiranje menja adresu u pretraživaču bez odlaska na server, a Vue Router odlučuje koja se komponenta prikazuje.

Problem nastaje kad korisnik tu adresu **osveži** — tada je pretraživač stvarno traži od servera. Flask ima pravilo da sve nepoznate putanje vrati na `index.html`, pa se aplikacija podigne i Vue Router preuzme rutiranje. Putanje koje počinju sa `api/` su iz tog pravila izuzete, da pogrešna API adresa vrati `404` u JSON-u, a ne HTML stranicu.

### 4. Šta radi ORM i šta je sesija?

ORM preslikava klase na tabele, a instance na redove, pa se nad podacima radi u pojmovima domena umesto u SQL-u. `Narudzbina` je klasa, `narudzbina` je tabela, a `stavke` je relacija koju SQLAlchemy prevodi u spajanje.

Sesija je **jedinica posla**: skuplja izmene u memoriji i pri `commit()` ih šalje bazi kao jednu transakciju. Ako nešto pukne, `rollback()` vraća stanje. Zato u `app.py` postoji obrađivač koji pri neočekivanoj grešci radi `rollback` — da polovična izmena ne ostane u sesiji.

### 5. Kako se prenosi rezultat operacije?

Statusnim kodom i telom odgovora:

| Kod | Kada |
|---|---|
| `200` | uspeh |
| `201` | resurs je kreiran |
| `400` | neispravan unos; telo sadrži `greske` po poljima |
| `404` | traženi entitet ili adresa ne postoje |
| `409` | radnja je u sukobu sa stanjem podataka |
| `503` | baza nije dostupna |

Kod nosi vrstu ishoda, a telo detalje. Klijent na osnovu koda zna kako da postupi: `400` znači greške po poljima, `409` poruku u traci, `404` da entiteta nema.

### 6. Kako se u bazi izražava master-detail veza?

Kroz dva strana ključa u tabeli `stavka`, namerno različito podešena. `narudzbina_id` ima `ON DELETE CASCADE` jer je narudžbina vlasnik svojih stavki. `proizvod_id` ima `ON DELETE RESTRICT` jer proizvod nije vlasnik — baza odbija njegovo brisanje dok god ga neka stavka referiše.

Uz to stoji `UNIQUE (narudzbina_id, proizvod_id)`, čime se isti proizvod na jednoj narudžbini može pojaviti najviše jednom.

### 7. Šta znači da je REST bez stanja, kad vi imate sesiju?

Bez stanja znači da server **ne pamti kontekst prethodnih zahteva** — svaki zahtev nosi sve što je potrebno za njegovu obradu, i dva ista zahteva daju isti rezultat bez obzira na redosled.

To se ne odnosi na podatke u bazi, koji su trajno stanje resursa, nego na stanje razgovora. U ovoj aplikaciji stanje razgovora drži klijent: koja je narudžbina otvorena, šta je u polju za pretragu, koji je filter uključen — sve to živi u komponenti, a ne na serveru.

### 8. Kako se čuva istorijska cena?

Stavka pamti cenu, naziv i jedinicu mere iz trenutka poručivanja. Te vrednosti se prepisuju iz šifarnika kada se stavka kreira ili kada joj se promeni proizvod; izmena same količine ih ne dira.

Time su odvojena dva različita podatka: tekuća cena u šifarniku i cena po kojoj je kupac tada poručio. Posledica se vidi kad se proizvod obriše sa isporučene narudžbine — stavka ostaje potpuna, jer joj ništa više nije potrebno iz šifarnika.

### 9. Šta je CORS i kada se ovde javlja?

Pretraživač po pravilu istog porekla ne dozvoljava skripti sa jedne adrese da čita odgovor sa druge, ako ta druga to ne dozvoli zaglavljima. CORS su ta zaglavlja.

Na prezentaciji se ne javlja, jer Flask servira i API i klijent sa istog porekla — sve je `localhost:5000`. Javlja bi se u razvoju, kad klijent radi na `5173`; tamo Vite prosleđuje `/api` Flask-u, pa je i tada poreklo isto. `Flask-Cors` je podešen kao pojas sigurnosti, za slučaj da se klijent pokrene odvojeno.

### 10. Kada Vue komponenta traži podatke i šta se dešava dok čeka?

U `onMounted`, dakle pošto je komponenta ugrađena u DOM. Zahtev je asinhron, pa komponenta u međuvremenu prikazuje stanje učitavanja; kada odgovor stigne, reaktivne promenljive se popune i Vue sam ponovo iscrta samo ono što se promenilo.

Ako zahtev padne, greška se hvata i prikazuje kao poruka. Komponenta ne pretpostavlja da će podaci stići.

---
---

# 3. Pet pitanja o implementaciji

### 1. Zašto REST API i odvojen klijent, a ne Jinja šabloni na serveru?

Zato što REST razdvaja Presenter od načina prikaza. Sa Jinjom bi Presenter generisao HTML, pa bi znao kako prikaz izgleda; sa REST-om vraća podatke i ne zna šta će sa njima biti.

Praktična posledica: isti API bi bez ijedne izmene opslužio i mobilnu aplikaciju. A za odbranu podele važnije je ovo — granica koja se **ne može zaobići** lakše se brani nego dogovor da se sloj neće preskakati. Klijent nema drugi način da dođe do podataka osim preko `/api/...`.

### 2. Zašto MySQL i InnoDB?

MySQL zato što je traženo zadatkom. InnoDB zato što je to jedini uobičajeni MySQL pogon koji podržava **transakcije i strane ključeve** — a bez stranih ključeva `CASCADE` i `RESTRICT` ne bi postojali, pa bi ceo argument o master-detail vezi ostao na nivou dogovora.

To je i razlog zašto u DDL-u stoji `ENGINE=InnoDB` eksplicitno, umesto da se osloni na podrazumevanu vrednost servera.

### 3. Zašto se greške vraćaju po poljima, a ne kao jedna poruka?

Zato što korisnik treba da vidi **koje polje** je problem, a ne da traži po formi. Presenter vraća rečnik u kome je ključ ime polja:

```json
{ "greske": { "kolicina": "Kolicina mora biti najmanje 1." } }
```

Klijent onda samo raspoređuje — svaku poruku ispod odgovarajućeg polja. Time i View ostaje bez odluke: ne zna šta je greška ni koja poruka kome pripada, nego to čita iz odgovora. Da vraćam jednu poruku, klijent bi morao da pogađa na koje se polje odnosi, a to pogađanje je pravilo domena u pogrešnom sloju.

### 4. Zašto se cena čita iz šifarnika, a ne uzima iz zahteva?

Zato što bi u suprotnom klijent diktirao cenu. Zahtev dolazi sa mreže i može biti sastavljen mimo interfejsa — dovoljan je jedan `curl` sa cenom nula. Provera u pretraživaču je udobnost, ne zaštita.

Zato Presenter iz tela zahteva uzima samo `narudzbina_id`, `proizvod_id` i `kolicina`, a cenu čita iz šifarnika. Isto važi za naziv i jedinicu mere. To je opšte pravilo: sve što je posledica, a ne izbor korisnika, izračunava server.

### 5. Zašto je potvrda brisanja Vue komponenta, a ne `confirm()` pretraživača?

Iz tri razloga. Prvi je sadržaj poruke — u komponenti mogu da napišem koja se narudžbina briše i koliko stavki odlazi sa njom, dok `confirm()` prikazuje golu rečenicu bez konteksta. Drugi je izgled — ugrađeni dijalog izgleda različito u svakom pretraživaču i ne može se stilizovati. Treći je što `confirm()` blokira izvršavanje cele stranice dok stoji otvoren.

Uz to, komponenta se ponovo koristi za sva tri entiteta i prima samo tekst i dva događaja, `potvrdi` i `otkazi` — pa ni ona ne zna šta se briše.

---
---

# 4. Dva pitanja u lošoj nameri

> Cilj ovakvih pitanja nije informacija nego da se izgubi tlo pod nogama.
> Odgovor u oba slučaja počinje priznavanjem onoga što je tačno u pitanju.
> Odbrana tvrdnje koja se ne može odbraniti je najgori mogući ishod.

### 1. „Vue radi na deklarativnom vezivanju podataka. To je MVVM. Vi ste napravili MVVM i nazvali ga MVP."

**Tačno je da Vue interno koristi vezivanje podataka i da je to odlika MVVM-a.** Reaktivne promenljive u komponenti i šablon koji se sam iscrtava kada se one promene — to jeste ViewModel obrazac, i nema smisla tvrditi suprotno.

Ali to je tehnika **unutar** View sloja, a ne kanal ka modelu. Pitanje koje razdvaja obrasce nije „kako se prikaz osvežava" nego „odakle prikazu podaci i ko donosi odluke".

Komponenta nema pristup bazi, ne zna nijedno pravilo domena, ne računa iznose i ne odlučuje šta sme da se obriše. Ona poziva Presenter preko `api.js` i prikazuje ono što dobije. Vezivanje podataka radi između promenljive u komponenti i njenog šablona — dakle u celini unutar View-a, na jednoj strani HTTP granice.

Da je ovo MVVM u punom smislu, ViewModel bi držao stanje domena i pravila. Ovde ih drži Presenter, na serveru, i to se može proveriti: šezdeset dve provere u `provera_api.py` testiraju sva pravila **bez pokretanja Vue-a**. Da su pravila u komponentama, tako se ne bi mogla proveriti.

### 2. „Vaš `models.py` je samo skup SQLAlchemy tabela. Sva pravila su u Presenteru. To je anemičan model — logika je iscurila u kontroler, i vi zapravo imate Transaction Script, a ne MVP."

**Pojam je upotrebljen ispravno i deo primedbe stoji.** Većina pravila jeste u Presenteru: provera da narudžbina postoji, da se proizvod ne ponavlja, da datum nije u budućnosti. To je svesna odluka, ne previd.

Vredi razdvojiti dve vrste pravila. **Pravila validacije ulaza** — da li je poslato ono što treba — po prirodi pripadaju sloju koji prima zahtev, jer se tiču zahteva, a ne entiteta. Pravilo „datum ne sme biti u budućnosti" ne opisuje narudžbinu, nego šta smemo primiti.

**Pravila koja opisuju sam entitet jesu u modelu.** `Narudzbina.ukupan_iznos` i `broj_stavki` su izvedena polja modela, a ne Presentera. `Stavka.iznos` isto. Kaskadno brisanje je u relaciji modela i u šemi. Jedinstvenost proizvoda po narudžbini je ograničenje u bazi. Ništa od toga Presenter ne računa.

Gde bih se složio: da domen dalje raste — da se pojave popusti, rezervacija zaliha, prelazi između statusa — ta pravila ne bi smela u Presenter, nego u metode modela ili u zaseban sloj domena. Za ovaj obim bi takav sloj bio prazna ljuštura, i to je kompromis koji sam napravio svesno.

Ono što razlikuje ovo od Transaction Script-a je da Presenter **ne pristupa bazi direktno**. Ne piše SQL i ne otvara konekciju; radi isključivo kroz entitete modela. Kad bi bio Transaction Script, u njemu bi bili upiti — a nijedan nije.
