# K1 — izlaganje i pitanja

Sve u ovom dokumentu odnosi se na aplikaciju u folderu [`K1/`](../../K1).
Teorijska pozadina je u [`ODBRANA.md`](ODBRANA.md), redosled otvaranja fajlova
u [`APLIKACIJA.md`](APLIKACIJA.md).

---

# 1. Monolog

> Namenjeno da se izgovori bez prekida, uz otvorenu aplikaciju i editor.
> Traje sedam do osam minuta ako se ne žuri. Delovi u zagradama su radnje, ne tekst.

---

Domen koji sam izabrao je evidencija narudžbina. Tri entiteta: narudžbina, stavka i proizvod.

Narudžbina je nadređeni entitet. Stavka je podređeni. Proizvod je šifarnik i namerno stoji van te veze — i ta razlika je ono što ovaj model čini master-detail modelom, a ne skupom tabela koje se referišu.

Razlika je u životnom veku. Stavka ne postoji bez narudžbine kojoj pripada — nema smisla van nje, i kada narudžbina nestane, nestaje i ona. Proizvod je nešto sasvim drugo: postojao je pre te stavke i ostaje posle nje. Stavka ga referiše, ali ga ne poseduje.

*(otvoriti `K1/model.py`, DDL na sredini fajla)*

To se u bazi vidi kao dva strana ključa u istoj tabeli, namerno različito podešena.

`narudzbina_id` ima `ON DELETE CASCADE`, jer je narudžbina vlasnik svojih stavki. `proizvod_id` ima `ON DELETE RESTRICT`, jer proizvod nije vlasnik — baza odbija da ga obriše dok god stoji na nekoj stavci. Da sam i tu stavio kaskadu, brisanje jednog artikla iz šifarnika obrisalo bi stavke iz tuđih narudžbina i tiho izmenilo njihove iznose.

U istoj tabeli je i `cena_po_komadu`. To nije suvišna kopija cene iz šifarnika. `proizvod.cena` je tekuća cena, a `stavka.cena_po_komadu` je cena po kojoj je taj kupac tada poručio. Bez te kolone, svaka izmena cenovnika retroaktivno bi promenila iznose svih ranijih narudžbina.

Nasuprot tome, `broj_stavki` i `ukupan_iznos` **nisu** kolone. Oni se izvode iz stavki pri svakom čitanju. Da su upisani, morali bi se ručno održavati pri svakoj izmeni stavke i pre ili kasnije bi se razišli sa stvarnim stanjem.

---

Arhitektura je Model – View – Presenter, i sprovedena je tako da svaki sloj bude tačno jedan fajl.

*(pokazati strukturu foldera)*

`model.py` je Model. U njemu su entiteti domena, njihova pravila i pristup bazi. Taj sloj ne zna da korisnički interfejs postoji — u njemu nema nijednog HTTP pojma, ni zahteva, ni odgovora, ni statusnog koda. Mogu ga pozvati iz obične skripte, bez pretraživača.

`presenter.py` je Presenter. On prima već raspakovan zahtev, proverava ulaz, radi nad modelom i vraća stanje koje treba prikazati, zajedno sa statusnim kodom. On ne zna kako izgleda prikaz — ne pravi HTML, ne zna za dugmad ni za tabele.

`view/` je View. Prikazuje ono što dobije i prijavljuje šta je korisnik uradio. U njemu nema nijednog pravila domena — nema računanja iznosa, nema odlučivanja šta sme da se obriše, nema SQL-a.

Između njih su još dva fajla koja nisu slojevi nego granica. `granica.py` prevodi HTTP zahtev u poziv funkcije Presentera i odgovor u JSON. `view/api.js` radi isto sa klijentske strane. Nijedan od njih ne sadrži pravilo domena — oba su namerno tanka i dosadna.

Zavisnosti idu samo nadole. Presenter je jedini sloj koji zna za oba susedna. View ne zna za model, model ne zna za View. Merilo da je podela stvarno sprovedena je jednostavno: kad bih obrisao Presenter, veza između pretraživača i baze bi bila prekinuta i ne bi postojao način da se zaobiđe.

---

Sada mehanizam, korak po korak.

*(otvoriti `http://localhost:8000`)*

Kada se strana učita, `view.js` pozove `ucitajSve`. To su dva zahteva kroz `api.js` — `GET /api/narudzbine` i `GET /api/proizvodi`. `granica.py` svaki od njih poklopi sa tabelom ruta i pozove odgovarajuću funkciju Presentera. Presenter traži podatke od modela, model izvrši SQL, i nazad ide JSON. View ga samo iscrta u dve tabele.

*(kliknuti „Stavke" na prvoj narudžbini)*

Klik na „Stavke" šalje `GET /api/narudzbine/1`. Presenter ovog puta traži narudžbinu **sa stavkama** i vraća ugnježden objekat. Otvara se drugi panel — to je detail strana master-detail veze. U podnožju tabele je ukupan iznos, koji nije stigao iz baze kao kolona nego ga je model izračunao iz stavki.

Obratite pažnju na kolonu „Cena po komadu": ovde piše osamdeset četiri devedeset, a u šifarniku ispod isti proizvod košta osamdeset devet devedeset. To je zapamćena cena o kojoj sam govorio.

*(u formi izabrati proizvod, uneti količinu, kliknuti „Sačuvaj stavku")*

Slanje forme šalje `POST /api/stavke` sa tri vrednosti: `narudzbina_id`, `proizvod_id` i `kolicina`. Cenu **ne** šaljem. Presenter prvo proverava ulaz — da narudžbina postoji, da proizvod postoji, da je količina bar jedan, i da taj proizvod već ne stoji na toj narudžbini. Tek ako sve prođe, čita cenu iz šifarnika i upisuje stavku. Vraća `201` i JSON nove stavke.

Klijent nakon toga **ne računa novi zbir sam** — traži novo stanje narudžbine od Presentera i prikaže ono što dobije. To je suština pasivnog View-a.

*(obrisati sadržaj polja količina i pokušati ponovo)*

Ako provera ne prođe, Presenter se modelu **uopšte ne obraća**. Vraća `400` sa greškama po poljima, i klijent svaku ispiše ispod odgovarajućeg polja i oboji ga crveno.

*(kliknuti „Obriši" na narudžbini)*

Brisanje narudžbine prvo traži potvrdu, sa brojem stavki u poruci. Presenter zatim briše samo narudžbinu — stavke odlaze same, kaskadno, i u kodu ne postoji nijedan `DELETE` nad tabelom stavki.

*(kliknuti „Obriši" na proizvodu koji se koristi)*

Brisanje proizvoda koji stoji na nekoj stavci vraća `409`. Ovde postoje dva nivoa odbrane: Presenter unapred proverava i vraća razumljivu poruku, a ispod njega `ON DELETE RESTRICT` bi odbio brisanje i da neko dođe do modela mimo Presentera.

---

Na kraju, ono zbog čega je podela uopšte napravljena.

Mogu da zamenim SQLite MySQL-om — menja se samo `model.py`. Mogu da zamenim ovaj klijent mobilnom aplikacijom — menja se samo `view/`, jer je granica HTTP i JSON, a ne dogovor da se sloj neće preskakati. Mogu da dodam entitet, na primer dostavljača — klasa u modelu, funkcije u Presenteru, komponenta u View-u, a postojeći slojevi se ne diraju.

Ista arhitektura, u punom obimu i sa MySQL-om i Vue-om, je moj K2.

---
---

# 2. Deset najverovatnijih pitanja — teorija

### 1. Kako izgleda tok jednog ažuriranja kroz slojeve?

Šest koraka. View prijavi korisnički događaj i pozove funkciju u `api.js`. `api.js` to prevede u HTTP zahtev — kod dodavanja stavke `POST /api/stavke` sa JSON telom. `granica.py` poklopi putanju i metodu sa tabelom ruta i pozove funkciju Presentera, prosleđujući raspakovano telo. Presenter proveri ulaz, pa radi nad modelom. Model izvrši SQL i vrati rezultat. Presenter vrati rečnik i statusni kod, granica ih pretvori u JSON odgovor, a View prikaže ono što je dobio.

Ključno je da nijedan korak ne može da se preskoči: View nema drugi kanal osim `api.js`, a `api.js` nema drugu adresu osim `/api/...`, koja vodi u Presenter.

### 2. Šta je MVP i po čemu se razlikuje od MVC?

Model su entiteti domena i njihova pravila. View je pasivan sloj koji prikazuje ono što dobije i prijavljuje događaje. Presenter je posrednik koji prima događaj, proverava ga, radi nad modelom i vraća stanje.

Odlučujuća razlika u odnosu na MVC je pristup modelu. **U MVC-u View sme da čita model direktno** i sam se osvežava kada se model promeni. **U MVP-u ta veza ne postoji** — sve što View prikaže prošlo je kroz Presenter. Druga razlika je u odnosu: jedan MVC kontroler opslužuje više prikaza, dok je Presenter vezan za svoj View.

### 3. Kako se u modelu podataka prepoznaje master-detail relacija?

Po zavisnosti životnog veka, ne po kardinalnosti. Strani ključ `stavka.narudzbina_id` je `NOT NULL`, pa svaka stavka pripada tačno jednoj narudžbini i ne može postojati bez nje. Kada nadređeni zapis nestane, podređeni nema razlog da postoji.

Obična veza mnogo-prema-jedan to nema. Stavka referiše i proizvod, ali proizvod nije njen roditelj — postojao je pre nje i ostaje posle nje.

### 4. Kako rade `ON DELETE CASCADE` i `ON DELETE RESTRICT`?

To su referencijalne akcije koje baza izvršava kada se briše red na koji strani ključ pokazuje.

`CASCADE` znači da baza sama briše sve redove koji ga referišu. U kodu ne postoji `DELETE` nad tabelom stavki — dovoljno je obrisati narudžbinu.

`RESTRICT` je suprotno: baza **odbija** brisanje dok god postoji red koji referiše taj zapis, i vraća grešku narušavanja integriteta. U SQLite-u obe akcije rade samo ako je uključeno `PRAGMA foreign_keys = ON`; bez toga bi strani ključevi bili samo zapisani, a ne sprovedeni.

### 5. Kako se čuva istorijska cena i zašto tako?

Cena se kopira u stavku u trenutku unosa. `stavka.cena_po_komadu` se prepisuje iz šifarnika kada se stavka kreira ili kada joj se promeni proizvod; izmena same količine je ne dira.

To su dva različita podatka: tekuća cena u šifarniku i cena po kojoj je kupac tada poručio. Bez te kopije, izmena cenovnika bi promenila iznose svih ranijih narudžbina — a one su već zaključene.

### 6. Kako View saznaje da li je operacija uspela?

Preko statusnog koda i tela odgovora, koje oba dolaze od Presentera. `200` i `201` znače uspeh, `400` neispravan unos sa greškama po poljima, `404` da traženi entitet ne postoji, `409` sukob sa stanjem podataka.

View ne odlučuje šta je greška — on samo raspoređuje ono što je dobio: greške po poljima idu ispod odgovarajućih polja, ostale u traku sa obaveštenjem.

### 7. Zašto se izvedeni podaci računaju umesto da se čuvaju?

Zato što bi bili podatak koji se može razići sa svojim izvorom. `ukupan_iznos` se izvodi iz stavki pri svakom čitanju, pa je uvek tačan po definiciji. Da je upisan u tabelu, morao bi se ručno ažurirati pri svakom dodavanju, izmeni i brisanju stavke, a jedan propušteni slučaj daje narudžbinu čiji zbir ne odgovara njenim stavkama.

Cena stanovanja te odluke je jedno računanje po čitanju. To je jeftino; nekonzistentan podatak nije.

### 8. Kako biste testirali Presenter bez korisničkog interfejsa?

Direktno — funkcije Presentera primaju obične Python rečnike i vraćaju rečnik i broj. Ne treba im ni pretraživač, ni HTTP server:

```python
import presenter
telo, status = presenter.dodaj_stavku({"narudzbina_id": 1, "proizvod_id": 2, "kolicina": 3})
assert status == 201
```

To je i praktična provera da je podela sprovedena: ako bih morao da pokrenem interfejs da bih testirao pravilo, pravilo ne bi bilo u Presenteru.

### 9. Šta je pasivan View i kako se to ovde vidi?

Pasivan View ne sadrži pravila i ne donosi odluke — on prikazuje i prijavljuje. Vidi se u tome što posle upisa stavke klijent ne sabira iznose sam, nego traži novo stanje narudžbine od Presentera i iscrta ono što dobije.

Praktična provera: pretraga fajla `view.js` za rečima „cena", „zbir" ili „SELECT" ne nalazi nijedan proračun, samo prikaz gotovih vrednosti.

### 10. Kako biste dodali još jedan entitet, na primer dostavljača?

Klasa u `model.py` sa svojim poljima i izvedenim vrednostima, nove funkcije u `presenter.py`, nove rute u tabeli `RUTE`, i prikaz u `view/`. Postojeći slojevi se ne diraju — dodaje se, ne prepravlja.

To je i svrha podele: ono što se menja zajedno stoji zajedno, a granice su na mestima gde se sistem prirodno seče.

---
---

# 3. Pet pitanja o implementaciji

### 1. Zašto bez ijednog okvira, samo standardna biblioteka?

Zato što je zadatak K1 da se **vidi** arhitektura. Svaki okvir deo posla skriva iza konvencije — Flask bi rutiranje sveo na dekorator, a ORM bi SQL sakrio iza atributa klase. Tada bih arhitekturu opisivao, umesto da je pokažem.

Ovako je svaki korak između pretraživača i Presentera kod koji se može otvoriti i pročitati, a ceo posao staje u nešto preko hiljadu linija. Uz to nema instalacije: `python pokreni.py` radi na svakom računaru sa Python-om, što je na dan odbrane bitna osobina.

### 2. Zašto SQLite, a ne MySQL kao u K2?

Zbog nula podešavanja — SQLite je deo standardne biblioteke i baza je jedan fajl. Za ono što ovde treba da se pokaže potpuno je dovoljan: podržava strane ključeve, `CASCADE`, `RESTRICT` i `UNIQUE` ograničenja, dakle sve o čemu govorim.

Zamena baze je i najbolji primer da podela radi: prelazak na MySQL dodirnuo bi samo `model.py`. Presenter i View ne bi znali da se išta promenilo.

### 3. Zašto se baza pravi iznova pri svakom pokretanju?

Zato što je ovo aplikacija za demonstraciju, a ne za upotrebu. Tokom izlaganja brišem narudžbine i proizvode; ako nešto pođe naopako, restart vraća poznato početno stanje, bez skripti za popravku.

U pravoj aplikaciji to bi bila greška, i tu razliku treba reći naglas — u K2, gde je baza MySQL, podaci ostaju.

### 4. Zašto je HTTP granica poseban fajl, a ne deo Presentera?

Zato da bi Presenter ostao slobodan od protokola. `granica.py` radi samo prevođenje: iz zahteva izvlači obične vrednosti, poziva funkciju i pretvara povratnu vrednost u JSON. Ne donosi nijednu odluku o narudžbinama.

Korist se vidi na testiranju i na zameni: Presenter se poziva direktno iz Python-a, a ako bi se HTTP zamenio nečim drugim, menjao bi se samo taj jedan fajl. Kad bi se u `granica.py` pojavio `if` koji odlučuje nešto o domenu, pravilo bi iscurilo iz Presentera u infrastrukturu.

### 5. Zašto View koristi jedan osluškivač na tabeli umesto po jednog na svakom dugmetu?

To je delegiranje događaja. Osluškivač stoji na `<tbody>`, a `dogadjaj.target.closest("tr")` utvrdi u koji je red kliknuto:

```javascript
el("telo-narudzbina").addEventListener("click", (dogadjaj) => {
  const red = dogadjaj.target.closest("tr");
  ...
});
```

Radi zahvaljujući bubble fazi propagacije — događaj sa dugmeta ispliva do roditelja. Prednost je što redove iscrtavam iznova posle svake izmene: da su osluškivači na dugmadima, morao bih ih ponovo vezivati pri svakom osvežavanju, a ovako osluškivač postoji jednom i radi i za redove koji tada još nisu postojali.

---
---

# 4. Dva pitanja u lošoj nameri

> Cilj ovakvih pitanja nije informacija nego da se izgubi tlo pod nogama.
> Odgovor u oba slučaja počinje priznavanjem onoga što je tačno u pitanju.
> Odbrana tvrdnje koja se ne može odbraniti je najgori mogući ishod.

### 1. „Vaš Presenter vraća statusne kodove — 400, 404, 409. Statusni kod je HTTP pojam. Znači vaš Presenter zna za protokol, dakle za način prikaza. Podela koju opisujete nije sprovedena."

**Primedba je delimično tačna i vredi je priznati.** Statusni kod jeste pojam iz HTTP-a i u čistoj varijanti Presenter bi vraćao svoj tip ishoda — recimo `Uspeh`, `NeispravanUnos`, `NePostoji`, `Sukob` — a granica bi ga preslikala u broj.

Svesno sam odabrao drugačije, iz dva razloga. Prvi je da su ta četiri ishoda ionako jedan-na-jedan preslikana, pa bi dodatni skup imena bio sloj bez sadržaja. Drugi je što granica time ostaje bez ijedne odluke, a to mi je bilo važnije: ako bi granica birala kod, morala bi da zna šta koja greška znači, i pravilo bi iscurilo iz Presentera u infrastrukturu.

Ono što jeste sprovedeno je važnija granica: Presenter **ne zna kako izgleda prikaz**. Ne pravi HTML, ne zna za dugmad ni tabele, ne bira boje ni raspored. Vraća podatke i ishod. Da sutra zamenim HTTP nečim drugim, promena bi bila u `granica.py` i u jednom rečniku preslikavanja, ne u pravilima.

### 2. „Tvrdite da View ne zna za model. Ali `view.js` barata imenima `cena_po_komadu`, `ukupan_iznos`, `narudzbina_id` — to su imena kolona u vašoj bazi. Znači View savršeno dobro poznaje model."

**Imena se poklapaju i to je tačno zapažanje.** Ali ono što View poznaje nije model — to je **ugovor koji Presenter objavljuje**. Imena su ista zato što ih Presenter nije preimenovao, a nije ih preimenovao zato što bi preimenovanje bez razloga bilo samo šum.

Razlika se vidi na testu koji se može izvesti odmah: ako u bazi preimenujem kolonu `cena_po_komadu`, a u `u_recnik()` ostavim isti ključ, **View se ne menja**. Obrnuto važi isto — mogu da promenim ugovor, a da baza ostane ista. To znači da veza nije direktna, nego posredovana, i to je upravo ono što MVP traži.

Pravi test „zna li View za model" nije poklapanje imena nego pristup: ne postoji način da `view.js` pročita red iz baze, izvrši upit, ili sazna nešto što mu Presenter nije vratio. Kad bih obrisao Presenter, imena bi ostala, ali podataka ne bi bilo.
