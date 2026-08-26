# ODBRANA — seminarski rad iz Društvenog računarstva

**Rad:** *Kako se ton korisničkih recenzija menja sa iskustvom — analiza 45.070 Steam
recenzija igre Dota 2* (`seminarski.ipynb`, `seminarski.pdf`)

Ovaj fajl je skripta za odbranu. Svako poglavlje rada je povezano sa **celinom u pripremi
za kolokvijum**, gde je teorija tog alata već objašnjena. Ako te profesor prekine pitanjem
„šta je to tačno", tamo je odgovor.

| fajl | čemu služi |
|---|---|
| `ODBRANA.md` (ovaj) | šta pričaš, kojim redom, i odgovori na pitanja |
| [`seminarski.ipynb`](seminarski.ipynb) | rad koji pokazuješ (izvršen, sa grafikonima) |
| [`seminarski.pdf`](seminarski.pdf) | rezerva ako notebook neće da se otvori |
| [`../kolokvijumi_priprema/K1_priprema.ipynb`](../kolokvijumi_priprema/K1_priprema.ipynb) | teorija: tokenizacija, stop-reči, sentiment, n-grami |
| [`../kolokvijumi_priprema/K2_priprema.ipynb`](../kolokvijumi_priprema/K2_priprema.ipynb) | teorija: preprocesiranje, BoW/TF-IDF, POS, NER, MNB |

---

## 0. Priprema, 10 minuta pre

```bash
python -m jupyter notebook seminarski.ipynb
```

- [ ] notebook je **izvršen** — svi grafikoni se vide bez ponovnog pokretanja
      (ako nije, pusti *Run All*; traje par minuta zbog 45.070 redova)
- [ ] `seminarski.pdf` otvoren u drugom prozoru, kao rezerva
- [ ] `data/recenzije.csv` na mestu (7 MB)
- [ ] u drugom tabu otvorena **priprema za K1** — ako pitaju teoriju, pokazuješ odakle znaš
- [ ] znaš napamet brojeve iz odeljka 5 ovog fajla

---

## 1. Rad u tri rečenice

> „Steam uz svaku recenziju čuva i koliko je sati igre autor imao **u trenutku pisanja**.
> To sam iskoristio da izmerim da li se ton recenzije menja sa iskustvom korisnika.
> Nalaz je da se menja — i da se tri efekta spajaju tako da ono što platforma prikazuje
> na vrhu stranice bude znatno negativnije od stvarnog raspoloženja igrača."

Ako te pitaju **zašto je to tema iz društvenog računarstva**, a ne iz statistike:

> „Zato što se ne meri samo tekst, nego posledica **algoritma rangiranja**. Recenzija je
> društveni artefakt — nastaje u zajednici, glasa se o njoj, a platforma odlučuje koja se
> vidi. Rad meri koliko se ta vidljiva slika razlikuje od stvarne raspodele mišljenja."

---

## 2. Mapa: alat u radu → teorija u pripremi za kolokvijum

Ovo je najvažnija tabela u fajlu. Levo je ono što se vidi u radu, desno mesto gde je to
objašnjeno — otvori i pokaži ako zatreba.

| poglavlje rada | alat / postupak | teorija |
|---|---|---|
| 2. Podaci | učitavanje iz fajla sa `encoding="utf-8"` | **K1 · Celina 1 — Učitavanje podataka** |
| 3. Preprocesiranje | uklanjanje URL-ova i BBCode-a regularnim izrazom | **K1 · Celina 2 — Čišćenje teksta** |
| 3. Preprocesiranje | `word_tokenize`, mala slova, `isalpha()` | **K1 · Celina 3 — Tokenizacija**; **K2 · Celina 2 — Standardno preprocesiranje** |
| 3. Preprocesiranje | stop-reči (`stopwords.words("english")`) | **K1 · Celina 4 — Stop-reči i frekvencije** |
| 5. Sentiment | `TextBlob` — `polarity`, `subjectivity` | **K1 · Celina 6 — Analiza sentimenta** |
| 5. Sentiment | VADER — `SentimentIntensityAnalyzer`, `compound` | **K1 · Celina 6** |
| 9. O čemu ko piše | `TfidfVectorizer`, `get_feature_names_out()` | **K2 · Celina 4 — Bag of Words i TF-IDF** |
| 10. N-grami | `nltk.util.ngrams`, `Counter.most_common` | **K1 · Celina 7 — N-grami**; brojanje: **K1 · Celina 4** |
| svuda | `pandas` `DataFrame`, `groupby`, `describe` | **K1 · Celina 8**, **K2 · Celina 11** (kompletna rešenja zadataka) |

**Šta u radu NIJE korišćeno, a jeste u pripremi** — pripremi odgovor, pitanje je verovatno:

| tehnika | gde je teorija | zašto nije u radu |
|---|---|---|
| stemming / lematizacija | K1 · Celina 5 | Meri se **ton i dužina**, ne rečnik. Svođenje na osnovu ne menja sentiment, a TF-IDF nad neizvedenim oblicima daje čitljivije reči u ispisu. |
| POS-tagging | K2 · Celina 5 | Ne postavlja se pitanje o vrstama reči. |
| NER | K2 · Celina 6 | U recenzijama nema imena ljudi ni mesta — nema šta da se izdvoji. |
| MNB klasifikacija | K2 · Celina 10 | Cilj nije bio **predviđati** ocenu (ona već postoji u koloni `preporucuje`), nego **objasniti** njeno kretanje. |

Ako pitaju „zašto nisi radio klasifikaciju" — to je pravi odgovor: ciljna promenljiva je
već data, pa je klasifikacija suvišan korak. Ali dodaj da bi to bio prirodan nastavak:
`CountVectorizer` + `MultinomialNB` nad dugim recenzijama, tačno kao u K2 · Celina 10.

---

## 3. Izlaganje, poglavlje po poglavlje (10–12 minuta)

### Poglavlje 2 — Podaci (1,5 min)

**Pokaži:** ispis sa 45.070 recenzija i poređenje 80,4% naspram zvaničnih 80,6%.

> „Podaci su skinuti sa zvaničnog Steam API-ja, sa endpointa `appreviews/570`, gde je 570
> identifikator Dota 2. Ključna kolona je `sati_pri_pisanju` — `playtime_at_review` —
> sati u trenutku pisanja, a ne trenutni broj sati. Bez tog polja rad ne bi bio moguć,
> jer bih poredio današnje iskustvo sa recenzijom od pre tri godine."

**Odmah zatim reci proveru reprezentativnosti** — time preduhitriš pitanje:

> „Steam zvanično prijavljuje 80,6% pozitivnih za ovu igru. Moj uzorak ima 80,4%.
> Poklapanje pokazuje da uzorak nije pristrasan po sentimentu."

Sortiranje po korisnosti degradira sa dubinom (prvih 500 recenzija ima medijanu od 28
reči, na 2.500 već svega 5), pa je strategija bila **skupiti obim pa filtrirati po dužini**.

### Poglavlje 3 — Preprocesiranje (1 min)

**Pokaži:** ćeliju sa funkcijom `preprocesiraj` i ispis SIROVO → TOKENI.

> „Redosled je: BBCode, pa URL, pa interpunkcija, pa mala slova, pa tokenizacija, pa
> stop-reči. BBCode je dodatak specifičan za Steam — recenzije mogu imati oznake tipa
> `[b]` ili `[url=...]`, koje bi tokenizator inače razbio na besmislene tokene."

**Naglasi redosled, to je klasično pitanje:**

> „URL se uklanja **pre** interpunkcije. Ako prvo obrišeš interpunkciju, `https://t.co/abc`
> postane `httpstcoabc` i regularni izraz za URL ga više ne prepoznaje."

To je doslovno zamka navedena u **K1 · Celina 2**.

**Granica od 30 reči:** analiza sadržaja nema smisla nad recenzijom od tri reči, a medijana
celog skupa **jeste** tri reči. Zato: sadržaj se analizira nad dugim recenzijama, a ocena
(`preporucuje`) nad celim skupom, jer tamo dužina nije prepreka.

### Poglavlje 5 — Sentiment i provera alata (2 min)

**Pokaži:** tabelu slaganja i dva histograma.

Ovo je poglavlje koje najviše vredi na odbrani, jer pokazuje da alat nisi uzeo zdravo za
gotovo:

> „Imam korisnikov sopstveni palac gore/dole u koloni `preporucuje`. To sam iskoristio kao
> **tačan odgovor** i proverio koliko su TextBlob i VADER pouzdani na ovom materijalu.
> TextBlob pogađa 65,7%, VADER 65,5%, a bazna linija — da uvek kažeš 'pozitivno' — je
> 50,5% na tom poduzorku. Znači, bolji su od pogađanja, ali daleko od pouzdanog."

> „Razlog je priroda materijala: gejmerske recenzije su pune ironije i šale — *10/10 would
> lose MMR again* je pozitivna ocena napisana kao žalba. Ni TextBlob ni VADER to ne
> razumeju. Zato u nastavku kao meru tona koristim `preporucuje`, a automatski sentiment
> ostaje samo dopuna."

Teorija: **K1 · Celina 6**. Ako pitaju razliku — VADER je pravljen za društvene mreže i
razume emotikone, velika slova i uzvičnike; TextBlob je opšti i vraća i `subjectivity`.

### Poglavlje 6 — Prvi nalaz: ton opada sa iskustvom (2,5 min)

**Pokaži:** tabelu po opsezima sati i grafikon obrnutog U.

> „Kriva ima oblik obrnutog U. Udeo pozitivnih raste do vrha u opsegu 100–250 sati, gde je
> 89%, pa ravnomerno opada do 66% kod igrača sa preko 8.000 sati. To je pad od oko 23
> procentna poena."

> „Spearmanov koeficijent je minus 0,13, sa p-vrednošću reda 10 na minus 168. Veza je po
> apsolutnoj vrednosti slaba, ali pri uzorku od 45.070 nesumnjivo postoji. Hi-kvadrat test
> veterana naspram ostalih daje 644 sa p reda 10 na minus 142."

**Odmah dodaj tumačenje**, da ne ostane suvi broj:

> „Novi igrači ocenjuju prvi utisak. Igrači sa nekoliko stotina sati su u fazi najvećeg
> entuzijazma. Veterani ocenjuju kroz godine promena — pravila, matchmaking, ponašanje
> zajednice. Njihova recenzija nije o prvom utisku nego o godinama igranja."

### Poglavlje 7 — Konfaund (1,5 min)

Ovo poglavlje postoji **da bi preduhitrilo prigovor**. Reci to otvoreno:

> „Očigledan prigovor je da veterani nisu negativniji zbog iskustva, nego zato što su
> pisali kasnije, kada je igra bila u lošijem stanju. Zato sam podelio podatke po godini i
> ponovio test **unutar** svake godine posebno."

> „U 2025. je rho minus 0,138, u 2026. minus 0,105. Trend se drži u obe godine, sa istim
> smerom. Pad između 2025. i 2026. jeste stvaran, ali je zaseban efekat — ne objašnjava
> razliku između novajlija i veterana unutar iste godine."

Ako pitaju šta je konfaund: **treća promenljiva koja utiče i na uzrok i na posledicu i
tako pravi lažnu vezu.** Ovde bi to bio period pisanja.

### Poglavlje 8 — Drugi nalaz: pristrasnost dužine (2 min)

**Pokaži:** vodoravni bar-grafikon.

> „Ovo je najvažniji nalaz. Ceo skup je 80% pozitivan. Kratke recenzije, ispod 30 reči, su
> 83% pozitivne. Duge, preko 30 reči, padaju na 51%. Preko 100 reči — 45%. Razlika prelazi
> 30 procentnih poena."

> „Objašnjenje je jednostavno: ljudi pišu opširno kada su nezadovoljni. Zadovoljni napišu
> 'gg' ili šalu. Uz to, dužina raste sa iskustvom — Spearman je plus 0,14 — pa veterani
> pišu duže, prosečno 17 reči naspram 9 kod novajlija."

**Zaključak koji treba da izgovoriš sporo:**

> „Tri efekta se spajaju. Veterani su negativniji. Veterani pišu duže. Duge recenzije su
> negativnije. A platforma na vrh stranice gura duge, izglasane recenzije. Znači kupac koji
> otvori stranicu igre vidi uzorak koji je znatno negativniji od stvarnog raspoloženja
> igrača — i to ne zbog nečije namere, nego zbog načina na koji algoritam bira šta će
> prikazati."

### Poglavlje 9 — TF-IDF i teme (1,5 min)

**Budi iskren, ovde je rezultat slab** — vidi odeljak 7, tačka 1.

> „Recenzije sam grupisao u četiri opsega iskustva, svaki tretirao kao jedan dokument, i
> pustio TF-IDF da izdvoji karakteristične reči. Rezultat je slabiji nego što sam očekivao
> — sve četiri grupe daju iste reči, `game`, `dota`, `play`. Razlog je što imam samo četiri
> dokumenta: IDF komponenta kažnjava reč koja je u svim dokumentima, ali kad ih je četiri,
> gotovo svaka česta reč je u sva četiri i kazna izostane."

> „Zato sam dodao drugi pristup — ručno definisane teme sa listama ključnih reči. Tu se
> razlika jasno vidi: novajlije pišu o učenju i težini igre, 35% naspram 25% kod veterana,
> a veterani o matchmakingu, 25% naspram 14%, i o toksičnosti, 28% naspram 10%."

Teorija TF-IDF: **K2 · Celina 4**. Formula koju treba da znaš:

```
tfidf(t, d) = tf(t, d) × log(N / df(t))
```

`tf` je koliko puta je reč u ovom dokumentu, `df` u koliko dokumenata se uopšte javlja,
`N` je ukupan broj dokumenata. Ako je reč svuda, `df = N`, logaritam je nula, težina pada
na nulu. **Kod mene je N = 4, pa taj mehanizam praktično ne radi** — to je poenta.

### Poglavlje 10 — N-grami (1 min)

**Ovde obavezno reci ograničenje pre nego što te pitaju** (vidi odeljak 7, tačka 2):

> „N-grami pokazuju najčešće fraze u pozitivnim i negativnim recenzijama. Rezultat je
> zagađen: prvih nekoliko bigrama dolazi iz **pojedinačnih recenzija koje jednu reč
> ponavljaju dvesta puta**. Proverio sam — `zov zov` se javlja 191 put, a sve to je jedna
> jedina recenzija od 192 reči. Da bih to sredio, trebalo bi da brojim **u koliko
> recenzija** se fraza javlja, a ne koliko puta ukupno."

To je zrelo zapažanje i bolje zvuči nego da ga profesor nađe.

### Poglavlje 11 — Zaključak (1 min)

Četiri nalaza, pa jedna rečenica o društvenom računarstvu, pa ograničenja. Ograničenja
**pročitaj naglas** — to je deo koji pokazuje da razumeš domet sopstvenog rada.

---

## 4. Teorija koju moraš znati napamet

Kratki podsetnici. Svaki upućuje na celinu gde je razrađeno.

### 4.1 Preprocesiranje — redosled (K1 · Celina 2, K2 · Celina 2)

**BBCode → URL → interpunkcija → mala slova → tokenizacija → stop-reči.**

Zašto tim redom: sve što je **struktura** (oznake, linkovi) mora da ode dok je još celo.
Čim obrišeš interpunkciju, link i oznaka se raspadnu na delove koje više ne prepoznaješ.

„Standardno preprocesiranje" na predmetu znači: mala slova, tokenizacija, izbaci
interpunkciju, izbaci stop-reči.

### 4.2 Tokenizacija (K1 · Celina 3)

| tokenizator | ponašanje |
|---|---|
| `word_tokenize` | opšti; `don't` → `do` + `n't`; interpunkcija je zaseban token |
| `TweetTokenizer` | čuva `@mention`, `#hashtag`, emotikone kao **jedan** token |
| `WordPunctTokenizer` | deli slova od ne-slova; `don't` → `don` + `'` + `t` |
| `RegexpTokenizer(r"\w+")` | samo nizovi slova i cifara, interpunkcija nestaje |

U radu koristim `word_tokenize`, jer Steam recenzija nije tweet — nema mentiona ni
hashtagova, ima BBCode, a njega rešavam regularnim izrazom pre tokenizacije.

### 4.3 Stop-reči i frekvencije (K1 · Celina 4)

Stop-reči su česte reči bez sadržaja (`the`, `is`, `at`). Uklanjaju se jer bi inače
zauzele ceo vrh svake frekvencijske liste. `Counter.most_common(n)` vraća `n` najčešćih
kao listu parova `(token, broj)`.

U mojoj funkciji dodatno tražim `w.isalpha()` i `len(w) > 2` — izbacuje brojeve i ostatke.

### 4.4 Stemming naspram lematizacije (K1 · Celina 5)

**Stemming** seče sufikse po pravilima, brz je, rezultat **ne mora biti prava reč**
(`studies` → `studi`). **Lematizacija** vraća pravu rečničku osnovu preko WordNet-a.

Zamka koju treba da izgovoriš ako pitaju: `WordNetLemmatizer` podrazumevano pretpostavlja
da je reč **imenica**, pa `running` ostaje `running`. Za glagole mora
`lemmatize(rec, pos="v")`.

Nije korišćeno u radu — objašnjenje u odeljku 2.

### 4.5 TextBlob i VADER (K1 · Celina 6)

- `TextBlob(t).sentiment.polarity` ∈ [−1, 1] — negativno / neutralno / pozitivno
- `TextBlob(t).sentiment.subjectivity` ∈ [0, 1] — 0 činjenica, 1 lično mišljenje
- VADER `polarity_scores(t)` → `neg`, `neu`, `pos`, `compound` ∈ [−1, 1]

VADER je pravljen za društvene mreže: razume emotikone, VELIKA SLOVA i `!!!`.

Zamka: **TextBlob očekuje tekst, ne listu tokena.** Ako mu daš listu, puca. Zato
`" ".join(tokeni)`.

### 4.6 BoW i TF-IDF (K2 · Celina 4)

**BoW** je prosto brojanje pojavljivanja, redosled se gubi — `not good` i `good not`
izgledaju isto. **TF-IDF** koriguje BoW tako da kazni reč koja se javlja svuda. Formula je
gore, u poglavlju 9.

### 4.7 N-grami (K1 · Celina 7)

N-gram je niz od `n` uzastopnih reči. Za `["a","b","c","d"]` bigrami su
`(a,b), (b,c), (c,d)`. `nltk.util.ngrams(tokeni, n)` vraća generator, pa ide u `Counter`.

### 4.8 Statistika koju koristim

| test | šta meri | vrednost u radu |
|---|---|---|
| **Spearman** `rho` | monotona veza dve promenljive, po rangu a ne po vrednosti | −0,13 (sati vs ocena), +0,14 (sati vs dužina) |
| **p-vrednost** | verovatnoća da bi se ovakav rezultat javio slučajno | 10⁻¹⁶⁸ i 10⁻¹⁹⁹ — praktično nula |
| **hi-kvadrat** | da li se dve kategorije razlikuju po raspodeli | 644,3 za veterane naspram ostalih |

Ako pitaju **zašto Spearman a ne Pearson**: zato što sati igre imaju izrazito iskošenu
raspodelu preko četiri reda veličine, a `preporucuje` je binarno. Spearman radi na
rangovima i ne pretpostavlja ni normalnost ni linearnost.

Ako pitaju **je li rho od 0,13 mala veza**: jeste, i tako je i napisano u radu. Ali pri
n = 45.070 nije slučajna, a razlika u udelima — 89% naspram 66% — je praktično velika.
Nizak rho i velika razlika u krajevima idu zajedno kad veza nije monotona (obrnuto U).

---

## 5. Brojevi koje moraš znati napamet

| šta | vrednost |
|---|---|
| ukupno recenzija | **45.070** |
| kolona u skupu | 21 |
| udeo pozitivnih (uzorak / Steam zvanično) | **80,4% / 80,6%** |
| godine | 2025: 24.403 · 2026: 20.667 |
| medijana dužine / prosek | **3 reči** / 11,1 |
| duge (≥ 30 reči) | 3.054, tj. 6,8% |
| medijana sati / maksimum | 767h / 40.067h |
| vrh krive (100–250h) | **89,0% pozitivnih** |
| dno krive (8.000h+) | **66,3% pozitivnih** |
| veterani 4.000h+ naspram ostalih | 69,3% naspram 82,4% |
| Spearman sati vs ocena | **rho = −0,1295**, p = 9,1 · 10⁻¹⁶⁸ |
| Spearman sati vs dužina | **rho = +0,1410**, p = 6,7 · 10⁻¹⁹⁹ |
| hi-kvadrat | 644,3, p = 3,8 · 10⁻¹⁴² |
| kratke (<30) / duge (≥30) / ≥100 reči | 82,6% / **50,7%** / 44,9% |
| dužina: novajlije naspram veterana (prosek) | 9,0 naspram 16,8 reči |
| TextBlob / VADER slaganje / bazna linija | 65,7% / 65,5% / 50,5% |

Ako zaboraviš tačan broj — reci red veličine i otvori ćeliju. Bolje nego pogrešna cifra.

---

## 6. Pitanja i odgovori

### A. Teorijska pitanja o alatima

**Šta je tokenizacija?**
Deljenje teksta na jedinice — tokene. Različiti tokenizatori daju različit rezultat na
istom ulazu, pa izbor zavisi od materijala. *(K1 · Celina 3)*

**Zašto uklanjaš stop-reči?**
Zato što su najčešće, a ne nose sadržaj. Bez toga bi vrh svake frekvencijske liste bio
`the`, `is`, `and`. *(K1 · Celina 4)*

**Koja je razlika između stemminga i lematizacije?**
Stemming seče sufikse po pravilima i može dati oblik koji nije reč. Lematizacija koristi
rečnik WordNet i vraća pravu osnovu, ali joj treba vrsta reči. *(K1 · Celina 5)*

**Šta vraća TextBlob?**
`polarity` u opsegu −1 do 1 i `subjectivity` u opsegu 0 do 1. *(K1 · Celina 6)*

**Po čemu se VADER razlikuje?**
Pravljen je za društvene mreže — razume emotikone, velika slova i interpunkciju kao
pojačivače. Vraća `neg`, `neu`, `pos` i zbirni `compound`. *(K1 · Celina 6)*

**Šta je TF-IDF i čemu služi?**
Težina reči u dokumentu, `tf × log(N/df)`. Kažnjava reči koje se javljaju u svim
dokumentima, pa izdvaja ono što je karakteristično za jedan. *(K2 · Celina 4)*

**Šta je n-gram?**
Niz od n uzastopnih reči. Koristi se za fraze i za predikciju sledeće reči.
*(K1 · Celina 7)*

**Šta je BoW i koja mu je mana?**
Vreća reči — samo brojanje pojavljivanja. Mana: gubi se redosled, pa `not good` i
`good not` izgledaju isto. *(K2 · Celina 4)*

### B. Pitanja o radu

**Odakle podaci?**
Zvanični Steam API, `store.steampowered.com/appreviews/570`. Skinute su sve tri kategorije
sortiranja i spojene bez duplikata po `recommendationid`.

**Koliko podataka i kako znaš da nisu pristrasni?**
45.070 recenzija. Provera: Steam zvanično prijavljuje 80,6% pozitivnih, moj uzorak ima
80,4%. Poklapanje po sentimentu.

**Koja je ključna promenljiva?**
`sati_pri_pisanju` — `playtime_at_review`. Sati **u trenutku pisanja**, ne trenutni. Bez
tog polja rad nije moguć, jer bi se današnje iskustvo poredilo sa starom recenzijom.

**Zašto granica od 30 reči?**
Medijana celog skupa je 3 reči. Analiza sadržaja nad tri reči nema smisla. Zato: sadržaj
nad dugim recenzijama, ocena nad celim skupom.

**Zašto koristiš `preporucuje` a ne sentiment alat kao meru tona?**
Zato što sam alate proverio i dobio slaganje od oko 65%. `preporucuje` je korisnikova
sopstvena, nedvosmislena ocena. Alat koji greši u trećini slučajeva ne može biti glavna
mera.

**Šta znači obrnuto U na grafikonu?**
Da veza nije prosta linija. Ton prvo **raste** sa iskustvom, do oko 250 sati, pa opada.
Zato je i Spearmanov rho relativno nizak — nemonotona veza se slabo hvata jednim brojem.

**Kako si isključio da je stvar u vremenu, a ne u iskustvu?**
Podelom po godini i ponavljanjem testa unutar svake. Trend se drži i u 2025. i u 2026.
sa istim smerom.

**Koji je glavni zaključak?**
Da vidljiva slika proizvoda sistematski odstupa od stvarnog raspoloženja korisnika, zbog
načina na koji algoritam rangiranja bira šta će se prikazati — a ne zbog nečije namere.

### C. Neprijatna pitanja

**TF-IDF ti daje iste reči za sve četiri grupe. Znači nije radio?**
Tačno, i tako je i napisano. Razlog je što imam samo četiri dokumenta — IDF kažnjava reč
koja je u svim dokumentima, ali pri N = 4 skoro svaka česta reč jeste u sva četiri, pa
kazna izostane. Zato sam dodao ručno definisane teme, koje jesu pokazale razliku. Ispravno
bi bilo da svaka recenzija bude zaseban dokument, pa da se težine prosečno uzmu po grupi.

**Tvoji bigrami su `zov zov` i `smurf smurf`. To je smeće.**
Jeste, i proverio sam odakle dolazi: `zov zov` se javlja 191 put, a sve to je **jedna
recenzija** koja tu reč ponavlja 192 puta. Isto važi za `lancerphantom` (199 puta u jednoj
recenziji) i `smurf` (176). Greška je što brojim ukupna pojavljivanja umesto broja
recenzija u kojima se fraza javlja. Ispravka je jednoredna — `set(ngrams(...))` po
recenziji pre brojanja.

**Recenzije preko 200 reči su 47%, a preko 100 su 45%. Zar nije trebalo da bude niže?**
Trend nije savršeno monoton, tačno. Grupa preko 200 reči ima svega 303 recenzije, pa je
oscilacija te veličine očekivana. Tvrdnja koju branim je da duge recenzije padaju ispod
50%, i to važi za obe granice.

**rho od 0,13 je vrlo slaba veza. Kako na tome gradiš zaključak?**
Ne gradim na rho, nego na razlici u udelima — 89% naspram 66% po iskustvu, i 83% naspram
51% po dužini. Rho je nizak jer veza nije monotona, u obliku je obrnutog U, a Spearman
meri monotonost. Statistička značajnost pri n = 45.070 samo potvrđuje da nije slučajno.

**Uzorak ti je iz 2025. i 2026. Nije li to premalo za tvrdnju o promeni kroz vreme?**
Jeste, i zato takvu tvrdnju ne iznosim. Rad je presek stanja. Godina se koristi samo kao
kontrola, da se pokaže da nalaz nije artefakt perioda.

**Sve su ti recenzije na engleskom. Šta sa ostalima?**
U sirovom feedu oko 80% čini ruski jezik. Analiza je svesno ograničena na engleski, jer su
NLTK-ove stop-reči, TextBlob i VADER pravljeni za engleski. Zaključak se zato odnosi na
englesku populaciju recenzenata, ne na sve korisnike. To je navedeno u ograničenjima.

**Možeš li tvrditi da iskustvo uzrokuje negativniji stav?**
Ne. Veza je korelaciona. Moguće je i obrnuto tumačenje — da nezadovoljni igrači iz drugih
razloga duže ostaju. Za uzročnost bi trebalo pratiti iste korisnike kroz vreme.

**Gde ti je skripta kojom si prikupljao podatke?**
U radu se pominje `03_prikupi_recenzije.py`, ali u ovom folderu je samo rezultat,
`data/recenzije.csv`. Postupak mogu da opišem: poziv na `appreviews/570` sa parametrima
`filter`, `language=english`, `num_per_page=100`, i straničenje kroz `cursor` dok ima
rezultata, uz spajanje po `recommendationid`.

**Zašto nisi koristio ništa sa drugog kolokvijuma osim TF-IDF?**
Zato što ostalo ne odgovara materijalu. NER traži imena i mesta, kojih u recenzijama nema.
POS-tagging bi imao smisla da pitam **kako** je nešto napisano, a ja pitam **koliko
pozitivno**. MNB je klasifikacija, a ciljna promenljiva mi je već data u podacima.

### D. „Uradi uživo"

Očekuj da ti kažu da nešto pokreneš. Pripremi se za ovo troje:

**1. Promeni granicu sa 30 na 50 reči i pusti ponovo.**
Menjaš `GRANICA = 30` u poglavlju 3 i pokrećeš ćelije ispod. Očekivano: broj dugih pada,
udeo pozitivnih među dugima pada još malo.

**2. Dodaj temu u rečnik `TEME`.**
U poglavlju 9, na primer `"lag": ["lag", "ping", "server", "servers", "disconnect"]`.
Pokreni ćeliju — tabela i grafikon se sami ažuriraju.

**3. Izračunaj sentiment za jednu rečenicu.**

```python
from textblob import TextBlob
TextBlob("this game is amazing but the matchmaking is broken").sentiment
vader.polarity_scores("this game is amazing but the matchmaking is broken")
```

Umej da objasniš zašto se dva rezultata razlikuju.

---

## 7. Slabosti rada — reci ih ti, prvi

Tri stvari koje bi profesor mogao da nađe. Ako ih sam izneseš, prestaju da budu zamerka.

**1. TF-IDF nad četiri dokumenta praktično ne radi.**
Sve četiri grupe daju `game`, `dota`, `play`. Objašnjenje i ispravka su u odeljku 6.C.

**2. N-grami broje ukupna pojavljivanja, ne broj recenzija.**
Zbog toga jedna recenzija koja ponavlja jednu reč 192 puta zauzima vrh liste. Provereno na
tri slučaja: `zov` (192 puta u jednoj recenziji), `lancerphantom` (199), `smurf` (176).

**3. Uzorak je 94% iz kategorije „recent".**
Od 45.070 recenzija, 42.564 su iz strategije `recent`, a 2.506 iz `all`. Znači uzorak je
bliži pitanju „šta se piše ovih meseci" nego slučajnom uzorku svih recenzija ikada.
Odbrana: poklapanje sa zvaničnih 80,6% pokazuje da po sentimentu nije iskrivljen, a analiza
po godini pokazuje da nalaz nije vezan za period.

---

## 8. Kontrolna lista pred ulazak

- [ ] umeš da izgovoriš istraživačko pitanje u jednoj rečenici
- [ ] znaš zašto je `sati_pri_pisanju` ključna kolona
- [ ] znaš napamet: 45.070 · 80,4% · 89% na vrhu · 66% na dnu · 51% duge · rho −0,13
- [ ] umeš da objasniš redosled preprocesiranja i **zašto URL ide pre interpunkcije**
- [ ] znaš razliku između TextBlob i VADER i zašto si ih proveravao
- [ ] umeš da napišeš formulu TF-IDF i objasniš zašto kod tebe nije razdvojila grupe
- [ ] umeš da objasniš šta je konfaund i kako si ga isključio
- [ ] znaš razliku Spearman naspram Pearson i zašto Spearman
- [ ] umeš da kažeš tri ograničenja rada bez gledanja
- [ ] pripremljene su tri slabosti iz odeljka 7 — izgovaraš ih sam
- [ ] notebook je izvršen i grafikoni se vide
