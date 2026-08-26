# -*- coding: utf-8 -*-
"""Generise notebook-e 01-07 skripte iz Masinskog ucenja."""
import nbformat as nbf

def novi():
    return []

def md(C, s): C.append(nbf.v4.new_markdown_cell(s.strip()))
def code(C, s): C.append(nbf.v4.new_code_cell(s.strip()))

def upisi(C, ime):
    nb = nbf.v4.new_notebook(cells=C)
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    nbf.write(nb, ime)
    print(f"  {ime:<34} {len(C)} celija")

ZAGLAVLJE = """
> **Skripta iz Mašinskog učenja** — predavanje {broj}: {tema}
> Teorija prati prezentaciju sa predavanja, uz izvršive primere.
"""

# ═══════════════════════════════════════════════════════ 01 UVOD
C = novi()
md(C, r"""
# 1. Uvod u mašinsko učenje

## Šta je mašinsko učenje

Mašinsko učenje je oblast veštačke inteligencije koja omogućava računarskim sistemima da
**uče obrasce iz podataka** i donose odluke ili predikcije **bez eksplicitnog programiranja
pravila**.

$$\text{Podaci} + \text{algoritam} \rightarrow \text{model} \qquad
\text{Model} + \text{novi podaci} \rightarrow \text{predikcija}$$

### Definicija po Mitchell-u (1997)

> Računarski program uči iz **iskustva I** u odnosu na grupu **zadataka Z** i **meru
> performansi P**, ako se njegova performansa nad zadatkom iz Z poboljšava zahvaljujući
> iskustvu I.

**Primer — spam filter:**

| | |
|---|---|
| **Zadatak (Z)** | klasifikacija poruka na spam / not-spam |
| **Iskustvo (I)** | skup označenih poruka + označavanje od strane korisnika |
| **Performanse (P)** | procenat ispravno klasifikovanih poruka |

## Klasično programiranje vs. mašinsko učenje

| pristup | šta se zadaje | šta se dobija |
|---|---|---|
| klasično programiranje | Ulaz + **Pravila** | Izlaz |
| mašinsko učenje | Ulaz + **Izlaz** | **Pravila** |

Kod klasičnog programiranja logiku piše čovek. Kod mašinskog učenja logika se **uči iz podataka**.

## Odnos oblasti

- **Veštačka inteligencija (AI)** — široka oblast sistema koji pokazuju inteligentno ponašanje: pravila, ekspertski sistemi, planiranje, rezonovanje, mašinsko učenje
- **Mašinsko učenje (ML)** — podoblast AI; sistem uči obrasce iz podataka
- **Duboko učenje (DL)** — podoblast ML; višeslojne neuronske mreže
- **Nauka o podacima** — šira disciplina (prikupljanje, analiza, vizualizacija, odlučivanje) koja koristi ML kao jedan od alata
""")

md(C, r"""
## Tipovi mašinskog učenja

- **Nadgledano učenje** (supervised) — imamo ulaz i **poznatu oznaku**
- **Nenadgledano učenje** (unsupervised) — nemamo oznake, tražimo strukturu
- **Polunadgledano učenje** (semi-supervised)
- **Učenje potkrepljenjem** (reinforcement learning)

### Nadgledano učenje

| problem | ciljna promenljiva | primer |
|---|---|---|
| **Klasifikacija** | kategorička | spam / not-spam, mačka / pas / ptica |
| **Regresija** | neprekidna | cena stana, temperatura |

### Nenadgledano učenje

| problem | algoritmi |
|---|---|
| **Klasterovanje** | k-means, hijerarhijsko, DBSCAN, Gaussian Mixture Models |
| **Redukcija dimenzionalnosti** | PCA, t-SNE, UMAP |
| **Procena gustine** | koliko je verovatno da se podatak pojavi na tom mestu u prostoru |
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris, load_diabetes

plt.rcParams["figure.figsize"] = (9, 4.5)
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
RS = 42

# --- primer skupa za KLASIFIKACIJU: kategoricka ciljna promenljiva ---
iris = load_iris(as_frame=True)
print("KLASIFIKACIJA — iris")
print(f"   X (ulaz)  : {iris.data.shape[0]} uzoraka x {iris.data.shape[1]} obelezja")
print(f"   y (izlaz) : klase {list(iris.target_names)}")
print(f"   raspodela : {np.bincount(iris.target).tolist()}")

# --- primer skupa za REGRESIJU: neprekidna ciljna promenljiva ---
dia = load_diabetes(as_frame=True)
print("\nREGRESIJA — diabetes")
print(f"   X (ulaz)  : {dia.data.shape[0]} uzoraka x {dia.data.shape[1]} obelezja")
print(f"   y (izlaz) : neprekidan, opseg [{dia.target.min():.0f}, {dia.target.max():.0f}]")
""")

md(C, r"""
## Osnovni pojmovi

**Ulaz $X$** — feature-i / atributi / obeležja. Vektor osobina koji opisuje jedan primer.
Mogu biti numerički ili kategorički.

**Izlaz $y$** — oznaka / target. Vrednost koju model treba da predvidi. Diskretna kod
klasifikacije, neprekidna kod regresije.

### Parametri vs. hiperparametri

| | parametri | hiperparametri |
|---|---|---|
| kada se određuju | **tokom** treniranja | **pre** treniranja |
| ko ih određuje | algoritam, iz podataka | mi |
| primeri | težine u regresiji i mreži | learning rate, dubina stabla, broj suseda $k$ |
""")

code(C, r"""
X = iris.data
y = iris.target

print("X — prvih 5 redova:")
display(X.head())
print(f"\ny — prvih 10 oznaka: {y.values[:10]}")
print(f"\nJedan uzorak je vektor osobina duzine {X.shape[1]}:")
print(f"   {X.iloc[0].to_dict()}  ->  klasa {iris.target_names[y.iloc[0]]}")
""")

md(C, r"""
## Podela podataka

| skup | uloga |
|---|---|
| **trening** | učenje modela |
| **validacioni** | izbor modela i podešavanje hiperparametara |
| **test** | **isključivo** konačna evaluacija; nije dostupan algoritmu ni u jednom delu učenja |

Uobičajene podele: 80/20 (train/test) ili 70/15/15 (train/val/test).

**Stratifikacija** čuva odnos klasa u svim skupovima — bitna kod neuravnoteženih podataka.
""")

code(C, r"""
from sklearn.model_selection import train_test_split

# bez stratifikacije
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=1)
print("BEZ stratifikacije — raspodela klasa u test skupu:", np.bincount(yte).tolist())

# sa stratifikacijom
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=1, stratify=y)
print("SA stratifikacijom  — raspodela klasa u test skupu:", np.bincount(yte).tolist())
print("\nOriginalna raspodela                             :", np.bincount(y).tolist())
""")

md(C, r"""
## Kros-validacija

Jedna podela na train/test daje **nestabilnu** procenu — rezultat zavisi od toga koji su
uzorci slučajno završili u testu.

**k-fold kros-validacija**: skup se deli na $k$ podskupova (foldova). Model se trenira
$k$ puta, svaki put je drugi fold validacioni. Konačni rezultat je **prosek**.

$$\text{Performansa} = \frac{1}{k}\sum_{i=1}^{k} \text{Performansa}_i$$

**LOOCV** (Leave-One-Out) je specijalan slučaj sa $k = n$ — svaki uzorak je jednom
validacioni. Maksimalno koristi podatke, ali je računski vrlo skup.
""")

code(C, r"""
from sklearn.model_selection import cross_val_score, KFold
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(max_depth=3, random_state=RS)

# jedna podela — nestabilna procena
pojedinacne = []
for seed in range(6):
    a, b, c, d = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    pojedinacne.append(model.fit(a, c).score(b, d))
print(f"6 razlicitih podela: {[round(s, 3) for s in pojedinacne]}")
print(f"   raspon: {min(pojedinacne):.3f} do {max(pojedinacne):.3f}  <- velika razlika!\n")

# 5-fold CV — stabilnija procena
cv = cross_val_score(model, X, y, cv=KFold(5, shuffle=True, random_state=RS))
print(f"5-fold CV: {cv.round(3).tolist()}")
print(f"   prosek {cv.mean():.3f} +- {cv.std():.3f}")
""")

md(C, r"""
## Overfitting i underfitting

| | trening greška | test greška | uzrok |
|---|---|---|---|
| **Underfitting** | velika | velika | model previše jednostavan |
| **Overfitting** | **mala** | **velika** | model previše složen, „nauči napamet" |

Cilj mašinskog učenja nije mala greška na treningu, nego **dobra generalizacija** na nove
podatke.
""")

code(C, r"""
dubine = range(1, 21)
tr_rez, te_rez = [], []
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.35, random_state=RS, stratify=y)

for d in dubine:
    m = DecisionTreeClassifier(max_depth=d, random_state=RS).fit(Xtr, ytr)
    tr_rez.append(m.score(Xtr, ytr))
    te_rez.append(m.score(Xte, yte))

fig, ax = plt.subplots()
ax.plot(dubine, tr_rez, "o-", label="trening", color="#4C72B0")
ax.plot(dubine, te_rez, "s-", label="test", color="#C44E52")
ax.set_xlabel("dubina stabla (slozenost modela)"); ax.set_ylabel("tacnost")
ax.set_title("Underfitting levo, overfitting desno")
ax.legend(); plt.tight_layout(); plt.show()

print(f"Dubina 1 : trening {tr_rez[0]:.3f}, test {te_rez[0]:.3f}   <- UNDERFITTING")
print(f"Dubina 20: trening {tr_rez[-1]:.3f}, test {te_rez[-1]:.3f}   <- OVERFITTING")
""")

md(C, r"""
## Tok rada u mašinskom učenju (ML pipeline)

1. Prikupljanje podataka
2. Čišćenje podataka
3. Feature engineering
4. Podela skupa (train / validation / test)
5. Treniranje modela
6. Evaluacija
7. Deployment
8. Monitoring

## Četiri česte greške u praksi

1. **Data leakage** — informacija iz test skupa procuri u obuku
2. **Treniranje na test skupu**
3. **Overfitting**
4. **Pogrešne metrike** — npr. tačnost kod jako neuravnoteženih klasa

## Objašnjiva veštačka inteligencija (XAI)

Modeli često funkcionišu kao **crna kutija**. Interpretabilnost je važna zbog:
poverenja korisnika, regulative, i otkrivanja grešaka i pristrasnosti.

Pristupi: interpretabilni modeli (stabla) i post-hoc objašnjenja (SHAP, LIME).
Detaljno u predavanju 13.
""")
upisi(C, "01_uvod.ipynb")

# ═══════════════════════════════════════════════════════ 02 REGRESIJA
C = novi()
md(C, r"""
# 2. Linearna i logistička regresija

## Pristrasnost i varijansa (bias–variance)

$$\mathbb{E}[\text{greška na testu}] = \text{Varijansa} + \text{Pristrasnost}^2 + \text{šum}$$

**Pristrasnost (bias)** — greška zbog **pojednostavljenih pretpostavki** ugrađenih u model.
Visoka pristrasnost → underfitting.

**Varijansa (variance)** — mera koliko se naučena funkcija menja kada se model trenira na
**različitim trening skupovima**. Visoka varijansa → overfitting.

| model | pristrasnost | varijansa |
|---|---|---|
| fleksibilniji | **manja** | **veća** |
| manje fleksibilan | veća | manja |

Najbolji model **balansira** ove dve greške.
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (mean_squared_error, r2_score, confusion_matrix,
                             accuracy_score, precision_score, recall_score,
                             roc_curve, roc_auc_score, ConfusionMatrixDisplay)

plt.rcParams["figure.figsize"] = (9, 4.5)
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42
rng = np.random.RandomState(RS)
print("Spremno.")
""")

md(C, r"""
## Jednostavna linearna regresija

$$Y = \beta_0 + \beta_1 X + \varepsilon$$

- $\beta_0$ — odsečak (intercept)
- $\beta_1$ — nagib (slope)
- $\varepsilon$ — greška / šum

### Metod najmanjih kvadrata

**Rezidual** je razlika stvarne i predviđene vrednosti: $\varepsilon_i = y_i - \hat{y}_i$

**RSS** (suma kvadrata reziduala):

$$RSS = \sum_{i=1}^{n}(y_i - \hat{y}_i)^2$$

Metod najmanjih kvadrata bira $\hat\beta_0$ i $\hat\beta_1$ koji **minimizuju RSS**.
Veći reziduali imaju veći uticaj jer se kvadriraju.
""")

code(C, r"""
# sinteticki podaci sa poznatom pravom vezom
n = 60
Xs = rng.uniform(0, 10, n)
prava_b0, prava_b1 = 4.0, 2.5
ys = prava_b0 + prava_b1 * Xs + rng.normal(0, 3, n)

lin = LinearRegression().fit(Xs.reshape(-1, 1), ys)
b0, b1 = lin.intercept_, lin.coef_[0]
pred = lin.predict(Xs.reshape(-1, 1))
rss = np.sum((ys - pred) ** 2)

print(f"Prava veza    : y = {prava_b0:.2f} + {prava_b1:.2f}*x")
print(f"Procenjeno    : y = {b0:.2f} + {b1:.2f}*x")
print(f"RSS           : {rss:.1f}")

fig, ax = plt.subplots()
ax.scatter(Xs, ys, s=30, color="#4C72B0", label="podaci", zorder=3)
xx = np.linspace(0, 10, 100)
ax.plot(xx, lin.predict(xx.reshape(-1, 1)), color="#C44E52", lw=2, label="fit")
for xi, yi, pi in zip(Xs[:25], ys[:25], pred[:25]):
    ax.plot([xi, xi], [yi, pi], color="gray", lw=0.8, alpha=0.6)
ax.set_title("Sive linije su reziduali — RSS je zbir njihovih kvadrata")
ax.legend(); plt.tight_layout(); plt.show()
""")

md(C, r"""
## Koliko je model dobro prilagođen

**RSE** (standardna greška reziduala) — veća vrednost znači lošije prilagođavanje.

**$R^2$** (koeficijent determinacije) — koliki deo varijabilnosti u $Y$ je objašnjen:

$$R^2 = 1 - \frac{RSS}{TSS}, \qquad TSS = \sum (y_i - \bar y)^2$$

| $R^2$ | značenje |
|---|---|
| 1 | savršeno prilagođavanje |
| 0 | model ne objašnjava ništa više od proste srednje vrednosti |
| < 0 | model je **lošiji** od predviđanja proseka |

**Koja vrednost je „dobra" zavisi od oblasti.** U fizici se očekuje $R^2$ blizu 1. U
biologiji i društvenim naukama $R^2 \approx 0.4$ može biti dobar rezultat.
""")

code(C, r"""
tss = np.sum((ys - ys.mean()) ** 2)
r2_rucno = 1 - rss / tss
rse = np.sqrt(rss / (n - 2))

print(f"RSS = {rss:.1f}")
print(f"TSS = {tss:.1f}")
print(f"R^2 (rucno)   = {r2_rucno:.4f}")
print(f"R^2 (sklearn) = {r2_score(ys, pred):.4f}")
print(f"RSE           = {rse:.3f}")

# demonstracija granicnih slucajeva
prosek = np.full_like(ys, ys.mean())
lose = ys.mean() + 5 * (Xs - Xs.mean())      # namerno pogresan nagib
print(f"\nR^2 za predikciju proseka : {r2_score(ys, prosek):.4f}   (definiciono 0)")
print(f"R^2 za namerno los model  : {r2_score(ys, lose):.4f}   (negativan!)")
""")

md(C, r"""
## Višestruka linearna regresija

$$Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \dots + \beta_p X_p + \varepsilon$$

**Tumačenje koeficijenta $\beta_j$:** prosečan uticaj povećanja $X_j$ za jednu jedinicu na
$Y$, **dok su sve ostale promenljive fiksirane**.

Zatvoreno (analitičko) rešenje:

$$\hat{\boldsymbol\beta} = (\mathbf{X}^\top\mathbf{X})^{-1}\mathbf{X}^\top\mathbf{Y}$$

> **Zašto ne raditi prostu regresiju posebno za svaku promenljivu?** Zato što se time
> zanemaruje **međusobni uticaj** promenljivih. Koeficijent iz proste regresije može biti
> zavaravajući ako je promenljiva korelisana sa nekom drugom.
""")

code(C, r"""
# TV, radio i novine -> prodaja; novine su korelisane sa radiom ali same ne uticu
m = 200
tv = rng.uniform(0, 300, m)
radio = rng.uniform(0, 50, m)
novine = 0.6 * radio + rng.normal(0, 8, m)          # korelisano sa radiom!
prodaja = 3 + 0.045 * tv + 0.19 * radio + rng.normal(0, 1.5, m)
df = pd.DataFrame({"TV": tv, "radio": radio, "novine": novine, "prodaja": prodaja})

print("PROSTE regresije (svaka promenljiva sama):")
for kol in ["TV", "radio", "novine"]:
    k = LinearRegression().fit(df[[kol]], df.prodaja).coef_[0]
    print(f"   {kol:<8} koeficijent = {k:+.4f}")

vis = LinearRegression().fit(df[["TV", "radio", "novine"]], df.prodaja)
print("\nVISESTRUKA regresija (sve zajedno):")
for kol, k in zip(["TV", "radio", "novine"], vis.coef_):
    print(f"   {kol:<8} koeficijent = {k:+.4f}")
print(f"\nKorelacija novine-radio: {df.novine.corr(df.radio):.3f}")
print("-> U prostoj regresiji 'novine' izgledaju znacajno, u visestrukoj koeficijent pada")
print("   ka nuli. Njihov 'efekat' je bio indirektan, preko radija.")
""")

md(C, r"""
## Kvalitativni (kategorijalni) ulazi

Kategorijalna promenljiva se uvodi preko **dummy (indikatorskih)** promenljivih.

Za promenljivu sa $K$ kategorija koristi se **$K-1$** dummy promenljivih. Jedna kategorija
se bira kao **bazna (referentna)** i predstavljena je sa svim nulama.
""")

code(C, r"""
boje = pd.Series(rng.choice(["plava", "zelena", "braon"], 12))
dummy = pd.get_dummies(boje, prefix="oci", drop_first=True).astype(int)
print("Kategorije:", sorted(boje.unique()))
print(f"Broj dummy promenljivih: {dummy.shape[1]}  (K-1 = 3-1 = 2)")
print("Bazna kategorija je ona koje NEMA medju kolonama — nju predstavljaju sve nule.\n")
display(pd.concat([boje.rename("boja"), dummy], axis=1).head(6))
""")

md(C, r"""
## Potencijalni problemi linearne regresije

1. **Nelinearnost** odnosa između odgovora i prediktora
2. **Ne-aditivnost** prediktora — interakcije
3. **Nekonstantna varijansa** grešaka (heteroskedastičnost)
4. **Outlieri** — neuobičajene vrednosti $Y$
5. **Tačke sa velikim uticajem** (high-leverage) — neuobičajene vrednosti $X$
6. **Korelisanost grešaka**
7. **Kolinearnost** — prediktori su međusobno snažno korelisani

### Nelinearnost → polinomska regresija

$$Y = \beta_0 + \beta_1 X + \beta_2 X^2 + \varepsilon$$

Iako sadrži kvadratni član, model je i dalje **linearan u parametrima**, pa se fituje
istim metodom najmanjih kvadrata.

Dijagnostika: **grafik reziduala**. Ako se u njemu vidi obrazac, pretpostavka linearnosti
je upitna.
""")

code(C, r"""
Xn = rng.uniform(-3, 3, 120)
yn = 2 + 1.5 * Xn + 0.9 * Xn ** 2 + rng.normal(0, 1.2, 120)
Xn2 = Xn.reshape(-1, 1)

lin_m = LinearRegression().fit(Xn2, yn)
pol_m = make_pipeline(PolynomialFeatures(2), LinearRegression()).fit(Xn2, yn)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
xx = np.linspace(-3, 3, 200).reshape(-1, 1)
ax[0].scatter(Xn, yn, s=18, color="#4C72B0")
ax[0].plot(xx, lin_m.predict(xx), color="#C44E52", lw=2, label=f"linearan (R2={r2_score(yn, lin_m.predict(Xn2)):.3f})")
ax[0].plot(xx, pol_m.predict(xx), color="#55A868", lw=2, label=f"kvadratni (R2={r2_score(yn, pol_m.predict(Xn2)):.3f})")
ax[0].set_title("Podaci i dva modela"); ax[0].legend()

ax[1].scatter(lin_m.predict(Xn2), yn - lin_m.predict(Xn2), s=18, color="#C44E52", label="linearan")
ax[1].scatter(pol_m.predict(Xn2), yn - pol_m.predict(Xn2), s=18, color="#55A868", alpha=0.6, label="kvadratni")
ax[1].axhline(0, color="k", lw=1)
ax[1].set_xlabel("predvidjeno"); ax[1].set_ylabel("rezidual")
ax[1].set_title("Grafik reziduala — obrazac znaci problem"); ax[1].legend()
plt.tight_layout(); plt.show()
""")

md(C, r"""
### Ne-aditivnost → interakcioni član

$$Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \beta_3 X_1 X_2 + \varepsilon$$

Član $X_1 X_2$ omogućava da **efekat jednog prediktora zavisi od vrednosti drugog**.
Primer: popust ima različit efekat u sezoni i van sezone.
""")

code(C, r"""
popust = rng.uniform(0, 30, 300)
sezona = rng.choice([0, 1], 300)
# efekat popusta je JACI u sezoni -> interakcija
prod = 10 + 0.5 * popust + 4 * sezona + 0.6 * popust * sezona + rng.normal(0, 2, 300)
d2 = pd.DataFrame({"popust": popust, "sezona": sezona, "prodaja": prod})

bez = LinearRegression().fit(d2[["popust", "sezona"]], d2.prodaja)
d2["inter"] = d2.popust * d2.sezona
sa = LinearRegression().fit(d2[["popust", "sezona", "inter"]], d2.prodaja)

print(f"BEZ interakcije: R2 = {r2_score(d2.prodaja, bez.predict(d2[['popust','sezona']])):.4f}")
print(f"SA interakcijom: R2 = {r2_score(d2.prodaja, sa.predict(d2[['popust','sezona','inter']])):.4f}")
print(f"\nKoeficijent interakcije: {sa.coef_[2]:+.4f}")
print("-> pozitivan: popust radi JACE u sezoni nego van nje")
""")

md(C, r"""
### Nekonstantna varijansa → log-transformacija

Prepoznaje se po **levkastom obliku** na grafiku reziduala. Rešenje je transformacija
ciljne promenljive konkavnom funkcijom, najčešće **logaritmom**.

Interpretacija se menja: bez loga koeficijent znači „porast za toliko jedinica", sa logom
znači „porast za toliko **procenata**".
""")

code(C, r"""
Xh = rng.uniform(1, 100, 300)
yh = 5 * Xh + rng.normal(0, 0.35 * Xh, 300)          # greska raste sa X -> levak
Xh2 = Xh.reshape(-1, 1)

m1 = LinearRegression().fit(Xh2, yh)
m2 = LinearRegression().fit(Xh2, np.log(yh - yh.min() + 1))

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].scatter(m1.predict(Xh2), yh - m1.predict(Xh2), s=14, color="#C44E52")
ax[0].axhline(0, color="k", lw=1); ax[0].set_title("BEZ transformacije — levak")
ax[0].set_xlabel("predvidjeno"); ax[0].set_ylabel("rezidual")

yl = np.log(yh - yh.min() + 1)
ax[1].scatter(m2.predict(Xh2), yl - m2.predict(Xh2), s=14, color="#55A868")
ax[1].axhline(0, color="k", lw=1); ax[1].set_title("SA log-transformacijom — ravnomerno")
ax[1].set_xlabel("predvidjeno"); ax[1].set_ylabel("rezidual")
plt.tight_layout(); plt.show()
""")

md(C, r"""
### Regularizacija — Ridge i Lasso

Varijacije linearne regresije koje dodaju kazneni član i time smanjuju overfitting:

| metoda | kazna | efekat |
|---|---|---|
| **Ridge** (L2) | $\lambda \sum w_j^2$ | smanjuje sve težine ka nuli |
| **Lasso** (L1) | $\lambda \sum \lvert w_j \rvert$ | može težine **ugasiti** na tačno 0 |

Lasso zato služi i kao **izbor obeležja**.
""")

code(C, r"""
from sklearn.datasets import make_regression
Xr, yr = make_regression(n_samples=100, n_features=25, n_informative=5,
                         noise=12, random_state=RS)
Xr_s = StandardScaler().fit_transform(Xr)

rezultati = []
for ime, m in [("LinearRegression", LinearRegression()),
               ("Ridge (alpha=10)", Ridge(alpha=10)),
               ("Lasso (alpha=1)", Lasso(alpha=1.0))]:
    m.fit(Xr_s, yr)
    rezultati.append({"model": ime, "R2": round(r2_score(yr, m.predict(Xr_s)), 4),
                      "tezina ~0": int(np.sum(np.abs(m.coef_) < 1e-6)),
                      "max |w|": round(np.abs(m.coef_).max(), 1)})
pd.DataFrame(rezultati)
""")

md(C, r"""
---
## Logistička regresija

Koristi se za **klasifikaciju**. Modeluje verovatnoću:

$$P(Y = 1 \mid X) = \sigma(\beta_0 + \beta_1 X), \qquad \sigma(z) = \frac{1}{1 + e^{-z}}$$

### Zašto ne linearna regresija za verovatnoću?

- verovatnoća mora biti u $[0, 1]$, a linearna funkcija daje i vrednosti $< 0$ i $> 1$
- linearna veza nije realistična za klasifikaciju

### Uticaj parametara na sigmoidnu krivu

| parametar | efekat |
|---|---|
| $\beta_0$ | **horizontalni pomak** krive levo/desno; početna sklonost ka klasi 1 |
| $\beta_1$ | **strmina** krive; veće $\beta_1$ = oštrija odluka |

Koeficijenti se procenjuju metodom **maksimalne verodostojnosti** (maximum likelihood) —
za razliku od linearne regresije, **nema zatvorenog rešenja**.
""")

code(C, r"""
z = np.linspace(-8, 8, 300)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))

for b0 in (-3, 0, 3):
    ax[0].plot(z, 1 / (1 + np.exp(-(b0 + 1 * z))), lw=2, label=f"b0={b0}")
ax[0].set_title("Uticaj $\\beta_0$ — horizontalni pomak"); ax[0].legend()
ax[0].axhline(0.5, color="k", ls=":", lw=1)

for b1 in (0.4, 1, 4):
    ax[1].plot(z, 1 / (1 + np.exp(-(0 + b1 * z))), lw=2, label=f"b1={b1}")
ax[1].set_title("Uticaj $\\beta_1$ — strmina"); ax[1].legend()
ax[1].axhline(0.5, color="k", ls=":", lw=1)

for a in ax: a.set_xlabel("z"); a.set_ylabel("P(Y=1)")
plt.tight_layout(); plt.show()
""")

code(C, r"""
from sklearn.datasets import load_breast_cancer
bc = load_breast_cancer(as_frame=True)
Xb, yb = bc.data, bc.target
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.3, random_state=RS, stratify=yb)

log = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000)).fit(Xtr, ytr)
verov = log.predict_proba(Xte)[:, 1]

print(f"Tacnost: {log.score(Xte, yte):.4f}")
print(f"\nModel vraca VEROVATNOCE, ne klase:")
print(f"   prvih 6 verovatnoca: {verov[:6].round(3)}")
print(f"   klase uz prag 0.5  : {(verov[:6] >= 0.5).astype(int)}")
""")

md(C, r"""
### Prag odlučivanja (threshold)

Logistička regresija daje **verovatnoću**. Da bi se donela odluka o klasi, uvodi se **prag**,
najčešće 0.5:

- ako je $p \geq 0.5$ → klasa 1
- ako je $p < 0.5$ → klasa 0

Prag se može pomerati — time se model čini konzervativnijim ili liberalnijim.
""")

code(C, r"""
redovi = []
for prag in (0.1, 0.3, 0.5, 0.7, 0.9):
    pred = (verov >= prag).astype(int)
    redovi.append({
        "prag": prag,
        "tacnost": round(accuracy_score(yte, pred), 3),
        "preciznost": round(precision_score(yte, pred, zero_division=0), 3),
        "odziv": round(recall_score(yte, pred), 3),
    })
print("Nizi prag = model je 'liberalniji', hvata vise pozitivnih ali gresi vise:")
pd.DataFrame(redovi)
""")

md(C, r"""
## Ocena klasifikatora — matrica konfuzije i metrike

|  | predviđeno 0 | predviđeno 1 |
|---|---|---|
| **stvarno 0** | TN | FP |
| **stvarno 1** | FN | TP |

$$\text{Tačnost} = \frac{TP+TN}{n} \qquad
\text{Preciznost} = \frac{TP}{TP+FP} \qquad
\text{Odziv} = \frac{TP}{TP+FN}$$

$$\text{Specifičnost} = \frac{TN}{FP+TN} \qquad
FPR = \frac{FP}{FP+TN}$$

**ROC kriva** prikazuje kompromis između odziva (TPR) i stope lažno pozitivnih (FPR) pri
različitim pragovima. **AUC** je površina ispod nje i sažima performansu u jedan broj.
""")

code(C, r"""
pred = (verov >= 0.5).astype(int)
cm = confusion_matrix(yte, pred)
tn, fp, fn, tp = cm.ravel()

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ConfusionMatrixDisplay(cm, display_labels=["maligni", "benigni"]).plot(ax=ax[0], colorbar=False, cmap="Blues")
ax[0].set_title("Matrica konfuzije"); ax[0].grid(False)

fpr, tpr, _ = roc_curve(yte, verov)
ax[1].plot(fpr, tpr, lw=2, color="#4C72B0", label=f"AUC = {roc_auc_score(yte, verov):.4f}")
ax[1].plot([0, 1], [0, 1], "k--", label="slucajno pogadjanje")
ax[1].set_xlabel("FPR"); ax[1].set_ylabel("TPR (odziv)"); ax[1].set_title("ROC kriva")
ax[1].legend()
plt.tight_layout(); plt.show()

print(f"TN={tn}  FP={fp}  FN={fn}  TP={tp}")
print(f"Tacnost      = (TP+TN)/n     = {(tp+tn)/cm.sum():.4f}")
print(f"Preciznost   = TP/(TP+FP)    = {tp/(tp+fp):.4f}")
print(f"Odziv        = TP/(TP+FN)    = {tp/(tp+fn):.4f}")
print(f"Specificnost = TN/(FP+TN)    = {tn/(fp+tn):.4f}")
""")

md(C, r"""
## Sažetak

| | linearna regresija | logistička regresija |
|---|---|---|
| cilj | neprekidna vrednost | verovatnoća klase |
| procena parametara | metod najmanjih kvadrata (zatvoreno rešenje) | maksimalna verodostojnost (iterativno) |
| glavne metrike | RSE, $R^2$ | tačnost, preciznost, odziv, AUC |
| **prednost** | jednostavan, koeficijenti se lako tumače | log-odnosi linearni, nema hiperparametara |
| **nedostatak** | osetljiv na outliere, može biti presimplifikovan | ne modeluje složene granice odlučivanja |
""")
upisi(C, "02_regresija.ipynb")

# ═══════════════════════════════════════════════════════ 03 kNN
C = novi()
md(C, r"""
# 3. Algoritam k-najbližih suseda (k-NN)

## Modeli zasnovani na instancama

kNN je **neparametarski** algoritam i spada u **metode zasnovane na instancama**
(memorijske metode).

- sve instance iz trening skupa se čuvaju u memoriji
- **ne postoji eksplicitna faza učenja** — otud naziv *lazy learning*
- predikcija se računa tek kada stigne nova instanca

## Princip rada

1. Izabrati broj suseda $k$
2. Izabrati meru udaljenosti
3. Za novu instancu izračunati udaljenost do **svih** trening instanci
4. Izabrati $k$ najbližih
5. Doneti odluku:
   - **klasifikacija** — većinsko glasanje
   - **regresija** — srednja vrednost (ili ponderisani prosek) suseda

> Osnovna ideja: **slični podaci imaju slične izlaze.** kNN pravi **lokalne** odluke,
> umesto globalnog modela.
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris, make_moons
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42

X, y = make_moons(n_samples=300, noise=0.28, random_state=RS)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=RS, stratify=y)
print(f"Podaci: {X.shape[0]} uzoraka, 2 obelezja, 2 klase")
""")

md(C, r"""
## Izbor parametra $k$

$k$ je **hiperparametar** — određuje koliko suseda učestvuje u odluci i time kontroliše
složenost modela.

| $k$ | granica odlučivanja | bias / varijansa | posledica |
|---|---|---|---|
| **malo** ($k=1$) | vrlo neregularna | **nizak bias, visoka varijansa** | osetljiv na šum, **overfitting** |
| **srednje** ($k \approx 10$) | uravnotežena | dobar kompromis | najbolje |
| **veliko** ($k=50+$) | vrlo glatka | **visok bias, niska varijansa** | gubi lokalnu strukturu, **underfitting** |

Bira se **eksperimentalno** — validacionim skupom ili kros-validacijom. Kod klasifikacije
se često bira **neparan** $k$ da bi se izbegao nerešen ishod pri glasanju.
""")

code(C, r"""
def granica(ax, model, X, y, naslov):
    h = 0.02
    x0, x1 = X[:, 0].min() - .5, X[:, 0].max() + .5
    y0, y1 = X[:, 1].min() - .5, X[:, 1].max() + .5
    xx, yy = np.meshgrid(np.arange(x0, x1, h), np.arange(y0, y1, h))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.25, cmap="coolwarm")
    ax.scatter(X[:, 0], X[:, 1], c=y, s=18, cmap="coolwarm", edgecolor="k", linewidth=0.3)
    ax.set_title(naslov); ax.set_xticks([]); ax.set_yticks([])

fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
for a, k in zip(ax, (1, 5, 25, 100)):
    m = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)
    granica(a, m, Xtr, ytr, f"k = {k}\ntest = {m.score(Xte, yte):.3f}")
plt.tight_layout(); plt.show()
print("k=1  : granica prati svaku tacku -> overfitting")
print("k=100: granica je skoro prava    -> underfitting")
""")

code(C, r"""
ks = range(1, 61, 2)
tr, te = [], []
for k in ks:
    m = KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)
    tr.append(1 - m.score(Xtr, ytr))
    te.append(1 - m.score(Xte, yte))

fig, ax = plt.subplots()
ax.plot(list(ks), tr, "o-", label="trening greska", color="#4C72B0")
ax.plot(list(ks), te, "s-", label="test greska", color="#C44E52")
najbolje = list(ks)[int(np.argmin(te))]
ax.axvline(najbolje, color="#55A868", ls="--", label=f"najbolje k = {najbolje}")
ax.set_xlabel("k"); ax.set_ylabel("greska")
ax.set_title("Greska u zavisnosti od k (bias-variance kompromis)")
ax.legend(); plt.tight_layout(); plt.show()

print("Sa smanjenjem k trening greska kontinuirano opada (k=1 -> greska 0).")
print(f"Test greska ima MINIMUM na srednjem k = {najbolje}, pa raste -> overfitting.")
""")

md(C, r"""
## Mere rastojanja

kNN se zasniva na merenju sličnosti. Najčešće mere:

**Euklidsko rastojanje** (L2) — „pravolinijsko", najčešće korišćeno:

$$d(x, y) = \sqrt{\sum_{i=1}^{n}(x_i - y_i)^2}$$

**Manhattan rastojanje** (L1) — zbir apsolutnih razlika, robusnije na autlajere:

$$d(x, y) = \sum_{i=1}^{n} \lvert x_i - y_i \rvert$$

**Minkowski rastojanje** — opšti oblik:

$$d(x, y) = \left(\sum_{i=1}^{n} \lvert x_i - y_i \rvert^{p}\right)^{1/p}$$

Za $p = 1$ dobija se Manhattan, za $p = 2$ Euklidsko.
""")

code(C, r"""
a = np.array([170, 25]); b = np.array([180, 30])
print(f"Tacka A = {a},  tacka B = {b}\n")
print(f"Euklidsko (p=2) : {np.sqrt(np.sum((a-b)**2)):.4f}")
print(f"Manhattan (p=1) : {np.sum(np.abs(a-b)):.4f}")
for p in (1, 2, 3, 10):
    print(f"Minkowski p={p:<3}: {np.sum(np.abs(a-b)**p)**(1/p):.4f}")
""")

md(C, r"""
## Skaliranje podataka

Euklidsko rastojanje je **osetljivo na skalu**. Atributi sa većim numeričkim vrednostima
dominiraju u računanju rastojanja, čak i ako nisu važniji.

**Primer:** visina u cm (160–190) i godine (20–40).

$$d = \sqrt{(170-180)^2 + (25-30)^2} = \sqrt{100 + 25}$$

Visina doprinosi sa 100, godine sa 25 — **četiri puta veći uticaj**, iako nisu četiri puta
važnije. Rešenje je **skaliranje**.

| metoda | formula | rezultat |
|---|---|---|
| **Standardizacija** (z-score) | $x' = \dfrac{x - \mu}{\sigma}$ | srednja vrednost 0, st. devijacija 1 |
| **Min–Max** | $x' = \dfrac{x - x_{\min}}{x_{\max} - x_{\min}}$ | opseg $[0, 1]$ |
""")

code(C, r"""
osobe = pd.DataFrame({"visina_cm": [170, 180, 175, 165], "godine": [25, 30, 45, 22]})
print("Doprinos svakog atributa kvadratu rastojanja A-B:")
d_v = (osobe.visina_cm[0] - osobe.visina_cm[1]) ** 2
d_g = (osobe.godine[0] - osobe.godine[1]) ** 2
print(f"   visina: {d_v}   godine: {d_g}   -> odnos {d_v/d_g:.1f} : 1\n")

z = StandardScaler().fit_transform(osobe)
mm = MinMaxScaler().fit_transform(osobe)
d_vz = (z[0, 0] - z[1, 0]) ** 2; d_gz = (z[0, 1] - z[1, 1]) ** 2
print(f"Posle standardizacije: visina {d_vz:.3f}, godine {d_gz:.3f} -> odnos {d_vz/d_gz:.2f} : 1")
print("\nz-score:"); display(pd.DataFrame(z, columns=osobe.columns).round(3))
""")

md(C, r"""
### Kada se radi skaliranje — ispravan redosled

1. **Podela** podataka na trening i test
2. Skaliranje se **uči SAMO na trening skupu** (`fit`)
3. Ista transformacija se primenjuje na oba skupa (`transform`)

> **Zašto ne pre podele?** Ako skaliramo pre podele, koristimo informacije iz test skupa
> (njegovu srednju vrednost i devijaciju) → **data leakage** → nerealno dobra tačnost.

Najsigurniji način je `Pipeline`, koji sam pazi na redosled unutar kros-validacije.
""")

code(C, r"""
from sklearn.datasets import load_wine
Xw, yw = load_wine(return_X_y=True)

# POGRESNO — skaliranje pre podele
sc = StandardScaler()
Xw_sve = sc.fit_transform(Xw)                    # koristi i test podatke!
a, b, c, d = train_test_split(Xw_sve, yw, test_size=0.3, random_state=RS, stratify=yw)
lose = KNeighborsClassifier(5).fit(a, c).score(b, d)

# ISPRAVNO — prvo podela, pa fit samo na treningu
a2, b2, c2, d2 = train_test_split(Xw, yw, test_size=0.3, random_state=RS, stratify=yw)
sc2 = StandardScaler().fit(a2)
dobro = KNeighborsClassifier(5).fit(sc2.transform(a2), c2).score(sc2.transform(b2), d2)

# NAJBOLJE — Pipeline
pipe = Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier(5))])
cv = cross_val_score(pipe, Xw, yw, cv=5)

print(f"POGRESNO (fit pre podele) : {lose:.4f}   <- data leakage")
print(f"ISPRAVNO (fit na treningu): {dobro:.4f}")
print(f"PIPELINE + 5-fold CV      : {cv.mean():.4f} +- {cv.std():.4f}")
print(f"\nBez skaliranja uopste     : {KNeighborsClassifier(5).fit(a2, c2).score(b2, d2):.4f}")
""")

md(C, r"""
## Izbor $k$ pomoću kros-validacije
""")

code(C, r"""
mreza = {"knn__n_neighbors": list(range(1, 32, 2)),
         "knn__weights": ["uniform", "distance"],
         "knn__p": [1, 2]}
gs = GridSearchCV(Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier())]),
                  mreza, cv=5, scoring="accuracy", n_jobs=-1).fit(Xw, yw)

print(f"Najbolji parametri : {gs.best_params_}")
print(f"Najbolji CV rezultat: {gs.best_score_:.4f}")
print(f"Isprobano kombinacija: {len(gs.cv_results_['params'])}")
""")

md(C, r"""
## kNN za regresiju

Isti princip, samo se umesto glasanja uzima **prosek** vrednosti $k$ suseda.
""")

code(C, r"""
Xreg = np.sort(np.random.RandomState(RS).uniform(0, 10, 80)).reshape(-1, 1)
yreg = np.sin(Xreg).ravel() + np.random.RandomState(RS).normal(0, 0.2, 80)
xx = np.linspace(0, 10, 400).reshape(-1, 1)

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
for a, k in zip(ax, (1, 5, 30)):
    m = KNeighborsRegressor(n_neighbors=k).fit(Xreg, yreg)
    a.scatter(Xreg, yreg, s=16, color="#4C72B0")
    a.plot(xx, m.predict(xx), color="#C44E52", lw=2)
    a.set_title(f"k = {k}")
plt.tight_layout(); plt.show()
print("k=1: predikcija je stepenasta i prati sum. k=30: preglatka, gubi oblik sinusa.")
""")

md(C, r"""
## Prednosti i nedostaci

**Prednosti**
- jednostavan i intuitivan
- nema fazu treniranja (lazy learning)
- može modelovati **nelinearne** granice odlučivanja
- dobro radi na malim i srednjim skupovima

**Nedostaci**
- **spor u fazi predikcije** — računa rastojanje do svih instanci
- veliki memorijski zahtevi
- osetljiv na izbor $k$, meru rastojanja i **skaliranje**
- slabo se ponaša u visokodimenzionalnom prostoru — **prokletstvo dimenzionalnosti**
""")

code(C, r"""
from sklearn.datasets import make_classification
print("Prokletstvo dimenzionalnosti — samo 5 obelezja je informativno:\n")
print(f"{'dimenzija':>10} {'tacnost':>9}")
for d in (5, 10, 25, 50, 200, 500):
    Xd, yd = make_classification(n_samples=600, n_features=d, n_informative=5,
                                 n_redundant=0, n_repeated=0, random_state=RS)
    s = cross_val_score(Pipeline([("sc", StandardScaler()), ("knn", KNeighborsClassifier(5))]),
                        Xd, yd, cv=5).mean()
    print(f"{d:>10} {s:>9.4f}")
print("\n-> Sa rastom dimenzije sve tacke postaju priblizno jednako udaljene,")
print("   pa pojam 'najblizi sused' gubi smisao.")
""")
upisi(C, "03_knn.ipynb")

print("\nGotovo za 01-03.")
