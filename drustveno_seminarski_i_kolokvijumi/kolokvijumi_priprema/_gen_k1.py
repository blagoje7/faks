# -*- coding: utf-8 -*-
"""Generise K1_priprema.ipynb."""
import nbformat as nbf
C = []
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(s): C.append(nbf.v4.new_code_cell(s.strip()))

md(r"""
# I kolokvijum — priprema

Predmet: **Društveno računarstvo**

Ovaj notebook je podeljen na **logičke celine**. Svaka celina ima kratku teoriju, zatim
kod koji tu teoriju pokazuje na malom primeru. Na kraju je **kompletno rešenje**
kolokvijumskog zadatka, sastavljeno od tih istih delova.

## Kako izgleda I kolokvijum

Zadatak sa roka (`k1/K1/okto1.pdf`) ima šest tačaka:

1. Učitati `tweets.json`, izdvojiti tekst prvih 20 tweet-ova
2. Tokenizovati pomoću `TweetTokenizer` → **skup1**
3. Napisati **sopstvenu** funkciju za tokenizaciju (razmak, bez interpunkcije, bez URL-ova) → **skup2**
4. Iz oba skupa ukloniti 2 najčešća tokena
5. `TextBlob` analiza sentimenta za oba skupa, uporediti, napraviti `DataFrame`
6. Izdvojiti najpozitivniji, najnegativniji i najsubjektivniji tweet iz oba skupa

Varijanta iz 2026 (`k1/V52026`) traži isto gradivo drugačije upakovano: preprocesiranje
`tweets.txt`, sopstvena pravila lematizacije nad `sentences.txt`, i n-grami sa
predikcijom sledeće reči nad `tales.txt`. Zato su ovde obrađene **obe** varijante.

## Sadržaj

| celina | tema |
|---|---|
| 1 | Učitavanje podataka (JSON i TXT) |
| 2 | Čišćenje teksta — URL, mention, hashtag, emotikoni, interpunkcija |
| 3 | Tokenizacija — gotovi tokenizatori i sopstvena funkcija |
| 4 | Stop-reči i frekvencije — `Counter` |
| 5 | Normalizacija — stemming i lematizacija |
| 6 | Analiza sentimenta — `TextBlob` i VADER |
| 7 | N-grami i predikcija sledeće reči |
| **8** | **Kompletno rešenje zadatka** |
| 9 | Kontrolna lista za izlazak na kolokvijum |
""")

md("## 0. Priprema okruženja\n\nSve što se koristi u nastavku uvozi se ovde.")

code(r"""
import json
import re
import string
import random
from collections import Counter, defaultdict

import nltk
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize, TweetTokenizer, WordPunctTokenizer, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, LancasterStemmer, SnowballStemmer, WordNetLemmatizer
from nltk.util import ngrams
from textblob import TextBlob

# NLTK resursi — pokrenuti jednom; ako su vec skinuti, prolazi trenutno
for r in ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4",
          "averaged_perceptron_tagger", "averaged_perceptron_tagger_eng", "vader_lexicon"]:
    try:
        nltk.download(r, quiet=True)
    except Exception:
        pass

STOP_EN = set(stopwords.words("english"))
print(f"Stop-reci (engleski): {len(STOP_EN)}  |  primer: {sorted(STOP_EN)[:8]}")
""")

# ═══════════════════════════ CELINA 1
md(r"""
---
# Celina 1 — Učitavanje podataka

Na kolokvijumu se pojavljuju dva oblika ulaza.

**JSON** — `tweets.json` je lista rečnika u punom Twitter formatu. Svaki tweet ima
mnogo polja, a nama treba samo `text`.

**Običan tekst** — `tweets.txt`, `tales.txt`, `sentences.txt` su obični fajlovi,
jedan zapis po redu ili slobodan tekst.

> **Zamka:** uvek otvarati sa `encoding="utf-8"`. Bez toga se na Windowsu javlja
> `UnicodeDecodeError` čim naiđe emotikon ili slovo van ASCII.
""")

code(r"""
# --- JSON ---
with open("data/tweets.json", encoding="utf-8") as f:
    tweets_json = json.load(f)

print(f"Ucitano tweet-ova: {len(tweets_json)}")
print(f"Polja u jednom tweet-u: {len(tweets_json[0])}")

# zadatak trazi tekst prvih 20
tweets = [t["text"] for t in tweets_json[:20]]
print(f"\nIzdvojeno: {len(tweets)} tekstova")
print("Prvi:", tweets[0][:110])
""")

code(r"""
# --- obican tekst ---
with open("data/tweets.txt", encoding="utf-8") as f:
    tweets_txt = [red.strip() for red in f if red.strip()]

with open("data/tales.txt", encoding="utf-8") as f:
    tales = f.read()

print(f"tweets.txt: {len(tweets_txt)} redova")
print(f"tales.txt:  {len(tales.split())} reci")
print("\nPrimer iz tweets.txt:", tweets_txt[0])
""")

# ═══════════════════════════ CELINA 2
md(r"""
---
# Celina 2 — Čišćenje teksta

Pre tokenizacije se iz teksta uklanja ono što nije reč. Svaki element se hvata
regularnim izrazom.

| element | regularni izraz | objašnjenje |
|---|---|---|
| URL | `https?://\S+` | `http` ili `https`, pa sve do prvog razmaka |
| mention | `@\w+` | znak `@` praćen slovima/ciframa |
| hashtag | `#\w+` | isto, sa `#` |
| emotikoni | opseg Unicode znakova | emotikoni su van osnovnog ASCII opsega |
| interpunkcija | `string.punctuation` | `!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~` |

**Redosled je bitan.** Ako prvo ukloniš interpunkciju, `https://t.co/abc` postaje
`httpstcoabc` i više ga ne prepoznaješ kao URL. Zato: **prvo URL i mention, pa tek onda
interpunkcija.**
""")

code(r"""
URL_RE     = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#\w+")
EMOJI_RE   = re.compile(
    "[" "\U0001F300-\U0001FAFF"   # simboli, emotikoni, predmeti
        "\U00002600-\U000027BF"   # razni simboli
        "\U0001F1E6-\U0001F1FF"   # zastave
        "\U00002190-\U000021FF"   # strelice
        "\U0000FE00-\U0000FE0F"   # modifikatori prikaza
    "]+", flags=re.UNICODE)

def ocisti(tekst, ukloni_hashtag=True, mala_slova=True):
    'Uklanja URL-ove, mentione, (opciono) hashtagove, emotikone i interpunkciju.'
    t = URL_RE.sub(" ", tekst)          # 1. URL prvi — pre interpunkcije
    t = MENTION_RE.sub(" ", t)          # 2. mention
    if ukloni_hashtag:
        t = HASHTAG_RE.sub(" ", t)      # 3. hashtag
    t = EMOJI_RE.sub(" ", t)            # 4. emotikoni
    t = t.translate(str.maketrans("", "", string.punctuation))   # 5. interpunkcija
    if mala_slova:
        t = t.lower()
    return re.sub(r"\s+", " ", t).strip()                        # 6. visak razmaka

primer = tweets[0]
print("PRE :", repr(primer))
print("POSLE:", repr(ocisti(primer)))
""")

code(r"""
# demonstracija zasto je redosled bitan
lose = primer.translate(str.maketrans("", "", string.punctuation))   # prvo interpunkcija
lose = URL_RE.sub(" ", lose)                                          # pa URL — kasno!
print("POGRESAN redosled:", repr(re.sub(r'\s+', ' ', lose).strip()))
print("\n-> URL je ostao kao 'httpstcoYZTAKLlcU4' jer su '://' i '.' obrisani pre njega.")
""")

# ═══════════════════════════ CELINA 3
md(r"""
---
# Celina 3 — Tokenizacija

**Tokenizacija** je deljenje teksta na jedinice (tokene). NLTK nudi više tokenizatora
i oni daju **različite** rezultate na istom ulazu.

| tokenizator | ponašanje |
|---|---|
| `word_tokenize` | opšti; `don't` → `do` + `n't`; interpunkcija je zaseban token |
| `TweetTokenizer` | čuva `@mention`, `#hashtag` i emotikone kao **jedan** token |
| `WordPunctTokenizer` | deli na slova i ne-slova; `don't` → `don` + `'` + `t` |
| `RegexpTokenizer(r"\w+")` | uzima samo nizove slova/cifara, interpunkcija nestaje |

`TweetTokenizer` ima i korisne parametre: `preserve_case=False` (mala slova),
`strip_handles=True` (baca mentione), `reduce_len=True` (`gooooood` → `goood`).
""")

code(r"""
recenica = "Don't @NBA!! Check https://t.co/abc #SackSarver 😀 gooooood"

print("word_tokenize      :", word_tokenize(recenica))
print("TweetTokenizer     :", TweetTokenizer().tokenize(recenica))
print("WordPunctTokenizer :", WordPunctTokenizer().tokenize(recenica))
print("RegexpTokenizer    :", RegexpTokenizer(r"\w+").tokenize(recenica))
print("\nTweetTokenizer sa parametrima:",
      TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True).tokenize(recenica))
""")

md(r"""
### Sopstvena funkcija za tokenizaciju

Zadatak izričito traži funkciju koja **razdvaja po razmaku**, uklanja interpunkciju i
URL-ove. To je tačka 3 kolokvijuma — piše se ručno, ne koristi se NLTK.
""")

code(r"""
def moja_tokenizacija(tekst):
    'Razdvaja po razmaku, uklanja URL-ove i znakove interpunkcije.'
    tekst = URL_RE.sub(" ", tekst)                 # URL pre interpunkcije
    tokeni = []
    for rec in tekst.split():                      # deljenje po razmaku
        rec = rec.strip(string.punctuation)        # interpunkcija sa krajeva
        rec = rec.translate(str.maketrans("", "", string.punctuation))
        if rec:
            tokeni.append(rec.lower())
    return tokeni

print("Ulaz :", repr(primer[:80]))
print("Izlaz:", moja_tokenizacija(primer))
""")

# ═══════════════════════════ CELINA 4
md(r"""
---
# Celina 4 — Stop-reči i frekvencije

**Stop-reči** su česte reči bez sadržaja (`the`, `is`, `at`). Uklanjaju se jer zauzimaju
vrh svake frekvencijske liste, a ništa ne govore o temi.

**`Counter`** je osnovni alat za frekvencije. `most_common(n)` vraća `n` najčešćih kao
listu parova `(token, broj)`.

Zadatak traži **uklanjanje 2 najčešća tokena** — to je ista ideja kao stop-reči, samo
što se lista ne uzima gotova nego se računa iz samog skupa.
""")

code(r"""
svi_tokeni = [t for tw in tweets for t in TweetTokenizer().tokenize(tw.lower())]
brojac = Counter(svi_tokeni)

print("10 najcescih tokena:")
for tok, n in brojac.most_common(10):
    print(f"   {tok!r:<18} {n}")

print("\nBez stop-reci i interpunkcije:")
filtrirani = [t for t in svi_tokeni if t not in STOP_EN and t not in string.punctuation]
for tok, n in Counter(filtrirani).most_common(10):
    print(f"   {tok!r:<18} {n}")
""")

code(r"""
def ukloni_najcesce(skup_tokenizovanih, koliko=2):
    'Iz kolekcije tokenizovanih dokumenata uklanja koliko globalno najcescih tokena.'
    ukupno = Counter(t for dok in skup_tokenizovanih for t in dok)
    za_izbacivanje = {t for t, _ in ukupno.most_common(koliko)}
    ocisceno = [[t for t in dok if t not in za_izbacivanje] for dok in skup_tokenizovanih]
    return ocisceno, za_izbacivanje

probni = [TweetTokenizer().tokenize(t.lower()) for t in tweets]
bez2, izbaceni = ukloni_najcesce(probni, 2)
print("Izbacena 2 najcesca tokena:", izbaceni)
print("Pre :", probni[0][:12])
print("Posle:", bez2[0][:12])
""")

# ═══════════════════════════ CELINA 5
md(r"""
---
# Celina 5 — Normalizacija: stemming i lematizacija

Cilj je svesti različite oblike iste reči na zajednički oblik.

**Stemming** seče sufikse po pravilima. Brz je, ali rezultat **ne mora biti prava reč**.

| stemmer | agresivnost | `studies` | `happily` |
|---|---|---|---|
| `PorterStemmer` | umeren, najčešći | `studi` | `happili` |
| `LancasterStemmer` | vrlo agresivan | `study` | `happy` |
| `SnowballStemmer` | poboljšani Porter, više jezika | `studi` | `happili` |

**Lematizacija** vraća pravu rečničku osnovu (**lemu**) koristeći rečnik WordNet.

> **Najvažnija zamka na kolokvijumu:** `WordNetLemmatizer` podrazumevano pretpostavlja da
> je reč **imenica**. Zato `running` ostaje `running`. Da bi radio nad glagolima, mora
> `lemmatize(rec, pos="v")`.
""")

code(r"""
reci = ["studies", "studying", "happily", "running", "better", "was", "children", "feet"]

porter, lanc, snow = PorterStemmer(), LancasterStemmer(), SnowballStemmer("english")
lem = WordNetLemmatizer()

df_norm = pd.DataFrame({
    "rec": reci,
    "porter": [porter.stem(r) for r in reci],
    "lancaster": [lanc.stem(r) for r in reci],
    "snowball": [snow.stem(r) for r in reci],
    "lemma (imenica)": [lem.lemmatize(r) for r in reci],
    "lemma (glagol)": [lem.lemmatize(r, pos="v") for r in reci],
})
df_norm
""")

code(r"""
# poredjenje rec-po-rec i izdvajanje onih koje se razlikuju (trazi se u varijanti 2026)
razlike = [(r, porter.stem(r), lanc.stem(r)) for r in reci if porter.stem(r) != lanc.stem(r)]
print("Reci gde se Porter i Lancaster razlikuju:")
for r, p, l in razlike:
    print(f"   {r:<12} porter={p:<10} lancaster={l}")
""")

md(r"""
### Lematizacija sopstvenim pravilima

Varijanta iz 2026 traži da se lematizacija napiše **ručno**, po zadatim pravilima:
glagolima ukloniti `-ing` i `-ed`, oblike glagola *to be* svesti na `be`,
pridevima ukloniti `-ing`, `-y`, `-ous`, prilozima `-ly`.
""")

code(r"""
TO_BE = {"is", "am", "are", "was", "were", "been", "being", "be"}

def moja_lematizacija(rec, vrsta="v"):
    # vrsta: v = glagol, a = pridev, r = prilog
    r = rec.lower()
    if r in TO_BE:
        return "be"
    if vrsta == "v":
        for suf in ("ing", "ed"):
            if r.endswith(suf) and len(r) - len(suf) >= 3:
                return r[: -len(suf)]
    elif vrsta == "a":
        for suf in ("ing", "ous", "y"):
            if r.endswith(suf) and len(r) - len(suf) >= 3:
                return r[: -len(suf)]
    elif vrsta == "r":
        if r.endswith("ly") and len(r) - 2 >= 3:
            return r[:-2]
    return r

for r, v in [("running", "v"), ("walked", "v"), ("were", "v"),
             ("dangerous", "a"), ("happy", "a"), ("quickly", "r")]:
    print(f"   {r:<12} ({v}) -> {moja_lematizacija(r, v)}")
""")

# ═══════════════════════════ CELINA 6
md(r"""
---
# Celina 6 — Analiza sentimenta

Na predmetu se koriste dva alata.

**`TextBlob`** daje dva broja:

- **`polarity`** ∈ [−1, 1] — negativno / neutralno / pozitivno
- **`subjectivity`** ∈ [0, 1] — 0 je činjenica, 1 je lično mišljenje

**VADER** (`SentimentIntensityAnalyzer`) je pravljen za društvene mreže: razume
emotikone, velika slova i `!!!`. Vraća `neg`, `neu`, `pos` i zbirni **`compound`** ∈ [−1, 1].

> **Zamka:** `TextBlob` očekuje **tekst**, ne listu tokena. Ako proslediš listu, dobićeš
> grešku. Zato se tokeni pre analize spajaju sa `" ".join(tokeni)`.
""")

code(r"""
from nltk.sentiment import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()

primeri = ["I love this game, it is amazing!",
           "This is the worst thing I have ever played.",
           "The match starts at 8pm.",
           "NOT BAD AT ALL!!! 😀"]

pd.DataFrame([{
    "tekst": t,
    "tb_polarity": round(TextBlob(t).sentiment.polarity, 3),
    "tb_subjectivity": round(TextBlob(t).sentiment.subjectivity, 3),
    "vader_compound": round(vader.polarity_scores(t)["compound"], 3),
} for t in primeri])
""")

# ═══════════════════════════ CELINA 7
md(r"""
---
# Celina 7 — N-grami i predikcija sledeće reči

**N-gram** je niz od `n` uzastopnih reči. Za `["a","b","c","d"]` bigrami su
`(a,b), (b,c), (c,d)`.

Ideja predikcije: prebroji šta sve dolazi **posle** datog n-grama, pa vrati najčešće.

Tri nadogradnje koje se traže:

- **backoff** — ako za trigram nema kandidata, pokušaj sa bigramom, pa sa unigramom
- **izbor** — vrati najčešću, najređu ili nasumičnu reč iz kandidata
- **smoothing** — da nepoznat kandidat ne dobije verovatnoću 0:
  $$p(\text{rec}) = \frac{count(\text{rec}) + 1}{count(\text{ulaz}) + V}$$
  gde je $V$ ukupan broj različitih reči (Laplasovo poravnanje).
""")

code(r"""
def napravi_ngrame(tokeni, n):
    'Genericka funkcija - radi za bilo koje n.'
    return list(ngrams(tokeni, n))

tok_tales = [t.lower() for t in word_tokenize(tales) if t.isalpha()]
print(f"tales.txt -> {len(tok_tales)} tokena")
for n in (2, 3):
    ng = napravi_ngrame(tok_tales, n)
    print(f"\n{n}-grami: {len(ng)}, 3 najcesca:")
    for g, c in Counter(ng).most_common(3):
        print(f"   {' '.join(g):<28} {c}")
""")

code(r"""
def izgradi_model(tokeni, max_n=3):
    'Recnik: (n-gram) -> Counter sledecih reci. Gradi se za sve duzine do max_n.'
    model = {n: defaultdict(Counter) for n in range(1, max_n + 1)}
    for n in range(1, max_n + 1):
        for gram in ngrams(tokeni, n + 1):
            model[n][gram[:-1]][gram[-1]] += 1
    return model

MODEL = izgradi_model(tok_tales, max_n=3)
RECNIK = set(tok_tales)          # V za smoothing

def predvidi(ulaz, model=MODEL, nacin="najcesca", backoff=True, smoothing=False):
    # ulaz      : tuple ili lista reci, npr. ("the", "old", "frog")
    # nacin     : "najcesca" | "najredja" | "nasumicna"
    # backoff   : ako nema kandidata, skrati ulaz za jednu rec i pokusaj ponovo
    # smoothing : uz rezultat vrati i Laplasovu verovatnocu
    ulaz = tuple(w.lower() for w in ulaz)
    n = len(ulaz)
    while n >= 1:
        kandidati = model.get(n, {}).get(ulaz[-n:])
        if kandidati:
            if nacin == "najcesca":
                rec = kandidati.most_common(1)[0][0]
            elif nacin == "najredja":
                rec = kandidati.most_common()[-1][0]
            else:
                rec = random.choice(list(kandidati.elements()))
            if smoothing:
                p = (kandidati[rec] + 1) / (sum(kandidati.values()) + len(RECNIK))
                return rec, round(p, 6), n
            return rec, n
        if not backoff:
            break
        n -= 1                      # backoff: skrati kontekst
    return (None, 0) if not smoothing else (None, 0.0, 0)

print("bez smoothing-a :", predvidi(("the", "old", "frog")))
print("sa smoothing-om :", predvidi(("the", "old", "frog"), smoothing=True))
print("nepoznat ulaz   :", predvidi(("xyz", "qqq", "frog")), "  <- backoff spustio na 1-gram")
print("nasumicna rec   :", predvidi(("the", "old", "frog"), nacin="nasumicna"))
""")

# ═══════════════════════════ CELINA 8 — REŠENJE
md(r"""
---
---
# Celina 8 — KOMPLETNO REŠENJE ZADATKA

Zadatak iz `k1/K1/okto1.pdf`. Svaka tačka je jedna ćelija, rešena alatima iz prethodnih celina.
""")

md("### Tačka 1 — Učitati `tweets.json` i izdvojiti tekst prvih 20 tweet-ova")
code(r"""
with open("data/tweets.json", encoding="utf-8") as f:
    svi = json.load(f)

tweets = [t["text"] for t in svi[:20]]
print(f"Izdvojeno {len(tweets)} tweet-ova\n")
for i, t in enumerate(tweets[:3], 1):
    print(f"{i}. {t[:95]}")
""")

md("### Tačka 2 — Tokenizacija pomoću `TweetTokenizer` → **skup1**")
code(r"""
tt = TweetTokenizer(preserve_case=False)
skup1 = [tt.tokenize(t) for t in tweets]

print(f"skup1: {len(skup1)} tokenizovanih tweet-ova")
print("Prvi:", skup1[0])
""")

md("### Tačka 3 — Sopstvena funkcija za tokenizaciju → **skup2**")
code(r"""
skup2 = [moja_tokenizacija(t) for t in tweets]

print(f"skup2: {len(skup2)} tokenizovanih tweet-ova")
print("Prvi:", skup2[0])

print(f"\nPoredjenje na prvom tweet-u:")
print(f"   skup1 (TweetTokenizer): {len(skup1[0])} tokena")
print(f"   skup2 (rucno):          {len(skup2[0])} tokena")
print(f"   samo u skup1: {sorted(set(skup1[0]) - set(skup2[0]))[:10]}")
""")

md(r"""
### Tačka 4 — Iz oba skupa ukloniti 2 najčešća tokena

Koristi se funkcija `ukloni_najcesce` iz Celine 4. Najčešći tokeni se računaju
**posebno za svaki skup**, jer se skupovi razlikuju.
""")
code(r"""
skup1_bez2, izb1 = ukloni_najcesce(skup1, 2)
skup2_bez2, izb2 = ukloni_najcesce(skup2, 2)

print("skup1 — izbaceno:", izb1)
print("skup2 — izbaceno:", izb2)
print("\nskup1 prvi tweet posle uklanjanja:", skup1_bez2[0][:14])
print("skup2 prvi tweet posle uklanjanja:", skup2_bez2[0][:14])
""")

md(r"""
### Tačka 5 — `TextBlob` sentiment za oba skupa + `DataFrame`

Tokeni se pre analize spajaju nazad u tekst (`" ".join`), jer `TextBlob` radi nad tekstom.
""")
code(r"""
def sentiment(tokeni):
    b = TextBlob(" ".join(tokeni)).sentiment
    return b.polarity, b.subjectivity

redovi = []
for i, (t1, t2) in enumerate(zip(skup1_bez2, skup2_bez2)):
    p1, s1 = sentiment(t1)
    p2, s2 = sentiment(t2)
    redovi.append({
        "i": i,
        "tweet_skup1": " ".join(t1),
        "tweet_skup2": " ".join(t2),
        "polarity_skup1": round(p1, 4),
        "polarity_skup2": round(p2, 4),
        "subjectivity_skup1": round(s1, 4),
        "subjectivity_skup2": round(s2, 4),
        "razlika_polarity": round(p1 - p2, 4),
    })

df = pd.DataFrame(redovi)
print(f"Prosecan polarity — skup1: {df.polarity_skup1.mean():.4f}, "
      f"skup2: {df.polarity_skup2.mean():.4f}")
print(f"Tweet-ova sa razlicitim polarity: {(df.razlika_polarity != 0).sum()} od {len(df)}")
df[["i", "polarity_skup1", "polarity_skup2", "razlika_polarity",
    "subjectivity_skup1", "subjectivity_skup2"]].head(10)
""")

md("### Tačka 6 — Najpozitivniji, najnegativniji i najsubjektivniji tweet iz oba skupa")
code(r"""
def ispisi(naslov, red, kolona_teksta, kolona_ocene):
    print(f"\n{naslov}")
    print(f"   ocena: {red[kolona_ocene]}")
    print(f"   tekst: {red[kolona_teksta][:120]}")

for skup in ("skup1", "skup2"):
    print("=" * 70)
    print(f"SKUP: {skup}")
    print("=" * 70)
    pol, sub, tek = f"polarity_{skup}", f"subjectivity_{skup}", f"tweet_{skup}"
    ispisi("NAJPOZITIVNIJI",   df.loc[df[pol].idxmax()], tek, pol)
    ispisi("NAJNEGATIVNIJI",   df.loc[df[pol].idxmin()], tek, pol)
    ispisi("NAJSUBJEKTIVNIJI", df.loc[df[sub].idxmax()], tek, sub)
""")

md(r"""
---
## Zaključak poređenja skupova

`TweetTokenizer` zadržava `@mention`, `#hashtag` i emotikone kao tokene, a sopstvena
funkcija ih razbija ili briše. Zbog toga:

- **skup1** ima više tokena po tweet-u
- **skup2** ima čistije reči, ali je izgubio informaciju koju nose hashtagovi
- ocene sentimenta se razlikuju jer `TextBlob` vidi različit tekst

Nijedan pristup nije „tačan" — bira se prema zadatku. Ako se analizira o čemu se priča,
hashtagovi su korisni. Ako se meri sentiment običnog teksta, smetaju.
""")

# ═══════════════════════════ CELINA 9
md(r"""
---
# Celina 9 — Kontrolna lista

Pred izlazak na kolokvijum proveri da umeš, bez gledanja:

- [ ] učitati JSON (`json.load`) i TXT (`open(..., encoding="utf-8")`)
- [ ] napisati regularne izraze za URL, mention, hashtag
- [ ] objasniti **zašto URL ide pre interpunkcije**
- [ ] nabrojati razliku između `word_tokenize`, `TweetTokenizer`, `WordPunctTokenizer`
- [ ] napisati sopstvenu tokenizaciju po razmaku
- [ ] koristiti `Counter.most_common(n)` i izbaciti n najčešćih tokena
- [ ] razlikovati stemming od lematizacije i znati da lematizator traži `pos="v"`
- [ ] pozvati `TextBlob(...).sentiment.polarity` i `.subjectivity`
- [ ] napraviti `pandas.DataFrame` iz liste rečnika
- [ ] naći ekstreme sa `idxmax()` / `idxmin()`
- [ ] generisati n-grame i napisati predikciju sledeće reči sa backoff-om

**Najčešće greške:**

1. `TextBlob` dobija listu tokena umesto teksta → spoji sa `" ".join()`
2. Interpunkcija uklonjena pre URL-ova → URL se više ne prepoznaje
3. `WordNetLemmatizer` bez `pos="v"` → glagoli ostaju nepromenjeni
4. Otvaranje fajla bez `encoding="utf-8"` → `UnicodeDecodeError` na emotikonu
""")

nb = nbf.v4.new_notebook(cells=C)
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
               "language_info": {"name": "python"}}
nbf.write(nb, "K1_priprema.ipynb")
print(f"Upisano K1_priprema.ipynb — {len(C)} celija")
