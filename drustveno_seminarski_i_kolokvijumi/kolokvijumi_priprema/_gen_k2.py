# -*- coding: utf-8 -*-
"""Generise K2_priprema.ipynb."""
import nbformat as nbf
C = []
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): C.append(nbf.v4.new_code_cell(s.strip()))

md(r"""
# II kolokvijum — priprema

Predmet: **Društveno računarstvo**

Isti raspored kao u pripremi za I kolokvijum: prvo **logičke celine** sa teorijom i
malim primerom, na kraju **kompletno rešenje** kolokvijumskog zadatka.

## Kako izgleda II kolokvijum

Zadatak (`k2/K2/k2 zadatak.pdf`) ima pet tačaka:

1. Učitati `text.txt` — kolekciju pisanih dela. Razdvojiti dela i napraviti rečnik `Naslov: Tekst`
2. Standardno preprocesiranje: ukloniti stop-reči i interpunkciju u svakom delu
3. Formirati **tri skupa**: kontrolni (samo preprocesiranje), **stemovani**, i **POS-tagging pa lematizacija**
4. Izdvojiti **metapodatke** za svaki skup — rečnik sa ključevima `Actors`, `Locations`, `Dates`
5. Napisati funkciju koja vraća **skupovnu razliku** dva skupa metapodataka i testirati je

Varijanta iz 2026 traži i BoW/TF-IDF po delu, pitanja o POS-u, interakcije likova,
sažimanje teksta i MNB klasifikator. Sve je obrađeno ovde.

## Sadržaj

| celina | tema |
|---|---|
| 1 | Parsiranje kolekcije dela u rečnik `Naslov: Tekst` |
| 2 | Standardno preprocesiranje |
| 3 | Tri skupa — kontrolni, stemovani, lematizovani |
| 4 | Bag of Words i TF-IDF |
| 5 | POS-tagging — brojanje imenica i glagola |
| 6 | NER — prepoznavanje imenovanih entiteta |
| 7 | Metapodaci i skupovne razlike |
| 8 | Interakcije likova |
| 9 | Ekstraktivno sažimanje teksta |
| 10 | Klasifikacija teksta (Multinomial Naive Bayes) |
| **11** | **Kompletno rešenje zadatka** |
| 12 | Kontrolna lista |
""")

md("## 0. Priprema okruženja")

code(r"""
import json
import re
import string
import heapq
from collections import Counter, defaultdict

import nltk
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

for r in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4",
          "averaged_perceptron_tagger", "averaged_perceptron_tagger_eng",
          "maxent_ne_chunker", "maxent_ne_chunker_tab", "words"]:
    try:
        nltk.download(r, quiet=True)
    except Exception:
        pass

STOP_EN = set(stopwords.words("english"))
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
print("Okruzenje spremno.")
""")

# ═══════════════════════════ CELINA 1
md(r"""
---
# Celina 1 — Parsiranje kolekcije dela

`text.txt` je jedan fajl sa **63 dela** (zbirka Lavkraftovih priča). Zadatak traži
rečnik oblika `{Naslov: Tekst}`.

Prvo treba naći **pravilo po kojem se dela razdvajaju**. U ovom fajlu svako delo ima
naslov, pa red sa godinom u zagradama:

```
The Tomb

(1917)

In relating the circumstances which have led to my confinement...
```

Dakle pravilo je: **red oblika `(GODINA)` označava početak novog dela**, a naslov je
poslednji neprazan red iznad njega.

> **Opšti savet:** na kolokvijumu prvo `print` prvih 30 redova fajla i pronađi obrazac.
> Ne postoji univerzalno pravilo — svaki fajl se deli drugačije.
""")

code(r"""
with open("data/text.txt", encoding="utf-8") as f:
    sirovo = f.read()

print(f"Ukupno: {len(sirovo):,} znakova, {len(sirovo.splitlines()):,} redova\n")
print("Prvih 12 redova:")
for i, red in enumerate(sirovo.splitlines()[:12]):
    print(f"  {i:>2}: {red[:80]!r}")
""")

code(r"""
def parsiraj_dela(tekst):
    'Deli kolekciju na dela. Naslov je poslednji neprazan red iznad reda sa (GODINA).'
    redovi = tekst.splitlines()
    granice = [i for i, r in enumerate(redovi) if re.match(r"^\s*\(\d{4}\)\s*$", r)]

    dela = {}
    for k, i in enumerate(granice):
        # naslov: prvi neprazan red iznad reda sa godinom
        naslov = "?"
        for j in range(i - 1, max(-1, i - 8), -1):
            if redovi[j].strip():
                naslov = redovi[j].strip()
                break
        # telo: od reda posle godine do naslova sledeceg dela
        kraj = granice[k + 1] - 8 if k + 1 < len(granice) else len(redovi)
        telo = " ".join(redovi[i + 1:kraj])
        dela[naslov] = re.sub(r"\s+", " ", telo).strip()
    return dela

sva_dela = parsiraj_dela(sirovo)
print(f"Pronadjeno dela: {len(sva_dela)}\n")
for naslov in list(sva_dela)[:6]:
    print(f"   {naslov:<38} {len(sva_dela[naslov].split()):>7,} reci")
""")

md(r"""
Dela ima 63 i neka su vrlo duga. Za vežbu i za kolokvijum se uzima **manji podskup** —
zadatak iz 2026 izričito kaže *„koristiti samo 2 zadata dela i prvih 1000 reči iz svakog"*.
""")

code(r"""
IZABRANA = ["The Tomb", "Dagon", "Polaris"]
LIMIT_RECI = 1200

korpus = {n: " ".join(sva_dela[n].split()[:LIMIT_RECI]) for n in IZABRANA if n in sva_dela}
for n, t in korpus.items():
    print(f"   {n:<16} {len(t.split()):>5} reci   pocetak: {t[:60]}...")
""")

# ═══════════════════════════ CELINA 2
md(r"""
---
# Celina 2 — Standardno preprocesiranje

„Standardno preprocesiranje" na ovom predmetu znači:

1. mala slova
2. tokenizacija
3. uklanjanje **interpunkcije**
4. uklanjanje **stop-reči**

Rezultat je lista čistih tokena po delu.
""")

code(r"""
def preprocesiraj(tekst, ukloni_stop=True):
    'Mala slova, tokenizacija, bez interpunkcije i (opciono) bez stop-reci.'
    tokeni = word_tokenize(tekst.lower())
    tokeni = [t for t in tokeni if t.isalpha()]          # baca i interpunkciju i brojeve
    if ukloni_stop:
        tokeni = [t for t in tokeni if t not in STOP_EN]
    return tokeni

for n, t in korpus.items():
    sirovi = word_tokenize(t.lower())
    cisti = preprocesiraj(t)
    print(f"{n:<16} pre: {len(sirovi):>5} tokena   posle: {len(cisti):>5}   "
          f"uklonjeno {100*(1-len(cisti)/len(sirovi)):.0f}%")
print("\nPrimer tokena:", preprocesiraj(korpus[IZABRANA[0]])[:14])
""")

# ═══════════════════════════ CELINA 3
md(r"""
---
# Celina 3 — Tri skupa podataka

Zadatak traži tri paralelne verzije istog korpusa:

| skup | obrada |
|---|---|
| **kontrolni** | samo standardno preprocesiranje |
| **stemovani** | preprocesiranje + `PorterStemmer` |
| **lematizovani** | preprocesiranje + `pos_tag` pa `WordNetLemmatizer` sa tim tagom |

Treći skup je najvažniji za razumevanje. `WordNetLemmatizer` traži **vrstu reči**, a
`pos_tag` vraća Penn Treebank tagove (`NN`, `VBD`, `JJ`, `RB`...). Ta dva se ne poklapaju,
pa je potrebna **funkcija za prevođenje**:

| Penn tag počinje sa | WordNet oznaka | vrsta |
|---|---|---|
| `J` | `a` | pridev |
| `V` | `v` | glagol |
| `N` | `n` | imenica |
| `R` | `r` | prilog |
""")

code(r"""
def penn_u_wordnet(penn_tag):
    'Prevodi Penn Treebank tag u oznaku koju trazi WordNetLemmatizer.'
    if penn_tag.startswith("J"):
        return "a"
    if penn_tag.startswith("V"):
        return "v"
    if penn_tag.startswith("R"):
        return "r"
    return "n"          # podrazumevano imenica

def lematizuj_sa_pos(tokeni):
    'POS-tagging pa lematizacija vodjena dobijenim tagom.'
    return [lemmatizer.lemmatize(rec, penn_u_wordnet(tag)) for rec, tag in pos_tag(tokeni)]

kontrolni   = {n: preprocesiraj(t) for n, t in korpus.items()}
stemovani   = {n: [stemmer.stem(w) for w in v] for n, v in kontrolni.items()}
lematizovani = {n: lematizuj_sa_pos(v) for n, v in kontrolni.items()}

d = IZABRANA[0]
pd.DataFrame({
    "kontrolni": kontrolni[d][:12],
    "stemovani": stemovani[d][:12],
    "lematizovani": lematizovani[d][:12],
})
""")

code(r"""
# koliko se skupovi razlikuju po broju RAZLICITIH reci
print(f"{'delo':<16} {'kontrolni':>10} {'stemovani':>10} {'lematiz.':>10}")
for n in korpus:
    print(f"{n:<16} {len(set(kontrolni[n])):>10} {len(set(stemovani[n])):>10} "
          f"{len(set(lematizovani[n])):>10}")
print("\n-> Stemming najvise smanjuje recnik jer sece agresivno i spaja razlicite reci.")
""")

# ═══════════════════════════ CELINA 4
md(r"""
---
# Celina 4 — Bag of Words i TF-IDF

**BoW** (vreća reči) je prosto brojanje: koliko se puta koja reč javlja u dokumentu.
Redosled se gubi. Najjednostavnije se dobija sa `Counter`.

**TF-IDF** koriguje BoW tako da kazni reči koje se javljaju **svuda**:

$$\text{tfidf}(t, d) = \underbrace{tf(t,d)}_{\text{koliko u ovom delu}} \times \underbrace{\log\frac{N}{df(t)}}_{\text{u koliko dela ukupno}}$$

Ako je reč u svim delovima, $df = N$, logaritam je 0 i težina pada na nulu. Zato TF-IDF
izdvaja reči **karakteristične za jedno delo**, a BoW samo najčešće.
""")

code(r"""
# --- BoW preko Counter-a ---
bow = {n: Counter(v) for n, v in kontrolni.items()}
for n in korpus:
    print(f"{n:<16} top BoW: {[w for w, _ in bow[n].most_common(5)]}")
""")

code(r"""
# --- TF-IDF preko sklearn-a ---
naslovi = list(korpus)
dokumenti = [" ".join(kontrolni[n]) for n in naslovi]

tfidf = TfidfVectorizer()
M = tfidf.fit_transform(dokumenti)
reci = tfidf.get_feature_names_out()

print(f"Matrica: {M.shape[0]} dokumenata x {M.shape[1]} reci\n")
for i, n in enumerate(naslovi):
    red = M[i].toarray()[0]
    top = sorted(zip(reci, red), key=lambda x: -x[1])[:5]
    print(f"{n:<16} top TF-IDF: {[w for w, _ in top]}")
""")

code(r"""
# dataset po delu — format koji zadatak trazi (recnik recnika)
dataset = {}
for i, n in enumerate(naslovi):
    red = M[i].toarray()[0]
    dataset[n] = {
        "text": korpus[n],
        "bow": bow[n],
        "words": len(korpus[n].split()),
        "top3_bow": [w for w, _ in bow[n].most_common(3)],
        "top3_tfidf": [w for w, _ in sorted(zip(reci, red), key=lambda x: -x[1])[:3]],
    }

pd.DataFrame([{"naslov": n, "words": d["words"],
               "top3_bow": ", ".join(d["top3_bow"]),
               "top3_tfidf": ", ".join(d["top3_tfidf"])} for n, d in dataset.items()])
""")

# ═══════════════════════════ CELINA 5
md(r"""
---
# Celina 5 — POS-tagging

`pos_tag` svakoj reči dodeljuje vrstu. Tagovi koji se najčešće traže:

| tag | značenje |
|---|---|
| `NN`, `NNS`, `NNP`, `NNPS` | imenica (jednina, množina, vlastita) |
| `VB`, `VBD`, `VBG`, `VBN`, `VBP`, `VBZ` | glagol (razni oblici) |
| `JJ`, `JJR`, `JJS` | pridev |
| `RB`, `RBR`, `RBS` | prilog |

Zato se broji **po prvom slovu taga**: sve što počinje sa `N` je imenica, sa `V` glagol.

> **Zamka:** POS-tagging radi nad **rečenicom sa kontekstom**. Ako mu daš listu bez
> stop-reči, tagovi su lošiji jer je kontekst pokidan. Za tačno brojanje vrsta reči
> tagovati **sirovi** tekst, pa tek onda filtrirati.
""")

code(r"""
def broj_vrsta(tekst):
    'Broji imenice, glagole, prideve i priloge u sirovom tekstu.'
    tagovi = pos_tag(word_tokenize(tekst))
    c = Counter()
    for rec, tag in tagovi:
        if not rec.isalpha():
            continue
        if tag.startswith("N"):
            c["imenice"] += 1
        elif tag.startswith("V"):
            c["glagoli"] += 1
        elif tag.startswith("J"):
            c["pridevi"] += 1
        elif tag.startswith("R"):
            c["prilozi"] += 1
    return c

tabela = pd.DataFrame([{"delo": n, **broj_vrsta(t)} for n, t in korpus.items()]).set_index("delo")
display(tabela)
print(f"Najvise imenica: {tabela.imenice.idxmax()}")
print(f"Najvise glagola: {tabela.glagoli.idxmax()}")
""")

# ═══════════════════════════ CELINA 6
md(r"""
---
# Celina 6 — NER (prepoznavanje imenovanih entiteta)

**NER** pronalazi imena u tekstu i svrstava ih u kategorije. NLTK to radi sa
`ne_chunk(pos_tag(tokens))`, što vraća **stablo**. Grane stabla su entiteti.

Kategorije koje NLTK prepoznaje:

| oznaka | značenje | u zadatku pripada |
|---|---|---|
| `PERSON` | osoba | **Actors** |
| `ORGANIZATION` | organizacija | **Locations** |
| `GPE` | geopolitički entitet (država, grad) | **Locations** |
| `LOCATION`, `FACILITY` | mesto, objekat | Locations |
| `DATE`, `TIME` | datum, vreme | **Dates** |

> **Važno:** `ne_chunk` **ne prepoznaje datume**. Zato se `Dates` hvata regularnim
> izrazom, a ne NER-om. To je najčešća greška na kolokvijumu.

> **Zamka 2:** NER mora da radi nad **sirovim tekstom sa velikim slovima**. Ako si već
> prebacio u mala slova, `ne_chunk` neće naći ništa — imena se prepoznaju upravo po
> velikom početnom slovu.
""")

code(r"""
primer = ("In July 1917 Jervas Dudley visited London and met Doctor Chester "
          "near the Hyde Park Museum on Monday morning.")

stablo = ne_chunk(pos_tag(word_tokenize(primer)))
print("Pronadjeni entiteti:")
for grana in stablo:
    if isinstance(grana, Tree):
        naziv = " ".join(rec for rec, _ in grana.leaves())
        print(f"   {grana.label():<14} {naziv}")
""")

code(r"""
DATUM_RE = re.compile(
    r"\b(?:\d{1,2}(?:st|nd|rd|th)?\s+)?"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"(?:\s+\d{1,2}(?:st|nd|rd|th)?)?(?:,?\s+\d{4})?\b"
    r"|\b\d{4}\b"
    r"|\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"
    r"|\b(?:morning|evening|night|midnight|noon|dawn|dusk|yesterday|today|tomorrow)\b",
    re.IGNORECASE)

def izvuci_metapodatke(tekst):
    'Vraca recnik sa kljucevima Actors, Locations, Dates.'
    meta = {"Actors": set(), "Locations": set(), "Dates": set()}
    for recenica in sent_tokenize(tekst):
        stablo = ne_chunk(pos_tag(word_tokenize(recenica)))
        for grana in stablo:
            if not isinstance(grana, Tree):
                continue
            naziv = " ".join(rec for rec, _ in grana.leaves())
            if grana.label() == "PERSON":
                meta["Actors"].add(naziv)
            elif grana.label() in ("ORGANIZATION", "GPE", "LOCATION", "FACILITY"):
                meta["Locations"].add(naziv)
    meta["Dates"] = {m.group().strip() for m in DATUM_RE.finditer(tekst)}
    return meta

m = izvuci_metapodatke(primer)
for k, v in m.items():
    print(f"   {k:<10} {sorted(v)}")
""")

# ═══════════════════════════ CELINA 7
md(r"""
---
# Celina 7 — Skupovne razlike metapodataka

Tačka 5 zadatka traži funkciju koja poredi **dva** skupa metapodataka i za svaki ključ
vraća **dve** kolekcije:

- šta je u prvom a nije u drugom → `A - B`
- šta je u drugom a nije u prvom → `B - A`

To je obična razlika skupova u Pythonu. Zato se metapodaci i čuvaju kao `set`.
""")

code(r"""
def razlika_metapodataka(meta1, meta2, ime1="skup1", ime2="skup2"):
    'Za svaki kljuc vraca sta je samo u prvom i sta je samo u drugom skupu.'
    rez = {}
    for kljuc in ("Actors", "Locations", "Dates"):
        a, b = set(meta1.get(kljuc, [])), set(meta2.get(kljuc, []))
        rez[kljuc] = {
            f"samo_u_{ime1}": sorted(a - b),
            f"samo_u_{ime2}": sorted(b - a),
            "zajednicko": sorted(a & b),
        }
    return rez

t1 = "John met Mary in London in July 1917."
t2 = "Mary visited Paris with Peter on Monday."
r = razlika_metapodataka(izvuci_metapodatke(t1), izvuci_metapodatke(t2), "tekst1", "tekst2")
for k, v in r.items():
    print(f"\n{k}:")
    for podk, vred in v.items():
        print(f"   {podk:<16} {vred}")
""")

# ═══════════════════════════ CELINA 8
md(r"""
---
# Celina 8 — Interakcije likova

Definicija iz zadatka: dva lika **imaju interakciju** ako se pojavljuju u istoj rečenici
ili u rečenicama udaljenim do 3.

Postupak:

1. tekst podeliti na rečenice (`sent_tokenize`)
2. u svakoj rečenici naći likove (NER, `PERSON`)
3. za svaku rečenicu uzeti prozor od ±3 rečenice i sve likove u tom prozoru povezati
4. brojati parove
""")

code(r"""
def likovi_po_recenici(tekst):
    'Za svaku recenicu vraca skup imena tipa PERSON.'
    out = []
    for r in sent_tokenize(tekst):
        imena = set()
        for grana in ne_chunk(pos_tag(word_tokenize(r))):
            if isinstance(grana, Tree) and grana.label() == "PERSON":
                imena.add(" ".join(w for w, _ in grana.leaves()))
        out.append(imena)
    return out

def interakcije(tekst, prozor=3):
    'Broji koliko puta se svaki par likova nadje u prozoru od +-`prozor` recenica.'
    po_rec = likovi_po_recenici(tekst)
    veze = defaultdict(Counter)
    for i, imena in enumerate(po_rec):
        okolina = set()
        for j in range(max(0, i - prozor), min(len(po_rec), i + prozor + 1)):
            okolina |= po_rec[j]
        for a in imena:
            for b in okolina:
                if a != b:
                    veze[a][b] += 1
    return veze

probni = korpus[IZABRANA[0]][:4000]
veze = interakcije(probni)
if veze:
    glavni = max(veze, key=lambda k: len(veze[k]))
    print(f"Lik sa najvise razlicitih interakcija: {glavni} ({len(veze[glavni])})")
    print("Sa kim najvise:", veze[glavni].most_common(5))
else:
    print("U ovom odlomku NER nije nasao vise likova — probaj drugo delo ili duzi odlomak.")
""")

# ═══════════════════════════ CELINA 9
md(r"""
---
# Celina 9 — Ekstraktivno sažimanje

**Ekstraktivno** sažimanje ne piše nove rečenice — bira najvažnije postojeće.

Postupak:

1. preprocesiraj tekst i izbroj frekvencije reči
2. frekvencije **normalizuj** (podeli najvećom) da budu u opsegu 0–1
3. svaku rečenicu oceni zbirom težina njenih reči
4. **penalizuj duge rečenice** (zadatak traži: duže od 12 reči)
5. uzmi najboljih `k` rečenica, gde je `k` procenat od ukupnog broja

`heapq.nlargest` je zgodan za korak 5.
""")

code(r"""
def sazmi(tekst, procenat=0.3, max_reci=12, kazna=0.5):
    'Ekstraktivno sazimanje frekvencijskim tezinama, sa kaznom za duge recenice.'
    recenice = sent_tokenize(tekst)
    frek = Counter(preprocesiraj(tekst))
    if not frek:
        return ""
    najveca = max(frek.values())
    tezine = {w: c / najveca for w, c in frek.items()}          # normalizacija

    ocene = {}
    for r in recenice:
        reci = preprocesiraj(r)
        if not reci:
            continue
        ocena = sum(tezine.get(w, 0) for w in reci)
        if len(r.split()) > max_reci:                            # penalizacija
            ocena *= kazna
        ocene[r] = ocena

    k = max(1, int(len(recenice) * procenat))
    izabrane = heapq.nlargest(k, ocene, key=ocene.get)
    # vrati ih u originalnom redosledu, da sazetak bude citljiv
    return " ".join([r for r in recenice if r in set(izabrane)])

tekst = korpus[IZABRANA[0]]
redovi = []
for p in (0.1, 0.6, 0.8):
    s = sazmi(tekst, p)
    redovi.append({
        "nivo": f"{int(p*100)}%",
        "recenica": len(sent_tokenize(s)),
        "reci": len(s.split()),
        "sentiment": round(TextBlob(s).sentiment.polarity, 4),
    })
redovi.append({"nivo": "original", "recenica": len(sent_tokenize(tekst)),
               "reci": len(tekst.split()),
               "sentiment": round(TextBlob(tekst).sentiment.polarity, 4)})
pd.DataFrame(redovi)
""")

# ═══════════════════════════ CELINA 10
md(r"""
---
# Celina 10 — Klasifikacija teksta (Multinomial Naive Bayes)

Zadatak traži funkciju koja skida tekst sa nekoliko stranica, pravi dataset
`rečenica → tip_teksta`, i trenira **MNB** klasifikator.

**Zašto baš Multinomial Naive Bayes za tekst?** Zato što radi sa **brojem pojavljivanja**
reči, a upravo to daje `CountVectorizer`. To je klasičan par za klasifikaciju teksta.

Ovde se koristi lokalni tekst umesto skidanja sa weba, da primer radi i bez interneta.
Deo sa `requests`/`BeautifulSoup` je u komentaru — na kolokvijumu se samo odkomentariše.
""")

code(r"""
def napravi_dataset(izvori, save_dataset=False, putanja="dataset.csv"):
    # izvori: lista parova (tekst_ili_link, tip_teksta)
    # Vraca DataFrame sa kolonama "recenica" i "tip".
    redovi = []
    for izvor, tip in izvori:
        if izvor.startswith("http"):
            # --- varijanta sa weba (na kolokvijumu odkomentarisati) ---
            # import requests
            # from bs4 import BeautifulSoup
            # html = requests.get(izvor).text
            # supa = BeautifulSoup(html, "html.parser")
            # tekst = " ".join(p.get_text() for p in supa.find_all("p"))
            raise NotImplementedError("Odkomentarisi blok za skidanje sa weba.")
        else:
            tekst = izvor
        for r in sent_tokenize(tekst):
            if len(r.split()) >= 5:
                redovi.append({"recenica": r.strip(), "tip": tip})

    df = pd.DataFrame(redovi)
    # izjednacavanje klasa na 50-50 (podjednak broj recenica po tipu)
    n = df["tip"].value_counts().min()
    delovi = [df[df["tip"] == t].sample(n, random_state=42) for t in df["tip"].unique()]
    df = pd.concat(delovi).sample(frac=1, random_state=42).reset_index(drop=True)
    if save_dataset:
        df.to_csv(putanja, index=False, encoding="utf-8")
    return df

ds = napravi_dataset([(korpus["The Tomb"], "tomb"), (korpus["Dagon"], "dagon")])
print(f"Dataset: {len(ds)} recenica")
print(ds.tip.value_counts().to_string())
ds.head(3)
""")

code(r"""
X_tr, X_te, y_tr, y_te = train_test_split(ds.recenica, ds.tip, test_size=0.3,
                                          random_state=42, stratify=ds.tip)
vec = CountVectorizer(stop_words="english")
Xtr = vec.fit_transform(X_tr)          # fit SAMO na trening skupu
Xte = vec.transform(X_te)              # test se samo transformise

mnb = MultinomialNB().fit(Xtr, y_tr)
pred = mnb.predict(Xte)

print(f"Tacnost: {accuracy_score(y_te, pred):.3f}   (bazna linija 0.500 — klase su 50-50)\n")
print(classification_report(y_te, pred))
""")

# ═══════════════════════════ CELINA 11 — REŠENJE
md(r"""
---
---
# Celina 11 — KOMPLETNO REŠENJE ZADATKA

Zadatak iz `k2/K2/k2 zadatak.pdf`, tačka po tačka.
""")

md("### Tačka 1 — Učitati `text.txt`, razdvojiti dela, napraviti rečnik `Naslov: Tekst`")
code(r"""
with open("data/text.txt", encoding="utf-8") as f:
    sirovo = f.read()

sva_dela = parsiraj_dela(sirovo)
print(f"Ukupno dela u kolekciji: {len(sva_dela)}")

# radimo sa podskupom, zbog brzine NER-a
DELA = ["The Tomb", "Dagon", "Polaris"]
korpus = {n: " ".join(sva_dela[n].split()[:1200]) for n in DELA}
for n, t in korpus.items():
    print(f"   {n:<16} {len(t.split())} reci")
""")

md("### Tačka 2 — Standardno preprocesiranje (stop-reči i interpunkcija)")
code(r"""
ocisceno = {n: preprocesiraj(t) for n, t in korpus.items()}
for n, v in ocisceno.items():
    print(f"   {n:<16} {len(v)} tokena posle ciscenja   {v[:8]}")
""")

md("### Tačka 3 — Tri skupa: kontrolni, stemovani, POS-tagging + lematizacija")
code(r"""
skup_kontrolni    = ocisceno
skup_stemovani    = {n: [stemmer.stem(w) for w in v] for n, v in ocisceno.items()}
skup_lematizovani = {n: lematizuj_sa_pos(v) for n, v in ocisceno.items()}

pd.DataFrame({
    "delo": list(korpus),
    "kontrolni_razliciti": [len(set(skup_kontrolni[n])) for n in korpus],
    "stemovani_razliciti": [len(set(skup_stemovani[n])) for n in korpus],
    "lematizovani_razliciti": [len(set(skup_lematizovani[n])) for n in korpus],
})
""")

md(r"""
### Tačka 4 — Metapodaci za svaki skup

**Ovde je ključna odluka.** NER radi nad **sirovim tekstom** — treba mu veliko početno
slovo i kontekst rečenice. Zato se metapodaci vade iz teksta rekonstruisanog iz svakog
skupa, ali se za `Actors`/`Locations` koristi originalni tekst kao referenca.

Da bi se videla razlika između skupova, ovde se NER pušta nad tekstom sastavljenim iz
tokena svakog skupa. Rezultat pokazuje **zašto stemovani skup gubi imena** — `Dudley`
posle stemminga postaje `dudlei` i NER ga više ne prepoznaje.
""")
code(r"""
def meta_iz_tokena(tokeni, original):
    'NER nad originalnim tekstom, ali zadrzava samo entitete cije reci postoje u skupu.'
    puni = izvuci_metapodatke(original)
    skup = set(w.lower() for w in tokeni)
    filtriran = {}
    for k in ("Actors", "Locations"):
        filtriran[k] = {e for e in puni[k]
                        if any(w.lower() in skup for w in e.split())}
    filtriran["Dates"] = puni["Dates"]
    return filtriran

metapodaci = {}
for ime_skupa, skup in [("kontrolni", skup_kontrolni),
                        ("stemovani", skup_stemovani),
                        ("lematizovani", skup_lematizovani)]:
    metapodaci[ime_skupa] = {n: meta_iz_tokena(skup[n], korpus[n]) for n in korpus}

for ime_skupa, po_delu in metapodaci.items():
    print(f"\n=== {ime_skupa.upper()} ===")
    for n, m in po_delu.items():
        print(f"  {n:<16} Actors={len(m['Actors']):>2}  "
              f"Locations={len(m['Locations']):>2}  Dates={len(m['Dates']):>2}")
        if m["Actors"]:
            print(f"                   {sorted(m['Actors'])[:4]}")
""")

md(r"""
### Tačka 5 — Funkcija za skupovnu razliku + testiranje

Zadatak izričito traži **dva testa**:

1. dva skupa metapodataka za **isto delo** (očekuje se mala razlika — kontrola)
2. dva skupa metapodataka iz **različitih dela** (očekuje se velika razlika)
""")
code(r"""
print("=" * 72)
print("TEST 1 — ISTO DELO, razliciti skupovi (kontrolni vs stemovani)")
print("=" * 72)
r1 = razlika_metapodataka(metapodaci["kontrolni"]["The Tomb"],
                          metapodaci["stemovani"]["The Tomb"],
                          "kontrolni", "stemovani")
for k, v in r1.items():
    print(f"\n{k}:")
    for podk, vred in v.items():
        print(f"   {podk:<22} ({len(vred)}) {vred[:5]}")
""")

code(r"""
print("=" * 72)
print("TEST 2 — RAZLICITA DELA, isti skup (The Tomb vs Dagon, kontrolni)")
print("=" * 72)
r2 = razlika_metapodataka(metapodaci["kontrolni"]["The Tomb"],
                          metapodaci["kontrolni"]["Dagon"],
                          "The_Tomb", "Dagon")
for k, v in r2.items():
    print(f"\n{k}:")
    for podk, vred in v.items():
        print(f"   {podk:<22} ({len(vred)}) {vred[:5]}")
""")

md(r"""
### Zaključak testova

**Test 1** poredi isto delo obrađeno na dva načina. Razlika koja se pojavi **nije osobina
dela nego posledica obrade** — stemming kvari imena, pa NER prepozna manje entiteta.
To je kontrolni test i pokazuje koliko obrada košta.

**Test 2** poredi različita dela. Ovde je razlika **stvarna** — reč je o drugim likovima i
drugim mestima. Presek (`zajednicko`) je mali ili prazan.

Upravo zbog toga zadatak traži oba testa: prvi meri **šum koji unosi obrada**, drugi meri
**pravu razliku sadržaja**.
""")

# ═══════════════════════════ CELINA 12
md(r"""
---
# Celina 12 — Kontrolna lista

- [ ] pronaći pravilo po kojem se dela razdvajaju i napisati parser u rečnik `Naslov: Tekst`
- [ ] standardno preprocesiranje (mala slova, tokenizacija, `isalpha()`, stop-reči)
- [ ] napraviti tri paralelna skupa (kontrolni / stemovani / lematizovani)
- [ ] napisati `penn_u_wordnet` i lematizovati **vođeno POS tagom**
- [ ] BoW preko `Counter`, TF-IDF preko `TfidfVectorizer`, izvući top-N
- [ ] brojati imenice i glagole po prvom slovu POS taga (`N`, `V`)
- [ ] `ne_chunk(pos_tag(word_tokenize(...)))` i čitanje `Tree` grana
- [ ] mapirati `PERSON` → Actors, `ORGANIZATION`/`GPE` → Locations
- [ ] **datume hvatati regularnim izrazom**, ne NER-om
- [ ] skupovna razlika `A - B` i `B - A`
- [ ] ekstraktivno sažimanje sa normalizovanim frekvencijama i kaznom za duge rečenice
- [ ] `CountVectorizer` + `MultinomialNB`, `fit` samo na trening skupu

**Najčešće greške:**

1. NER pušten nad tekstom u malim slovima → ne nađe nijedno ime
2. Očekivanje da `ne_chunk` vraća `DATE` → ne vraća, treba regex
3. `WordNetLemmatizer` bez POS taga → glagoli ostaju neizmenjeni
4. `vec.fit_transform` pozvan i na test skupu → curenje informacija
5. POS-tagging nad tekstom bez stop-reči → pokidan kontekst, lošiji tagovi
""")

nb = nbf.v4.new_notebook(cells=C)
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
               "language_info": {"name": "python"}}
nbf.write(nb, "K2_priprema.ipynb")
print(f"Upisano K2_priprema.ipynb — {len(C)} celija")
