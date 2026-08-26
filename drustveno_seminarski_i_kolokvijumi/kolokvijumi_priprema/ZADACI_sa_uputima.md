# Kolokvijumski zadaci — celokupan tekst sa uputima

Predmet: **Društveno računarstvo**

Ovaj fajl sadrži **pun tekst oba kolokvijumska zadatka**, razložen na korake. Uz svaki
korak stoji uput na:

- **notebook sa vežbi** iz `drustvenoRacunarstvo/` gde je ta tehnika obrađena
- **celinu** u `K1_priprema.ipynb` / `K2_priprema.ipynb` gde je objašnjena i rešena

Putanje su relativne u odnosu na `C:\Users\Blagoje\Documents\drustvenoRacunarstvo\`.

---

## Mapa gradiva → vežbe

| tema | notebook sa vežbi | PDF |
|---|---|---|
| Tokenizacija (`word_tokenize`, `TweetTokenizer`, `WordPunctTokenizer`, `RegexpTokenizer`), stop-reči, `Counter` | `Vežbe 2026/V1/v1.ipynb`, `Vežbe 2026/V1/v2.ipynb` | — |
| Stemming (Porter, Lancaster, Snowball) | `Vežbe 2026/V2/primer (2).ipynb` | `Vežbe 2026/V2/drv2.pdf` |
| Lematizacija, POS-tagging, VADER sentiment | `Vežbe 2026/V3/primer.ipynb`, `Vežbe 2026/V3/lematizacija.ipynb` | `Vežbe 2026/V4/drV4.pdf` |
| Preprocesiranje tweet-ova — **priprema za K1** | `Vežbe 2026/V5/V5 (1).ipynb`, `Vežbe 2026/V5/V5_resenje.ipynb` | `Vežbe 2026/V5/dr5.pdf` |
| Zadaci za II kolokvijum | `Vežbe 2026/V8/v10 (1).ipynb` | `Vežbe 2026/V7/V7 (5).pdf`, `Vežbe 2026/V8/V8 (5).pdf` |
| Sažimanje teksta (`heapq.nlargest`, `BeautifulSoup`) | `Vežbe 2026/V9/text_summarization (2).ipynb` | `Vežbe 2026/V9/DRV9.pdf` |
| Dataset iz kolekcije dela — **priprema za K2** | `Vežbe 2026/V10/k2 (1) (1).ipynb`, `Vežbe 2026/V11/k2 ispravak (2).ipynb` | — |
| Word2Vec / gensim | `Vežbe 2026/V13/gensim (2).ipynb` | `Vežbe 2026/V13/V13.pdf` |

> **Napomena:** nazivi foldera i PDF-ova se ne poklapaju uvek (folder `V4` sadrži PDF za
> „vežbe 3", folder `V5` PDF za „vežbe 4", folder `V8` PDF za „vežbe 10"). Idi po sadržaju,
> ne po broju u imenu foldera.

---
---

# I KOLOKVIJUM

**Izvor:** `k1/K1/okto1.pdf`
**Podaci:** `tweets.json` (500 tweet-ova u punom Twitter formatu)
**Rešenje:** `K1_priprema.ipynb`, Celina 8

---

### Tačka 1
> Učitati `tweets.json` i iz njega izdvojiti tekstualne sadržaje prvih 20 tweet-ova.
> Sve buduće zadatke raditi sa ovim skupom.

```python
with open("data/tweets.json", encoding="utf-8") as f:
    svi = json.load(f)
tweets = [t["text"] for t in svi[:20]]
```

**Uput:** `Vežbe 2026/V1/v1.ipynb` — učitavanje i osnovni rad sa podacima.
**Teorija:** `K1_priprema.ipynb` → **Celina 1**.

**Pazi:** `tweets.json` je **lista rečnika**, ne rečnik. Tekst je u polju `text`.
Obavezno `encoding="utf-8"` — bez toga puca na prvom emotikonu.

---

### Tačka 2
> Odraditi tokenizaciju tweet-ova koristeći `TweetTokenizer`. Rezultat ove operacije je
> kolekcija tokenizovanih tweet-ova, koju ćemo zvati **skup1**.

```python
tt = TweetTokenizer(preserve_case=False)
skup1 = [tt.tokenize(t) for t in tweets]
```

**Uput:** `Vežbe 2026/V1/v1.ipynb` i `v2.ipynb` — poređenje svih tokenizatora.
**Teorija:** `K1_priprema.ipynb` → **Celina 3**.

**Pazi:** `TweetTokenizer` čuva `@mention`, `#hashtag` i emotikone kao **jedan token** —
po tome se razlikuje od `word_tokenize`. Parametri: `preserve_case`, `strip_handles`,
`reduce_len`.

---

### Tačka 3
> Kreirati funkciju za tokenizaciju, koja razdvaja svaku reč po razmaku, uklanja znake
> interpunkcije i sve URL-ove. Ovako dobijamo **skup2**.

```python
def moja_tokenizacija(tekst):
    tekst = URL_RE.sub(" ", tekst)          # URL PRE interpunkcije
    tokeni = []
    for rec in tekst.split():
        rec = rec.strip(string.punctuation)
        rec = rec.translate(str.maketrans("", "", string.punctuation))
        if rec:
            tokeni.append(rec.lower())
    return tokeni
```

**Uput:** `Vežbe 2026/V1/v2.ipynb` — odeljak *„Tokenizacija upotrebom split metode"*.
**Teorija:** `K1_priprema.ipynb` → **Celina 2 i 3**.

**Najvažnija zamka celog kolokvijuma:** URL se mora ukloniti **pre** interpunkcije.
Ako obrneš redosled, `https://t.co/abc` postane `httpstcoabc` i regex ga više ne prepoznaje.

---

### Tačka 4
> Iz oba skupa ukloniti 2 najčešća tokena.

```python
ukupno = Counter(t for dok in skup for t in dok)
izbaci = {t for t, _ in ukupno.most_common(2)}
skup_bez2 = [[t for t in dok if t not in izbaci] for dok in skup]
```

**Uput:** `Vežbe 2026/V1/v1.ipynb` — `Counter` i stop-reči.
**Teorija:** `K1_priprema.ipynb` → **Celina 4**.

**Pazi:** najčešći tokeni se računaju **preko celog skupa**, ne po tweet-u. I računaju se
**posebno za skup1 i skup2**, jer se skupovi razlikuju.

---

### Tačka 5
> Odraditi `TextBlob` analizu sentimenta za oba skupa tweet-ova i porediti rezultate.
> Kreirati dataframe sa kolonama za tweet-ove iz oba skupa, kao i polarity ocenama za oba.

```python
def sentiment(tokeni):
    b = TextBlob(" ".join(tokeni)).sentiment      # " ".join — TextBlob trazi TEKST
    return b.polarity, b.subjectivity
```

**Uput:** `Vežbe 2026/V3/primer.ipynb` (VADER), `Vežbe 2026/V5/V5_resenje.ipynb`.
**Teorija:** `K1_priprema.ipynb` → **Celina 6**.

**Pazi:** `TextBlob` prima **string**, ne listu tokena. Bez `" ".join()` dobijaš grešku.
`polarity` ∈ [−1, 1], `subjectivity` ∈ [0, 1].

---

### Tačka 6
> Izdvojiti i ispisati najpozitivniji tweet, najnegativniji tweet, i najsubjektivniji
> tweet iz oba skupa.

```python
df.loc[df["polarity_skup1"].idxmax()]      # najpozitivniji
df.loc[df["polarity_skup1"].idxmin()]      # najnegativniji
df.loc[df["subjectivity_skup1"].idxmax()]  # najsubjektivniji
```

**Teorija:** `K1_priprema.ipynb` → **Celina 8**, tačka 6.

**Pazi:** `idxmax()` vraća **indeks** reda, pa ide `df.loc[...]`. Traži se za **oba** skupa.

---

## Varijanta I kolokvijuma iz 2026

**Izvor:** `k1/V52026/V5 (1).ipynb`, `k1/V52025/V5.ipynb`
**Podaci:** `tweets.txt`, `sentences.txt`, `tales.txt`

1. **Preprocesiranje `tweets.txt`** — emotikoni, URL, mention, interpunkcija, mala slova,
   tokenizacija (`TweetTokenizer` vs sopstvena), uklanjanje 2 najčešća tokena
   → `K1_priprema.ipynb`, **Celine 2–4**
2. **Lematizacija sopstvenim pravilima nad `sentences.txt`** — glagolima skloniti `-ing`/`-ed`,
   oblike *to be* → `be`, pridevima `-ing`/`-y`/`-ous`, prilozima `-ly`; pa uporediti
   Porter i Lancaster reč po reč
   → `K1_priprema.ipynb`, **Celina 5**; vežbe `V2/primer (2).ipynb`, `V3/primer.ipynb`
3. **N-grami i predikcija reči nad `tales.txt`** — funkcija prima trigram, vraća sledeću reč;
   dodati **backoff**, izbor (najčešća / najređa / nasumična) i **smoothing**
   → `K1_priprema.ipynb`, **Celina 7**

---
---

# II KOLOKVIJUM

**Izvor:** `k2/K2/k2 zadatak.pdf`
**Podaci:** `text.txt` (kolekcija od 63 dela)
**Rešenje:** `K2_priprema.ipynb`, Celina 11

---

### Tačka 1
> Učitati `text.txt`. Skup podataka čini kolekcija pisanih dela. Razdvojiti svako delo i
> kreirati rečnik u formatu `Naslov: Tekst`.

```python
granice = [i for i, r in enumerate(redovi) if re.match(r"^\s*\(\d{4}\)\s*$", r)]
# naslov = poslednji neprazan red IZNAD reda sa godinom
```

**Uput:** `Vežbe 2026/V10/k2 (1) (1).ipynb`, `Vežbe 2026/V11/k2 ispravak (2).ipynb`.
**Teorija:** `K2_priprema.ipynb` → **Celina 1**.

**Pazi:** ne postoji univerzalno pravilo za deljenje. **Prvo ispiši prvih 30 redova** i
pronađi obrazac. U `text.txt` je to red oblika `(1917)`. U `tales.txt` je drugačije.

---

### Tačka 2
> Odraditi standardno procesiranje uklanjanjem stopwords i znakova interpunkcije u svakom delu.

```python
tokeni = word_tokenize(tekst.lower())
tokeni = [t for t in tokeni if t.isalpha()]        # baca interpunkciju I brojeve
tokeni = [t for t in tokeni if t not in STOP_EN]
```

**Uput:** `Vežbe 2026/V1/v1.ipynb`.
**Teorija:** `K2_priprema.ipynb` → **Celina 2**.

---

### Tačka 3
> Formirati 3 skupa podataka. Prvi je **kontrolni** skup nad kojim se radi samo standardno
> preprocesiranje. Drugi se dobija **stemming-om**, a treći koristeći **POS-tagging pa lematizaciju**.

```python
def penn_u_wordnet(tag):
    return {"J": "a", "V": "v", "R": "r"}.get(tag[0], "n")

lematizovani = [lemmatizer.lemmatize(w, penn_u_wordnet(t)) for w, t in pos_tag(tokeni)]
```

**Uput:** `Vežbe 2026/V2/primer (2).ipynb` (stemming), `Vežbe 2026/V3/primer.ipynb` (POS + lematizacija).
**Teorija:** `K2_priprema.ipynb` → **Celina 3**.

**Pazi:** `WordNetLemmatizer` podrazumevano misli da je reč **imenica**. Bez prevođenja
Penn taga u WordNet oznaku, glagoli ostaju nepromenjeni — a upravo to zadatak proverava.

---

### Tačka 4
> Izdvojiti metapodatke za svaki skup. Metapodaci su rečnik sa ključevima **Actors**,
> **Locations** i **Dates**. `Actors` su sve osobe u delu. `Locations` su sve organizacije
> i geopolitički entiteti. `Dates` su svi datumi, odnosno sva vremena dešavanja.

```python
stablo = ne_chunk(pos_tag(word_tokenize(recenica)))
for grana in stablo:
    if isinstance(grana, Tree):
        if grana.label() == "PERSON":                          -> Actors
        elif grana.label() in ("ORGANIZATION", "GPE"):         -> Locations
# Dates se hvataju REGEX-om, ne NER-om
```

**Uput:** `Vežbe 2026/V3/primer.ipynb` (POS-tagging kao osnova za NER).
**Teorija:** `K2_priprema.ipynb` → **Celina 6**.

**Dve najveće zamke:**
1. `ne_chunk` **ne prepoznaje datume** — nema `DATE` oznaku. `Dates` se mora hvatati
   regularnim izrazom.
2. NER radi **samo nad tekstom sa velikim slovima**. Ako si već prebacio u mala slova,
   neće naći nijedno ime — imena se prepoznaju baš po velikom početnom slovu.

---

### Tačka 5
> Kreirati funkciju koja vraća skupovnu razliku između dva prosleđena skupa metapodataka.
> Razliku predstavljaju po 2 kolekcije za svaki metapodatak — nalazi se u prvom a ne u
> drugom, i nalazi se u drugom a ne u prvom. Testirati koristeći 2 skupa metapodataka za
> **isto delo** i koristeći 2 skupa metapodataka iz **različitih dela** (radi kontrole).

```python
for kljuc in ("Actors", "Locations", "Dates"):
    a, b = set(meta1[kljuc]), set(meta2[kljuc])
    rez[kljuc] = {"samo_u_prvom": sorted(a - b), "samo_u_drugom": sorted(b - a)}
```

**Teorija:** `K2_priprema.ipynb` → **Celina 7 i 11**.

**Zašto se traže dva testa:** test nad **istim delom** meri koliko šuma unosi sama obrada
(stemming kvari imena pa NER prepozna manje). Test nad **različitim delima** meri stvarnu
razliku sadržaja. Prvi je kontrola, drugi je rezultat.

---

## Varijanta II kolokvijuma iz 2026

**Izvor:** `Vežbe 2026/V11/k2 ispravak (2).ipynb`
**Podaci:** `tales.txt`

1. **Dataset iz kolekcije dela** — rečnik rečnika: ključ je naslov, vrednost rečnik sa
   `text`, `bow`, `words` → `K2_priprema.ipynb`, **Celina 1 i 4**
2. **BoW i TF-IDF** po delu + top-3 reči po svakom → **Celina 4**
3. **POS/NER pitanja** — koje delo ima najviše imenica, koje najviše glagola, koji lik ima
   interakciju sa najviše drugih (ista rečenica ili do 3 rečenice razlike)
   → **Celine 5 i 8**

## Ostale teme koje se pojavljuju na završnom

| tema | vežba | celina u pripremi |
|---|---|---|
| Sažimanje teksta na više nivoa (10/60/80%), kazna za duge rečenice | `V9/text_summarization (2).ipynb` | K2 → **Celina 9** |
| MNB klasifikator nad tekstom sa weba | `V8/v10 (1).ipynb` | K2 → **Celina 10** |
| Word2Vec / gensim | `V13/gensim (2).ipynb` | (nije u pripremi) |

---
---

# Zbirna lista zamki

| # | zamka | gde se javlja |
|---|---|---|
| 1 | interpunkcija uklonjena **pre** URL-ova | K1, tačka 3 |
| 2 | `TextBlob` dobija listu tokena umesto stringa | K1, tačka 5 |
| 3 | `WordNetLemmatizer` bez `pos="v"` | K1 i K2 |
| 4 | otvaranje fajla bez `encoding="utf-8"` | svuda |
| 5 | NER pušten nad tekstom u malim slovima | K2, tačka 4 |
| 6 | očekivanje da `ne_chunk` vraća `DATE` | K2, tačka 4 |
| 7 | `idxmax()` vraća indeks — treba `df.loc[...]` | K1, tačka 6 |
| 8 | `vec.fit_transform` pozvan i nad test skupom | K2, klasifikacija |
| 9 | POS-tagging nad tekstom bez stop-reči (pokidan kontekst) | K2, tačka 3 |
| 10 | najčešći tokeni računati po dokumentu umesto po celom skupu | K1, tačka 4 |
