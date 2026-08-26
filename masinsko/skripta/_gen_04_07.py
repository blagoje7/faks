# -*- coding: utf-8 -*-
"""Generise notebook-e 04-07 skripte iz Masinskog ucenja."""
import nbformat as nbf

def novi(): return []
def md(C, s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(C, s): C.append(nbf.v4.new_code_cell(s.strip()))
def upisi(C, ime):
    nb = nbf.v4.new_notebook(cells=C)
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    nbf.write(nb, ime)
    print(f"  {ime:<34} {len(C)} celija")

# ═══════════════════════════════════════════════════════ 04 STABLA
C = novi()
md(C, r"""
# 4. Stabla odlučivanja

## Osnovna ideja

Proces donošenja odluka može se modelovati nizom **if–then–else** pravila koja grananjem
vode do klasifikacije.

Stabla odlučivanja su direktno povezana sa **ekspertskim sistemima**:

| | ekspertski sistem | stablo odlučivanja |
|---|---|---|
| oblik znanja | if–then pravila | if–then pravila |
| kako nastaju | **ručno ih piše ekspert** | **uče se automatski iz podataka** |

Primer pravila:

```
IF Balance > 2000
    IF Income < 40k  ->  Kredit = ODBIJEN
    ELSE             ->  Kredit = ODOBREN
ELSE                 ->  Kredit = ODBIJEN
```

## Struktura stabla

| element | uloga |
|---|---|
| **čvor** | proverava atribut (kolonu) |
| **grana** | vrednost atributa (najčešće binarna) |
| **list** | konačna odluka / klasa |

Ključni izazov nije ideja stabla, nego **kako naučiti stablo iz podataka** — konkretno,
**kako izabrati atribut za grananje**.
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree, export_text
from sklearn.datasets import load_iris, load_diabetes
from sklearn.model_selection import train_test_split, cross_val_score

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42
print("Spremno.")
""")

md(C, r"""
## Entropija

Da bismo automatski izabrali najbolji atribut, uvodimo meru **neuređenosti** podataka —
**entropiju**.

Neka je $S$ skup trening instanci, $S^+$ pozitivni i $S^-$ negativni primeri:

$$p_+ = \frac{|S^+|}{|S|}, \qquad p_- = \frac{|S^-|}{|S|}$$

$$H(S) = -p_+ \log_2 p_+ - p_- \log_2 p_-$$

| entropija | značenje |
|---|---|
| **niska (0)** | skup je čist — sve instance su iste klase |
| **visoka (1)** | klase su savršeno pomešane |

### Zašto baš entropija — veza sa teorijom informacija

Poruka sa verovatnoćom $P$ zahteva dužinu koda $-\log_2 P$. Česta poruka dobija kratak
kod, retka dug. Entropija je **prosečan broj bitova** potrebnih za kodiranje poruke,
odnosno mera **neizvesnosti**.

Oznaka $H$ potiče od Claude-a Shannon-a.
""")

code(C, r"""
def entropija(p_plus):
    'Entropija binarnog skupa sa udelom pozitivnih p_plus.'
    if p_plus in (0, 1):
        return 0.0
    p_minus = 1 - p_plus
    return -p_plus * np.log2(p_plus) - p_minus * np.log2(p_minus)

for opis, poz, neg in [("sve pozitivno", 10, 0), ("9 poz / 1 neg", 9, 1),
                       ("pola-pola", 5, 5), ("9 poz / 5 neg (Play Tennis)", 9, 5)]:
    p = poz / (poz + neg)
    print(f"   {opis:<28} H = {entropija(p):.4f}")

pp = np.linspace(0.001, 0.999, 300)
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.plot(pp, [entropija(x) for x in pp], lw=2.5, color="#4C72B0")
ax.set_xlabel("udeo pozitivnih $p_+$"); ax.set_ylabel("entropija H(S)")
ax.set_title("Entropija je maksimalna kada su klase pomesane 50-50")
plt.tight_layout(); plt.show()
""")

md(C, r"""
## Information Gain (dobitak informacije)

Meri **koliko se smanjuje neizvesnost** kada podelimo podatke po nekom atributu:

$$IG(S, A) = H(S) - \sum_{i} \frac{|S_i|}{|S|} H(S_i)$$

gde su $S_i$ podskupovi nastali grananjem po atributu $A$.

- **veći IG** → bolji atribut
- bira se atribut sa **najvećim** IG i on postaje korenski čvor
""")

md(r"""
### Primer — Play Tennis

| Day | Outlook | Temp. | PlayTennis |
|---|---|---|---|
| D1 | Sunny | Hot | No |
| D2 | Sunny | Hot | No |
| D3 | Overcast | Hot | Yes |
| D4 | Rain | Mild | Yes |
| D5 | Rain | Cool | Yes |
| D6 | Rain | Cool | No |
| D7 | Overcast | Cool | Yes |
| D8 | Sunny | Mild | No |
| D9 | Sunny | Cold | Yes |
| D10 | Rain | Mild | Yes |
| D11 | Sunny | Mild | Yes |
| D12 | Overcast | Mild | Yes |
| D13 | Overcast | Hot | Yes |
| D14 | Rain | Mild | No |

Skup ima 9 „Yes" i 5 „No", pa je $H(S) = 0.94$.
""") if False else md(C, r"""
### Primer — Play Tennis

Klasičan primer sa predavanja. Skup ima **9 „Yes"** i **5 „No"**, pa je $H(S) \approx 0.94$.

Pitanje: koji atribut staviti u koren — `Outlook` ili `Temperature`?
""")

code(C, r"""
tenis = pd.DataFrame({
    "Day":     [f"D{i}" for i in range(1, 15)],
    "Outlook": ["Sunny","Sunny","Overcast","Rain","Rain","Rain","Overcast",
                "Sunny","Sunny","Rain","Sunny","Overcast","Overcast","Rain"],
    "Temp":    ["Hot","Hot","Hot","Mild","Cool","Cool","Cool",
                "Mild","Cold","Mild","Mild","Mild","Hot","Mild"],
    "PlayTennis": ["No","No","Yes","Yes","Yes","No","Yes",
                   "No","Yes","Yes","Yes","Yes","Yes","No"],
})
display(tenis)

def H(oznake):
    n = len(oznake)
    if n == 0: return 0.0
    return -sum((c/n) * np.log2(c/n) for c in pd.Series(oznake).value_counts() if c > 0)

Hs = H(tenis.PlayTennis)
print(f"\nH(S) = {Hs:.4f}   ({(tenis.PlayTennis=='Yes').sum()} Yes, {(tenis.PlayTennis=='No').sum()} No)")
""")

code(C, r"""
def information_gain(df, atribut, cilj="PlayTennis"):
    'IG(S,A) = H(S) - suma (|Si|/|S|) * H(Si)'
    ukupno = H(df[cilj])
    posle = 0.0
    print(f"\nAtribut '{atribut}':")
    for vrednost, grupa in df.groupby(atribut):
        udeo = len(grupa) / len(df)
        h = H(grupa[cilj])
        posle += udeo * h
        poz = (grupa[cilj] == "Yes").sum(); neg = (grupa[cilj] == "No").sum()
        print(f"   {vrednost:<10} S=[{poz}+, {neg}-]  |S_i|/|S| = {len(grupa)}/{len(df)}  H = {h:.4f}")
    ig = ukupno - posle
    print(f"   -> IG = {ukupno:.4f} - {posle:.4f} = {ig:.4f}")
    return ig

ig_out = information_gain(tenis, "Outlook")
ig_tmp = information_gain(tenis, "Temp")

print(f"\n{'='*54}")
print(f"IG(Outlook)     = {ig_out:.4f}")
print(f"IG(Temperature) = {ig_tmp:.4f}")
print(f"-> Outlook ide u koren: znatno vise smanjuje entropiju.")
""")

md(C, r"""
## Algoritam ID3

1. Počni sa celim skupom podataka
2. Izračunaj entropiju
3. Za svaki atribut izračunaj Information Gain
4. Izaberi atribut sa **najvećim** dobitkom
5. Podeli podatke po tom atributu
6. Ponovi postupak **rekurzivno** na svakom podskupu

## Algoritmi za konstrukciju stabla

| algoritam | autor / godina | osobine |
|---|---|---|
| **ID3** | Quinlan, 1984–85 | prvi; entropija + information gain; samo diskretni atributi |
| **C4.5 / C5.0** | Quinlan | poboljšani ID3; podržavaju **kontinuirane** atribute |
| **CART** | — | koristi se u `scikit-learn`; Gini indeks ili entropija |
""")

code(C, r"""
iris = load_iris(as_frame=True)
X, y = iris.data, iris.target
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=RS, stratify=y)

stablo = DecisionTreeClassifier(criterion="entropy", max_depth=3, random_state=RS).fit(Xtr, ytr)
print(f"Tacnost: trening {stablo.score(Xtr, ytr):.4f}, test {stablo.score(Xte, yte):.4f}\n")

fig, ax = plt.subplots(figsize=(15, 7))
plot_tree(stablo, feature_names=X.columns, class_names=iris.target_names,
          filled=True, rounded=True, fontsize=9, ax=ax)
plt.tight_layout(); plt.show()
""")

code(C, r"""
# isto stablo kao tekstualna if-then pravila
print(export_text(stablo, feature_names=list(X.columns)))
""")

md(C, r"""
## Overfitting kod stabala

Znak preprilagođavanja je **preveliko, duboko stablo** sa mnogo čvorova i grananja.

Cilj je **malo, kompaktno** stablo — po principu *Occam's razor*: jednostavnije je bolje.

### Kako se izbegava

| tehnika | opis |
|---|---|
| **Post-pruning** | stablo se prvo potpuno izgradi, pa se uklanjaju grane koje ne doprinose tačnosti |
| **Validacija** | ako uklanjanje grane ne smanjuje tačnost (npr. u k-fold CV), grana je nepotrebna |
| **Early stopping** | prekid grananja kada novi split ne donosi statistički značajno poboljšanje |

Ključni hiperparametri u `scikit-learn`: `max_depth`, `min_samples_leaf`, `min_samples_split`,
`ccp_alpha` (za post-pruning).
""")

code(C, r"""
dubine = range(1, 16)
tr, te, listovi = [], [], []
for d in dubine:
    m = DecisionTreeClassifier(max_depth=d, random_state=RS).fit(Xtr, ytr)
    tr.append(m.score(Xtr, ytr)); te.append(m.score(Xte, yte))
    listovi.append(m.get_n_leaves())

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(list(dubine), tr, "o-", label="trening", color="#4C72B0")
ax[0].plot(list(dubine), te, "s-", label="test", color="#C44E52")
ax[0].set_xlabel("max_depth"); ax[0].set_ylabel("tacnost")
ax[0].set_title("Tacnost u zavisnosti od dubine"); ax[0].legend()
ax[1].plot(list(dubine), listovi, "o-", color="#55A868")
ax[1].set_xlabel("max_depth"); ax[1].set_ylabel("broj listova")
ax[1].set_title("Slozenost stabla raste eksponencijalno")
plt.tight_layout(); plt.show()
""")

code(C, r"""
# post-pruning preko ccp_alpha (cost complexity pruning)
put = DecisionTreeClassifier(random_state=RS).cost_complexity_pruning_path(Xtr, ytr)
alfe = put.ccp_alphas[:-1]

rez = []
for a in alfe:
    m = DecisionTreeClassifier(random_state=RS, ccp_alpha=a).fit(Xtr, ytr)
    rez.append({"alpha": round(a, 5), "listova": m.get_n_leaves(),
                "trening": round(m.score(Xtr, ytr), 4), "test": round(m.score(Xte, yte), 4)})
tab = pd.DataFrame(rez).drop_duplicates("listova")
display(tab)
print("-> Orezivanje smanjuje broj listova, a test tacnost cesto ostaje ista ili raste.")
""")

md(C, r"""
## Stablo odlučivanja za regresiju

Ključna razlika u odnosu na klasifikaciju:

| | klasifikacija | regresija |
|---|---|---|
| predikcija | diskretna klasa | **kontinuirana vrednost** |
| u listu | većinska klasa | **prosečna vrednost** ciljne promenljive u tom regionu |
| kriterijum podele | entropija / Gini | **MSE** ili *variance reduction* |

Cilj je pronaći podelu koja **najviše smanjuje varijansu** ciljne promenljive.
""")

code(C, r"""
rng = np.random.RandomState(RS)
Xr = np.sort(rng.uniform(0, 10, 120)).reshape(-1, 1)
yr = np.sin(Xr).ravel() + rng.normal(0, 0.25, 120)
xx = np.linspace(0, 10, 500).reshape(-1, 1)

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
for a, d in zip(ax, (2, 5, 15)):
    m = DecisionTreeRegressor(max_depth=d, random_state=RS).fit(Xr, yr)
    a.scatter(Xr, yr, s=14, color="#4C72B0")
    a.plot(xx, m.predict(xx), color="#C44E52", lw=2)
    a.set_title(f"max_depth = {d}   ({m.get_n_leaves()} listova)")
plt.tight_layout(); plt.show()
print("Predikcija je STEPENASTA — u svakom listu je konstanta (prosek tog regiona).")
""")

md(C, r"""
## Zašto su stabla dobar izbor

1. **Diskretan, jasan izlaz** — pogodno kada treba konkretna odluka, a ne verovatnoća
2. **Rade i sa malo podataka** — upotrebljiv model već sa 10–200 instanci
3. **Otpornost na šum**
4. **Razdvojive klase** — jednostavna pravila često dovoljna
5. **Praktične prednosti** — brzo treniranje, mala memorija, jednostavna implementacija

Iako su konceptualno jednostavna, napredne verzije (**ensemble metode**, predavanje 12)
mogu postići performanse uporedive sa dubokim neuronskim mrežama.
""")
upisi(C, "04_stabla.ipynb")

# ═══════════════════════════════════════════════════════ 05 BAYES
C = novi()
md(C, r"""
# 5. Bajesovo učenje i Naivni Bajesov klasifikator

## Motivacija za probabilistički pristup

U praksi podaci **nisu savršeni** — šumoviti su, nepotpuni i ograničeni. Da bismo donosili
odluke u prisustvu **neizvesnosti**, potrebni su formalni modeli, a neizvesnost se formalno
modeluje **verovatnoćom**.

### Verovatnoća vs. stepen pripadnosti

| | verovatnoća $P(A)$ | stepen pripadnosti $\mu_A(x)$ |
|---|---|---|
| odnosi se na | **neizvesnost** | **neodređenost** |
| promenljiva $X$ | **nepoznata** | **poznata** |
| skup $A$ | dobro definisan | **neprecizno** definisan |
| pitanje | Kolika je verovatnoća da će se A dogoditi? | Koliko jako X pripada skupu A? |
| kada | **pre** događaja | **posle** događaja |

Naivni Bajes je **probabilistički** model — uvek radi **pre** donošenja odluke i računa
verovatnoće klasa.
""")

md(C, r"""
## Bajesova teorema

$$P(h \mid D) = \frac{P(D \mid h) \cdot P(h)}{P(D)}$$

| član | naziv | značenje |
|---|---|---|
| $P(h \mid D)$ | **posterior** | verovatnoća hipoteze **nakon** što smo videli podatke |
| $P(D \mid h)$ | **likelihood** (verodostojnost) | koliko podaci podržavaju hipotezu |
| $P(h)$ | **prior** | početno verovanje, **pre** podataka |
| $P(D)$ | **evidence** | verovatnoća podataka; služi kao normalizacija |

> Bajesova teorema govori **kako da promenimo mišljenje kada dobijemo nove podatke**.
> Posterior je kompromis između podataka (likelihood) i prethodnog znanja (prior).
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.datasets import load_iris, fetch_20newsgroups, make_classification
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
RS = 42

# --- primer sa predavanja: meningitis ---
P_M = 1 / 50_000       # ucestalost meningitisa u populaciji
P_S_M = 0.5            # ako neko ima meningitis, u 50% slucajeva ima ukocen vrat
P_S = 1 / 20           # ucestalost ukocenog vrata u opstoj populaciji

P_M_S = P_S_M * P_M / P_S
print(f"P(M)     = {P_M:.6f}   (prior — meningitis je REDAK)")
print(f"P(S|M)   = {P_S_M}      (likelihood)")
print(f"P(S)     = {P_S}       (evidence)")
print(f"\nP(M|S)   = {P_S_M} * {P_M:.6f} / {P_S} = {P_M_S:.6f} = {P_M_S*100:.2f}%")
print("\n-> Iako je ukocen vrat cest simptom, meningitis je izuzetno redak,")
print("   pa je konacna verovatnoca vrlo mala. SIMPTOM NIJE BOLEST.")
print("   Zato modeli koriste PRIOR — znanje koje imamo pre nego sto vidimo podatke.")
""")

md(C, r"""
## Osnovna pravila verovatnoće

**Pravilo proizvoda (AND):**
$$P(A \cap B) = P(A \mid B)P(B) = P(B \mid A)P(A)$$
Ovo je osnova Bajesove teoreme.

**Pravilo zbira (OR):**
$$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$
Presek se oduzima da se ne bi brojao dvaput.

**Zakon totalne verovatnoće:** ako su $A_1, \dots, A_n$ međusobno isključivi i pokrivaju ceo
univerzum ($\sum P(A_i) = 1$):
$$P(B) = \sum_{i=1}^{n} P(B \mid A_i) P(A_i)$$

U klasifikaciji su $A_i$ klase, $P(A_i)$ prior verovatnoće klasa, a njihov zbir je 1 —
zato modeli često **normalizuju** verovatnoće.
""")

md(C, r"""
## Od MAP do Maximum Likelihood

**MAP** (Maximum A Posteriori) — biramo najverovatniju hipotezu nakon podataka. Pošto je
$P(D)$ konstanta:

$$h_{MAP} = \arg\max_{h \in \mathcal{H}} P(D \mid h) \, P(h)$$

**ML** (Maximum Likelihood) — ako pretpostavimo da su **sve hipoteze jednako verovatne**
(uniformni prior), prior ne utiče na izbor:

$$h_{ML} = \arg\max_{h \in \mathcal{H}} P(D \mid h)$$

> **MAP = podaci + prethodno znanje.  ML = samo podaci.**
> ML je specijalan slučaj MAP-a kada nemamo (ili ignorišemo) prior znanje.

## Bayes optimalni klasifikator

$$v^* = \arg\max_{v \in \mathcal{V}} \sum_{h \in \mathcal{H}} P(v \mid h) \, P(h \mid D)$$

To je **probabilističko glasanje**: svaki model glasa za neku klasu, glas se ponderiše
verovatnoćom tog modela, doprinosi se sabiraju.

**Zašto nije praktičan?** Zahteva razmatranje **svih** hipoteza. U realnim problemima broj
hipoteza je ogroman i računanje je neizvodljivo. Teorijski idealan, računski preskup.
""")

code(C, r"""
# primer Bayes-optimalne odluke sa predavanja
hipoteze = {"h1": 0.5, "h2": 0.3, "h3": 0.4}      # posterior P(h|D)
odluke   = {"h1": "+", "h2": "-", "h3": "-"}       # sta svaka hipoteza predvidja

glasovi = {"+": 0.0, "-": 0.0}
for h, p in hipoteze.items():
    glasovi[odluke[h]] += p

for h in hipoteze:
    print(f"   {h}: P(h|D) = {hipoteze[h]}, predvidja '{odluke[h]}'")
print(f"\nUkupna podrska:  '+' = {glasovi['+']:.1f}   '-' = {glasovi['-']:.1f}")
print(f"Bayes-optimalna odluka: '{max(glasovi, key=glasovi.get)}'")
print("\n-> h1 je najverovatnija pojedinacna hipoteza i glasa za '+',")
print("   ali h2 i h3 ZAJEDNO imaju vecu podrsku za '-'.")
""")

md(C, r"""
## Naivna pretpostavka

Pošto je Bayes-optimalno preskupo, pravimo **svesno pojednostavljenje**.

> **Naivna pretpostavka:** atributi su **uslovno nezavisni** data klasa.
> $$a_1 \perp a_2 \perp \dots \perp a_n \mid v_j$$

Ne tvrdimo da su atributi u stvarnosti nezavisni — tvrdimo samo da ih **model tako tretira**.

### Matematička posledica

Bez pretpostavke, $P(a_1, a_2, \dots, a_n \mid v_j)$ je složena zajednička verovatnoća.
Sa pretpostavkom:

$$P(a_1, a_2, \dots, a_n \mid v_j) = \prod_{i=1}^{n} P(a_i \mid v_j)$$

Umesto jedne komplikovane verovatnoće računamo mnoštvo jednostavnih i **množimo ih**.
Zato Naive Bayes radi i sa 500+ atributa.

### Konačna formula

$$v^* = \arg\max_{v_j \in \mathcal{V}} P(v_j) \prod_{i=1}^{n} P(a_i \mid v_j)$$

Iz podataka se procenjuju samo: **prior klasa** $P(v_j)$ i **uslovne verovatnoće** $P(a_i \mid v_j)$.
""")

md(C, r"""
## Problem nulte verovatnoće i Laplasovo poravnanje

Ako je za neki atribut $P(a_i \mid v_j) = 0$, ceo proizvod postaje **nula** i klasa se
eliminiše bez obzira na sve ostale atribute. Sa 500 atributa dovoljna je **jedna** nula.

**Rešenje — Laplasovo poravnanje** (Laplace smoothing):

$$\hat{P}(a_i \mid v_j) = \frac{C(a_i, v_j) + m \cdot P}{C(v_j) + m}$$

- $C(a_i, v_j)$ — broj pojavljivanja atributa u klasi
- $C(v_j)$ — ukupan broj uzoraka klase
- $P$ — prior procena verovatnoće atributa
- $m$ — težina priora (parametar poravnanja)

Ne tvrdimo da je verovatnoća nula, već da je **mala ali ne nula**. To čini model robustnim.
""")

md(C, r"""
### Primer sa predavanja — Car Theft
""")

code(C, r"""
auta = pd.DataFrame({
    "Color":  ["Red","Red","Red","Yellow","Yellow","Yellow","Yellow","Yellow","Red","Red"],
    "Type":   ["Sports","Sports","Sports","Sports","Sports","SUV","SUV","SUV","SUV","Sports"],
    "Origin": ["Domestic","Domestic","Domestic","Domestic","Imported","Imported","Imported",
               "Domestic","Imported","Imported"],
    "Stolen": ["Y","N","Y","N","Y","N","Y","N","N","Y"],
})
display(auta)

nY = (auta.Stolen == "Y").sum(); nN = (auta.Stolen == "N").sum()
print(f"\nn_Y = {nY}, n_N = {nN}   ->   P(Y) = {nY/len(auta)}, P(N) = {nN/len(auta)}")
print("\nPitanje: da li ce 'Red Domestic SUV' biti ukraden?")
print("(ta kombinacija NE postoji u tabeli — zato nam treba model)")
""")

code(C, r"""
m_par, P_par = 3, 0.5          # parametri poravnanja sa predavanja

def laplas(atribut, vrednost, klasa):
    'P_hat(a_i | v_j) sa Laplasovim poravnanjem.'
    C_ai_vj = ((auta[atribut] == vrednost) & (auta.Stolen == klasa)).sum()
    C_vj = (auta.Stolen == klasa).sum()
    return (C_ai_vj + m_par * P_par) / (C_vj + m_par)

upit = {"Color": "Red", "Type": "SUV", "Origin": "Domestic"}
print(f"Imenilac je svuda isti: C(v_j) + m = 5 + 3 = 8\n")

verovatnoce = {}
for klasa in ("Y", "N"):
    print(f"Klasa {klasa}:")
    for atr, vred in upit.items():
        p = laplas(atr, vred, klasa)
        broj = ((auta[atr] == vred) & (auta.Stolen == klasa)).sum()
        print(f"   P({vred:<9}|{klasa}) = ({broj} + 3*0.5)/8 = {p:.4f}")
        verovatnoce[(atr, klasa)] = p
    print()

skor = {}
for klasa in ("Y", "N"):
    s = 0.5                                      # P(v_j)
    for atr in upit:
        s *= verovatnoce[(atr, klasa)]
    skor[klasa] = s
    print(f"Score({klasa}) = 0.5 * " + " * ".join(f"{verovatnoce[(a,klasa)]:.2f}" for a in upit)
          + f" = {s:.5f}")

odluka = max(skor, key=skor.get)
print(f"\nScore(N) {'>' if skor['N']>skor['Y'] else '<'} Score(Y)  ->  PREDIKCIJA: {odluka}")
print("   (auto NECE biti ukraden)" if odluka == "N" else "   (auto CE biti ukraden)")
""")

md(C, r"""
## Varijante u `scikit-learn`

| klasa | pretpostavka o $P(a_i \mid v_j)$ | kada se koristi |
|---|---|---|
| `GaussianNB` | normalna raspodela | **neprekidni** atributi |
| `MultinomialNB` | multinomijalna (broj pojavljivanja) | **tekst**, brojanje reči |
| `BernoulliNB` | Bernoulli (0/1) | binarni atributi |
""")

code(C, r"""
iris = load_iris()
Xtr, Xte, ytr, yte = train_test_split(iris.data, iris.target, test_size=0.3,
                                      random_state=RS, stratify=iris.target)
gnb = GaussianNB().fit(Xtr, ytr)
print(f"GaussianNB na iris: tacnost {gnb.score(Xte, yte):.4f}")
print(f"\nNauceni prior klasa: {gnb.class_prior_.round(3)}")
print(f"Nauceni proseci po klasi (prve 2 kolone):\n{gnb.theta_[:, :2].round(2)}")
""")

code(C, r"""
# MultinomialNB na tekstu — zadatak za koji je Naive Bayes i napravljen
kat = ["rec.sport.hockey", "sci.space", "talk.politics.mideast"]
tr = fetch_20newsgroups(subset="train", categories=kat, remove=("headers","footers","quotes"))
te = fetch_20newsgroups(subset="test", categories=kat, remove=("headers","footers","quotes"))

vec = CountVectorizer(stop_words="english", min_df=2)
Xtr_t = vec.fit_transform(tr.data)            # fit SAMO na treningu
Xte_t = vec.transform(te.data)

mnb = MultinomialNB().fit(Xtr_t, tr.target)
print(f"Dokumenata: {len(tr.data)} trening, {len(te.data)} test")
print(f"Recnik: {len(vec.vocabulary_):,} reci")
print(f"\nTacnost MultinomialNB: {accuracy_score(te.target, mnb.predict(Xte_t)):.4f}")
print(f"Bazna linija (najcesca klasa): {np.bincount(te.target).max()/len(te.target):.4f}")
""")

md(C, r"""
## Kada naivna pretpostavka škodi

Naive Bayes radi **iznenađujuće dobro** kada je pretpostavka približno tačna (tekst,
gde je vreća reči prirodna reprezentacija).

Ali kada su atributi **jako korelisani**, model ih broji višestruko i rezultat pada.
Sledeći primer to pokazuje merenjem.
""")

code(C, r"""
from sklearn.linear_model import LogisticRegression

print(f"{'situacija':<34} {'GaussianNB':>11} {'LogReg':>9}")
print("-" * 56)
for opis, redundantnih in [("nezavisni atributi (0 kopija)", 0),
                           ("umereno korelisani (5 kopija)", 5),
                           ("jako korelisani (15 kopija)", 15)]:
    Xc, yc = make_classification(n_samples=1200, n_features=20, n_informative=5,
                                 n_redundant=redundantnih, random_state=RS)
    a = cross_val_score(GaussianNB(), Xc, yc, cv=5).mean()
    b = cross_val_score(LogisticRegression(max_iter=3000), Xc, yc, cv=5).mean()
    print(f"{opis:<34} {a:>11.4f} {b:>9.4f}")
print("\n-> Kako raste korelacija, NB gubi vise od logisticke regresije,")
print("   jer krsi sopstvenu pretpostavku o uslovnoj nezavisnosti.")
""")

md(C, r"""
## Sažetak

**Prednosti**
- vrlo brz, radi i sa 500+ atributa
- traži malo podataka za procenu parametara
- prirodno daje verovatnoće klasa
- odličan baseline za klasifikaciju teksta

**Nedostaci**
- pretpostavka uslovne nezavisnosti je u praksi skoro uvek narušena
- problem nulte verovatnoće (rešava se Laplasovim poravnanjem)
- procenjene verovatnoće su često loše kalibrisane (previše samouverene)
""")
upisi(C, "05_bayes.ipynb")
print("\nGotovo za 04-05.")
