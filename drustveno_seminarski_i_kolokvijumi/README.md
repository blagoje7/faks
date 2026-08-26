# Društveno računarstvo — seminarski i pripreme za kolokvijume

```
seminarski_i_kolokvijumi/
├── seminarski/
│   ├── seminarski.ipynb          glavni rad (izvršen, sa rezultatima i grafikonima)
│   ├── ODBRANA.md                skripta za odbranu — šta se priča i pitanja
│   ├── seminarski.pdf            isti rad u PDF-u — 19 strana
│   ├── seminarski.html           međukorak ka PDF-u, može se otvoriti u pregledaču
│   ├── data/recenzije.csv        45.070 Steam recenzija
│   ├── _gen_seminarski.py        generator notebook-a
│   └── _u_pdf.py                 HTML → PDF
│
└── kolokvijumi_priprema/
    ├── K1_priprema.ipynb         I kolokvijum — teorija + rešenje
    ├── K2_priprema.ipynb         II kolokvijum — teorija + rešenje
    ├── ZADACI_sa_uputima.md      pun tekst zadataka sa uputima na vežbe
    ├── data/                     tweets.json, tweets.txt, sentences.txt, tales.txt, text.txt
    ├── _gen_k1.py
    └── _gen_k2.py
```

## Seminarski rad

**Tema:** Kako se ton korisničkih recenzija menja sa iskustvom — analiza 45.070 Steam
recenzija igre Dota 2.

Rad koristi alate sa vežbi (`nltk`, `TextBlob`, VADER, `TfidfVectorizer`, `ngrams`) i
odgovara na pitanje da li iskustvo sa proizvodom menja ton recenzije.

**Glavni nalazi:**

1. Udeo pozitivnih recenzija raste do vrha na 100–250 sati (89%), pa opada na 66% kod
   igrača sa preko 8.000 sati
2. Dužina recenzije raste sa iskustvom
3. Duge recenzije su znatno negativnije od kratkih — ceo skup je 80% pozitivan, a
   recenzije duže od 200 reči padaju ispod 50%
4. Zaključak: vidljiva slika proizvoda sistematski odstupa od stvarnog raspoloženja
   korisnika, zbog načina na koji platforma rangira recenzije

`ODBRANA.md` je priprema za odbranu: redosled izlaganja poglavlje po poglavlje, brojevi
koje treba znati napamet, pitanja sa odgovorima i tri slabosti rada sa spremnom odbranom.
Svaki alat upotrebljen u radu je u njemu povezan sa celinom u `kolokvijumi_priprema/` gde
je ta teorija objašnjena.

Za ponovno pravljenje PDF-a:

```bash
python -m jupyter nbconvert --to html --embed-images seminarski.ipynb
python _u_pdf.py seminarski.html seminarski.pdf
```

## Pripreme za kolokvijume

Oba notebook-a imaju isti raspored: **logičke celine** sa teorijom i malim primerom, pa
**kompletno rešenje** kolokvijumskog zadatka, pa **kontrolna lista** sa najčešćim greškama.

| notebook | celina | tema |
|---|---|---|
| **K1** | 1–7 | učitavanje, čišćenje, tokenizacija, frekvencije, stemming/lematizacija, sentiment, n-grami |
| | 8 | rešenje zadatka iz `k1/K1/okto1.pdf` |
| **K2** | 1–10 | parsiranje kolekcije, tri skupa, BoW/TF-IDF, POS, NER, metapodaci, interakcije, sažimanje, MNB |
| | 11 | rešenje zadatka iz `k2/K2/k2 zadatak.pdf` |

`ZADACI_sa_uputima.md` sadrži pun tekst oba zadatka, tačku po tačku, sa uputom na
notebook sa vežbi gde je svaka tehnika obrađena i na celinu u pripremi gde je rešena.

Oba notebook-a su **izvršena i rade** sa podacima u `data/`. Pokreću se iz svog foldera:

```bash
cd kolokvijumi_priprema
python -m jupyter notebook K1_priprema.ipynb
```

## Okruženje

Koristi se venv predmeta: `drustvenoRacunarstvo/drustveno/`. Dodatno su instalirani
`scipy`, `nbformat`, `nbconvert` i `playwright` (za PDF).

NLTK resursi koje notebook-ovi skidaju pri prvom pokretanju: `punkt`, `punkt_tab`,
`stopwords`, `wordnet`, `omw-1.4`, `averaged_perceptron_tagger(_eng)`,
`maxent_ne_chunker(_tab)`, `words`, `vader_lexicon`.
