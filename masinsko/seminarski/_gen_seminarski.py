# -*- coding: utf-8 -*-
"""Generise sablon i biblioteku koda za seminarski."""
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

# ═══════════════════════════════════════════ ŠABLON
C = novi()
md(C, r"""
# [NASLOV PROJEKTA]

**Seminarski rad iz predmeta Mašinsko učenje**

Ime i prezime · broj indeksa · datum

---

> **Uputstvo za korišćenje ovog šablona**
>
> Poglavlja odgovaraju **tačkama iz pravila ispita**, jedan na jedan. Svako poglavlje ima
> kratko objašnjenje šta se traži i `TODO` ćelije koje treba popuniti.
>
> Kada završiš, **obriši sve `TODO` komentare i ovaj okvir**.
>
> Gotovi isečci koda za svaku fazu su u `biblioteka_koda.ipynb`.

## Pravila ispita

Projekat treba da obuhvata:

| # | zahtev | poglavlje |
|---|---|---|
| 1 | odabir odgovarajućeg dataset-a | **2** |
| 2 | definisanje problema | **1** |
| 3 | preprocesiranje podataka | **4** |
| 4 | treniranje više modela mašinskog učenja po izboru | **5** |
| 5 | evaluaciju i poređenje rezultata modela | **6** |
| 6 | interpretaciju modela i dobijenih rezultata | **7** |
""")

md(C, r"""
---
# 1. Definisanje problema

**Šta se traži:** jasno reći **šta se predviđa**, iz **čega**, i **kako se meri uspeh**.

Najkraći način da se to uradi je formulacija po Mitchell-u (predavanje 01).

> **TODO** — popuni tabelu i dva pasusa ispod.

| | |
|---|---|
| **Zadatak (Z)** | *šta model treba da uradi* |
| **Iskustvo (I)** | *koji podaci, koliko uzoraka* |
| **Performanse (P)** | *koja metrika i zašto baš ona* |

**Tip problema:** *klasifikacija / regresija / klasterovanje*

**Zašto je ovo problem mašinskog učenja**

*Objasni zašto se pravilo ne može napisati eksplicitno, nego se mora naučiti iz podataka.
Ako se problem može rešiti jednim `if`-om, nije dobra tema.*

**Zašto je problem zanimljiv**

*Kome bi rezultat koristio i šta bi se s njim moglo uraditi.*
""")

md(C, r"""
---
# 2. Odabir dataset-a

**Šta se traži:** opisati odakle podaci dolaze, koliko ih ima i šta predstavljaju.

> **TODO** — popuni opis i tabelu obeležja.

**Izvor:** *link ili opis (Kaggle, UCI, sopstveno prikupljanje, API...)*

**Zašto baš ovaj skup:** *veza sa problemom iz poglavlja 1*
""")

code(C, r"""
# TODO: podesi importe prema onome sto koristis
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["figure.figsize"] = (9, 4.5)
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3
RS = 42                      # jedan seed kroz ceo rad — zbog ponovljivosti
np.random.seed(RS)
""")

code(C, r"""
# TODO: ucitaj svoj skup
# df = pd.read_csv("data/tvoj_skup.csv")

print(f"Oblik: {df.shape[0]} redova x {df.shape[1]} kolona")
df.head()
""")

code(C, r"""
# TODO: opis obelezja — sta koja kolona znaci
print(df.info())
print("\nOsnovna statistika:")
df.describe().T
""")

md(C, r"""
---
# 3. Istraživačka analiza podataka (EDA)

**Nije eksplicitno u pravilima, ali se podrazumeva** — bez nje se ne može opravdati nijedna
odluka u preprocesiranju.

Obavezno pokazati:

- **raspodelu ciljne promenljive** — ovo određuje koje metrike smeš da koristiš
- nedostajuće vrednosti
- korelacije između obeležja
- 2–3 grafika koja nešto **stvarno pokazuju**, ne ukras

> **TODO** — dopuni analizu prema svom skupu.
""")

code(C, r"""
# TODO: zameni "ciljna" imenom svoje ciljne kolone
CILJ = "ciljna"

print("Raspodela ciljne promenljive:")
print(df[CILJ].value_counts())
print(f"\nUdeo manjinske klase: {df[CILJ].value_counts(normalize=True).min():.1%}")

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
df[CILJ].value_counts().plot.bar(ax=ax[0], rot=0, color="#4C72B0")
ax[0].set_title("Raspodela klasa")
df.isna().sum().sort_values(ascending=False).head(10).plot.barh(ax=ax[1], color="#C44E52")
ax[1].set_title("Nedostajuce vrednosti (10 najgorih)")
plt.tight_layout(); plt.show()
""")

code(C, r"""
# korelaciona matrica
num = df.select_dtypes(include=[np.number])
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(num.corr(), cmap="RdBu_r", center=0, square=True,
            linewidths=.5, cbar_kws={"shrink": .7}, ax=ax)
ax.set_title("Korelaciona matrica")
plt.tight_layout(); plt.show()
""")

md(C, r"""
### Zaključci iz EDA

> **TODO** — u 3–5 rečenica: šta si video i **kako to utiče na naredne korake**.
> Npr. „klase su neuravnotežene 90:10, pa tačnost nije upotrebljiva metrika" ili
> „tri obeležja su međusobno korelisana preko 0.9, pa razmatram PCA".
""")

md(C, r"""
---
# 4. Preprocesiranje podataka

**Šta se traži:** pripremiti podatke i **obrazložiti svaku odluku**.

Tipični koraci:

| korak | kada je potreban |
|---|---|
| **podela na train/test** | uvek, **pre** svega ostalog |
| nedostajuće vrednosti | ako ih ima |
| kodiranje kategoričkih | ako ima tekstualnih kolona (`get_dummies`, `OneHotEncoder`) |
| **skaliranje** | obavezno za kNN, SVM, neuronske mreže, PCA |
| balansiranje klasa | ako su klase jako neuravnotežene |

> **Najvažnije pravilo:** sve što se **uči** iz podataka (skaler, imputer, PCA, kodiranje)
> mora se naučiti **samo na trening skupu**, pa primeniti na test.
> Najsigurnije je koristiti `Pipeline`.

> **TODO** — sprovedi korake koje tvoj skup traži i **napiši zašto**.
""")

code(C, r"""
from sklearn.model_selection import train_test_split

X = df.drop(columns=[CILJ])
y = df[CILJ]

Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, random_state=RS,
    stratify=y            # TODO: izbaci ako je regresija
)
print(f"Trening: {Xtr.shape[0]} uzoraka")
print(f"Test   : {Xte.shape[0]} uzoraka")
print(f"\nRaspodela klasa — trening: {np.bincount(ytr).tolist()}")
print(f"Raspodela klasa — test   : {np.bincount(yte).tolist()}")
""")

code(C, r"""
# TODO: preprocesiranje kroz Pipeline — sam pazi na redosled i sprecava leakage
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

numericke = X.select_dtypes(include=[np.number]).columns.tolist()
kategoricke = X.select_dtypes(exclude=[np.number]).columns.tolist()
print(f"Numerickih obelezja  : {len(numericke)}")
print(f"Kategorickih obelezja: {len(kategoricke)}")

priprema = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc", StandardScaler())]), numericke),
    ("kat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                      ("oh", OneHotEncoder(handle_unknown="ignore"))]), kategoricke),
])
""")

md(C, r"""
### Obrazloženje odluka u preprocesiranju

> **TODO** — za svaki korak napiši **zašto** si ga primenio.
> Npr. „nedostajuće vrednosti popunjene medijanom jer je raspodela iskošena";
> „skaliranje je obavezno jer koristim kNN i SVM koji se oslanjaju na rastojanja".
""")

md(C, r"""
---
# 5. Treniranje više modela

**Šta se traži:** obučiti **više** modela i uporediti ih.

Preporuka: **5–8 modela**, iz različitih porodica, plus **bazni model**.

| porodica | modeli | predavanje |
|---|---|---|
| bazni | `DummyClassifier` | 07 |
| linearni | logistička / linearna regresija | 02 |
| instance-based | kNN | 03 |
| stabla | `DecisionTree` | 04 |
| probabilistički | `GaussianNB` | 05 |
| margine | SVM | 06 |
| ansambli | RandomForest, XGBoost, Voting, Stacking | 12 |
| duboko učenje | MLP | 10 |

> **Bazni model je obavezan.** Bez njega se ne zna šta je „loše" — 90% tačnosti ne znači
> ništa ako 90% uzoraka pripada jednoj klasi.

> **TODO** — izaberi modele i obuči ih **istim postupkom**, da poređenje bude pošteno.
""")

code(C, r"""
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold

cv = StratifiedKFold(5, shuffle=True, random_state=RS)

MODELI = {
    "Dummy (bazni)":        DummyClassifier(strategy="most_frequent"),
    "Logisticka regresija": LogisticRegression(max_iter=3000, random_state=RS),
    "kNN":                  KNeighborsClassifier(),
    "Stablo odlucivanja":   DecisionTreeClassifier(max_depth=5, random_state=RS),
    "Naivni Bajes":         GaussianNB(),
    "SVM (RBF)":            SVC(probability=True, random_state=RS),
    "Random Forest":        RandomForestClassifier(n_estimators=300, random_state=RS, n_jobs=-1),
}
# TODO: dodaj XGBoost / MLP / Voting / Stacking ako zelis
""")

code(C, r"""
rezultati = {}
modeli_fit = {}

for ime, model in MODELI.items():
    pipe = Pipeline([("prep", priprema), ("m", model)])
    cv_skor = cross_val_score(pipe, Xtr, ytr, cv=cv, scoring="accuracy", n_jobs=-1)
    pipe.fit(Xtr, ytr)
    modeli_fit[ime] = pipe
    rezultati[ime] = {"cv_prosek": cv_skor.mean(), "cv_std": cv_skor.std()}
    print(f"{ime:<24} CV = {cv_skor.mean():.4f} +- {cv_skor.std():.4f}")
""")

md(C, r"""
### Podešavanje hiperparametara

> **TODO** — podesi hiperparametre bar jednog modela pomoću `GridSearchCV`, i **prikaži
> koliko je to pomoglo**. Ovo pokriva deo gradiva sa predavanja 07.
""")

code(C, r"""
from sklearn.model_selection import GridSearchCV

# TODO: prilagodi mrezu svom modelu
mreza = {
    "m__n_estimators": [100, 300],
    "m__max_depth": [5, 10, None],
    "m__min_samples_leaf": [1, 5],
}
gs = GridSearchCV(Pipeline([("prep", priprema),
                            ("m", RandomForestClassifier(random_state=RS, n_jobs=-1))]),
                  mreza, cv=cv, scoring="accuracy", n_jobs=-1)
gs.fit(Xtr, ytr)

print(f"Najbolji parametri : {gs.best_params_}")
print(f"Najbolji CV rezultat: {gs.best_score_:.4f}")
print(f"Isprobano kombinacija: {len(gs.cv_results_['params'])}")

modeli_fit["Random Forest (podesen)"] = gs.best_estimator_
rezultati["Random Forest (podesen)"] = {"cv_prosek": gs.best_score_, "cv_std": 0.0}
""")

md(C, r"""
---
# 6. Evaluacija i poređenje rezultata

**Šta se traži:** uporediti modele **istim metrikama** i prikazati rezultate pregledno.

> **Izbor metrike zavisi od raspodele klasa.** Ako su neuravnotežene, tačnost vara —
> koristi F1, balanced accuracy, ROC-AUC ili PR-AUC.

Obavezno prikazati:
- **zbirnu tabelu** svih modela
- **matricu konfuzije** najboljeg modela
- bar jednu **krivu** (ROC ili PR)

> **TODO** — dopuni evaluaciju.
""")

code(C, r"""
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             balanced_accuracy_score, roc_auc_score, confusion_matrix,
                             ConfusionMatrixDisplay, roc_curve, classification_report)

redovi = []
for ime, pipe in modeli_fit.items():
    pred = pipe.predict(Xte)
    red = {
        "model": ime,
        "CV": round(rezultati[ime]["cv_prosek"], 4),
        "tacnost": round(accuracy_score(yte, pred), 4),
        "balanced_acc": round(balanced_accuracy_score(yte, pred), 4),
        "preciznost": round(precision_score(yte, pred, average="weighted", zero_division=0), 4),
        "odziv": round(recall_score(yte, pred, average="weighted"), 4),
        "F1": round(f1_score(yte, pred, average="weighted"), 4),
    }
    if hasattr(pipe, "predict_proba") and len(np.unique(yte)) == 2:
        red["ROC-AUC"] = round(roc_auc_score(yte, pipe.predict_proba(Xte)[:, 1]), 4)
    redovi.append(red)

tabela = pd.DataFrame(redovi).sort_values("F1", ascending=False).reset_index(drop=True)
display(tabela)
""")

code(C, r"""
fig, ax = plt.subplots(figsize=(9, 5))
t = tabela.set_index("model")["F1"].sort_values()
boje = ["#C44E52" if "Dummy" in i else "#4C72B0" for i in t.index]
t.plot.barh(ax=ax, color=boje)
ax.set_xlabel("F1 (weighted)"); ax.set_title("Poredjenje modela")
plt.tight_layout(); plt.show()
""")

code(C, r"""
najbolji = tabela.model.iloc[0]
pipe = modeli_fit[najbolji]
pred = pipe.predict(Xte)

fig, ax = plt.subplots(figsize=(5.5, 4.5))
ConfusionMatrixDisplay(confusion_matrix(yte, pred)).plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title(f"Matrica konfuzije — {najbolji}"); ax.grid(False)
plt.tight_layout(); plt.show()

print(f"NAJBOLJI MODEL: {najbolji}\n")
print(classification_report(yte, pred, digits=4))
""")

md(C, r"""
### Diskusija rezultata

> **TODO** — odgovori na pitanja:
> - Koji model je najbolji i **za koliko** je bolji od baznog?
> - **Zašto** baš taj tip modela radi najbolje na ovim podacima?
> - Da li se neki model ponaša neočekivano loše i zašto? *(npr. naivni Bajes ako su
>   obeležja korelisana — pretpostavka uslovne nezavisnosti je narušena)*
> - Da li je razlika između top modela **stvarna** ili u granicama standardne devijacije CV-a?
""")

md(C, r"""
---
# 7. Interpretacija modela i rezultata

**Šta se traži:** objasniti **zašto** model donosi odluke koje donosi.

Preporuka — bar dve metode:

| metoda | tip | predavanje |
|---|---|---|
| koeficijenti / `feature_importances_` | model-specifična | 02, 12 |
| **permutaciona važnost** | model-agnostička | 13 |
| **SHAP** | model-agnostička | 13 |
| PDP / ICE | model-agnostička | 13 |

> **TODO** — primeni bar dve metode i **protumači** rezultat rečima.
""")

code(C, r"""
from sklearn.inspection import permutation_importance

pi = permutation_importance(pipe, Xte, yte, n_repeats=10,
                            random_state=RS, scoring="f1_weighted", n_jobs=-1)
vazn = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 5))
vazn.head(12)[::-1].plot.barh(ax=ax, color="#4C72B0")
ax.set_xlabel("pad F1 pri mesanju obelezja")
ax.set_title("Permutaciona vaznost")
plt.tight_layout(); plt.show()
""")

code(C, r"""
# SHAP — radi najbrze nad modelima zasnovanim na stablima (TreeExplainer)
import shap

# TODO: prilagodi ako tvoj najbolji model nije zasnovan na stablima
model_bez_pipe = pipe.named_steps["m"]
X_prep = pipe.named_steps["prep"].transform(Xte)
if hasattr(X_prep, "toarray"):
    X_prep = X_prep.toarray()

try:
    expl = shap.TreeExplainer(model_bez_pipe)
    sv = expl.shap_values(X_prep)
    if isinstance(sv, list):
        sv = sv[1]
    shap.summary_plot(sv, X_prep, max_display=12, show=False)
    plt.title("SHAP — globalni pregled", pad=18)
    plt.tight_layout(); plt.show()
except Exception as e:
    print(f"TreeExplainer nije primenljiv ({type(e).__name__}).")
    print("Koristi shap.KernelExplainer ili shap.Explainer za druge tipove modela.")
""")

md(C, r"""
### Tumačenje

> **TODO** — u nekoliko rečenica:
> - Koja obeležja model najviše koristi?
> - Da li to ima **smisla u domenu**? Ako obeležje koje nema veze sa problemom ispadne
>   najvažnije, to je često znak **curenja informacija**.
> - Slažu li se različite metode interpretacije međusobno?
> - **Oprez:** SHAP objašnjava **model**, ne stvarnost. Korelacija nije uzročnost.
""")

md(C, r"""
---
# 8. Zaključak

> **TODO** — sažmi rad u nekoliko pasusa.

**Šta je urađeno** — problem, podaci, modeli, rezultat u jednoj rečenici.

**Glavni nalazi** — 3–4 tačke; brojevi, ne uopštene tvrdnje.

**Ograničenja** — navedi ih sam, pre nego što ih neko pita:
- veličina i reprezentativnost uzorka
- da li su podaci iz jednog izvora / perioda
- korelacija nije uzročnost
- šta model ne može

**Mogući nastavak** — šta bi sledeće uradio da imaš više vremena ili podataka.
""")
upisi(C, "seminarski_sablon.ipynb")

# ═══════════════════════════════════════════ BIBLIOTEKA KODA
C = novi()
md(C, r"""
# Biblioteka koda za seminarski

Gotovi isečci za svaku fazu projekta. **Nije za pokretanje redom** — kopiraj ono što ti
treba u svoj rad.

| poglavlje | tema |
|---|---|
| 1 | Učitavanje i prvi pregled |
| 2 | Istraživačka analiza |
| 3 | Preprocesiranje |
| 4 | Treniranje više modela odjednom |
| 5 | Podešavanje hiperparametara |
| 6 | Evaluacija i poređenje |
| 7 | Interpretacija |
| 8 | Neuravnotežene klase |
| 9 | Regresija |
""")

code(C, r"""
# ═══ ZAJEDNICKI IMPORTI ═══
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42
np.random.seed(RS)
print("Spremno.")
""")

md(C, "## 1. Učitavanje i prvi pregled")
code(C, r"""
# --- CSV ---
# df = pd.read_csv("data/skup.csv")
# df = pd.read_csv("data/skup.csv", sep=";", decimal=",", encoding="utf-8")

# --- Excel ---
# df = pd.read_excel("data/skup.xlsx", sheet_name=0)

# --- JSON ---
# df = pd.read_json("data/skup.json")

# --- ugradjeni skupovi iz sklearn-a (za probu) ---
from sklearn.datasets import load_breast_cancer, load_wine, load_iris, fetch_california_housing
d = load_breast_cancer(as_frame=True)
df = d.frame

def pregled(df, cilj=None):
    'Brzi pregled skupa — pokrenuti odmah posle ucitavanja.'
    print(f"Oblik: {df.shape[0]:,} redova x {df.shape[1]} kolona")
    print(f"Duplikata: {df.duplicated().sum()}")
    print(f"Memorija: {df.memory_usage(deep=True).sum()/1024**2:.1f} MB")
    nedostaje = df.isna().sum()
    if nedostaje.any():
        print(f"\nNedostajuce vrednosti:\n{nedostaje[nedostaje > 0].to_string()}")
    else:
        print("\nNema nedostajucih vrednosti.")
    print(f"\nTipovi:\n{df.dtypes.value_counts().to_string()}")
    if cilj:
        print(f"\nCiljna promenljiva '{cilj}':\n{df[cilj].value_counts().to_string()}")

pregled(df, cilj="target")
""")

md(C, "## 2. Istraživačka analiza")
code(C, r"""
CILJ = "target"

# raspodela ciljne + nedostajuce
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
df[CILJ].value_counts().plot.bar(ax=ax[0], rot=0, color="#4C72B0")
ax[0].set_title("Raspodela ciljne promenljive")
df.isna().sum().sort_values(ascending=False).head(10).plot.barh(ax=ax[1], color="#C44E52")
ax[1].set_title("Nedostajuce vrednosti")
plt.tight_layout(); plt.show()
""")

code(C, r"""
# korelaciona matrica + najjace korelacije sa ciljem
num = df.select_dtypes(include=[np.number])
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(num.corr(), cmap="RdBu_r", center=0, square=True, linewidths=.4,
            cbar_kws={"shrink": .7}, ax=ax)
plt.tight_layout(); plt.show()

k = num.drop(columns=[CILJ]).corrwith(df[CILJ]).sort_values(key=abs, ascending=False)
print("Najjace korelacije sa ciljem:")
print(k.head(8).round(3).to_string())
""")

code(C, r"""
# raspodele obelezja po klasama
obelezja = num.drop(columns=[CILJ]).columns[:6]
fig, ax = plt.subplots(2, 3, figsize=(14, 6))
for a, f in zip(ax.ravel(), obelezja):
    for klasa in sorted(df[CILJ].unique()):
        a.hist(df[df[CILJ] == klasa][f], bins=25, alpha=0.55, label=f"klasa {klasa}")
    a.set_title(f, fontsize=9); a.legend(fontsize=7)
plt.tight_layout(); plt.show()
""")

md(C, "## 3. Preprocesiranje")
code(C, r"""
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer

X = df.drop(columns=[CILJ]); y = df[CILJ]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=RS, stratify=y)

numericke = X.select_dtypes(include=[np.number]).columns.tolist()
kategoricke = X.select_dtypes(exclude=[np.number]).columns.tolist()

priprema = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                      ("sc", StandardScaler())]), numericke),
    ("kat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                      ("oh", OneHotEncoder(handle_unknown="ignore"))]), kategoricke),
])
print(f"Numerickih: {len(numericke)}, kategorickih: {len(kategoricke)}")
""")

code(C, r"""
# --- PCA kao deo pripreme (ako ima mnogo korelisanih obelezja) ---
from sklearn.decomposition import PCA
priprema_pca = Pipeline([("prep", priprema), ("pca", PCA(n_components=0.95))])

# --- ako su podaci GRUPISANI (vise redova iz istog izvora) ---
from sklearn.model_selection import GroupShuffleSplit, GroupKFold
# gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RS)
# tr_idx, te_idx = next(gss.split(X, y, groups=df["id_grupe"]))
""")

md(C, "## 4. Treniranje više modela odjednom")
code(C, r"""
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier,
                              VotingClassifier, StackingClassifier)
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from xgboost import XGBClassifier

cv = StratifiedKFold(5, shuffle=True, random_state=RS)

MODELI = {
    "Dummy (bazni)":        DummyClassifier(strategy="most_frequent"),
    "Logisticka regresija": LogisticRegression(max_iter=3000, random_state=RS),
    "kNN":                  KNeighborsClassifier(),
    "Stablo":               DecisionTreeClassifier(max_depth=5, random_state=RS),
    "Naivni Bajes":         GaussianNB(),
    "SVM (RBF)":            SVC(probability=True, random_state=RS),
    "Random Forest":        RandomForestClassifier(n_estimators=300, random_state=RS, n_jobs=-1),
    "XGBoost":              XGBClassifier(eval_metric="logloss", random_state=RS, n_jobs=-1),
    "MLP":                  MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000,
                                          early_stopping=True, random_state=RS),
}

rezultati, modeli_fit = {}, {}
for ime, m in MODELI.items():
    pipe = Pipeline([("prep", priprema), ("m", m)])
    s = cross_val_score(pipe, Xtr, ytr, cv=cv, scoring="f1_weighted", n_jobs=-1)
    pipe.fit(Xtr, ytr)
    modeli_fit[ime] = pipe
    rezultati[ime] = {"cv": s.mean(), "std": s.std()}
    print(f"{ime:<24} CV F1 = {s.mean():.4f} +- {s.std():.4f}")
""")

code(C, r"""
# --- ansambli nad najboljim modelima ---
bazni = [("lr", Pipeline([("prep", priprema), ("m", LogisticRegression(max_iter=3000))])),
         ("rf", Pipeline([("prep", priprema), ("m", RandomForestClassifier(n_estimators=200, random_state=RS))])),
         ("xgb", Pipeline([("prep", priprema), ("m", XGBClassifier(eval_metric="logloss", random_state=RS))]))]

for ime, m in [("Voting (soft)", VotingClassifier(bazni, voting="soft", n_jobs=-1)),
               ("Stacking", StackingClassifier(bazni, final_estimator=LogisticRegression(max_iter=2000),
                                               cv=5, n_jobs=-1))]:
    s = cross_val_score(m, Xtr, ytr, cv=cv, scoring="f1_weighted", n_jobs=-1)
    m.fit(Xtr, ytr)
    modeli_fit[ime] = m
    rezultati[ime] = {"cv": s.mean(), "std": s.std()}
    print(f"{ime:<24} CV F1 = {s.mean():.4f} +- {s.std():.4f}")
""")

md(C, "## 5. Podešavanje hiperparametara")
code(C, r"""
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

MREZE = {
    "RandomForest": {"m__n_estimators": [100, 300, 500],
                     "m__max_depth": [5, 10, 20, None],
                     "m__min_samples_leaf": [1, 3, 5]},
    "XGBoost":      {"m__n_estimators": [200, 400],
                     "m__max_depth": [3, 4, 6],
                     "m__learning_rate": [0.05, 0.1],
                     "m__subsample": [0.8, 1.0]},
    "SVM":          {"m__C": [0.1, 1, 10, 100],
                     "m__gamma": ["scale", 0.01, 0.1]},
    "kNN":          {"m__n_neighbors": list(range(3, 32, 2)),
                     "m__weights": ["uniform", "distance"],
                     "m__p": [1, 2]},
}

gs = GridSearchCV(Pipeline([("prep", priprema),
                            ("m", RandomForestClassifier(random_state=RS, n_jobs=-1))]),
                  MREZE["RandomForest"], cv=cv, scoring="f1_weighted", n_jobs=-1)
gs.fit(Xtr, ytr)
print(f"Najbolji: {gs.best_params_}")
print(f"CV: {gs.best_score_:.4f}")

# pregled najboljih kombinacija
pd.DataFrame(gs.cv_results_)[["params", "mean_test_score", "std_test_score", "rank_test_score"]] \
    .sort_values("rank_test_score").head(8)
""")

code(C, r"""
# kriva validacije — kako jedan hiperparametar utice
from sklearn.model_selection import validation_curve
opseg = [1, 2, 3, 5, 8, 12, 20, None]
tr, te = validation_curve(Pipeline([("prep", priprema), ("m", DecisionTreeClassifier(random_state=RS))]),
                          Xtr, ytr, param_name="m__max_depth", param_range=opseg,
                          cv=cv, scoring="f1_weighted", n_jobs=-1)
x = [d if d else 25 for d in opseg]
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, tr.mean(1), "o-", label="trening", color="#4C72B0")
ax.plot(x, te.mean(1), "s-", label="validacija", color="#C44E52")
ax.set_xlabel("max_depth"); ax.set_ylabel("F1"); ax.legend()
ax.set_title("Kriva validacije")
plt.tight_layout(); plt.show()
""")

md(C, "## 6. Evaluacija i poređenje")
code(C, r"""
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, precision_score,
                             recall_score, f1_score, roc_auc_score, average_precision_score,
                             confusion_matrix, ConfusionMatrixDisplay, classification_report,
                             roc_curve, precision_recall_curve)

def oceni_sve(modeli_fit, Xte, yte, rezultati=None):
    'Zbirna tabela svih modela.'
    binarno = len(np.unique(yte)) == 2
    redovi = []
    for ime, m in modeli_fit.items():
        p = m.predict(Xte)
        r = {"model": ime,
             "tacnost": accuracy_score(yte, p),
             "balanced_acc": balanced_accuracy_score(yte, p),
             "preciznost": precision_score(yte, p, average="weighted", zero_division=0),
             "odziv": recall_score(yte, p, average="weighted"),
             "F1": f1_score(yte, p, average="weighted")}
        if rezultati and ime in rezultati:
            r["CV"] = rezultati[ime]["cv"]
        if binarno and hasattr(m, "predict_proba"):
            pr = m.predict_proba(Xte)[:, 1]
            r["ROC-AUC"] = roc_auc_score(yte, pr)
            r["PR-AUC"] = average_precision_score(yte, pr)
        redovi.append(r)
    return pd.DataFrame(redovi).sort_values("F1", ascending=False).round(4).reset_index(drop=True)

tabela = oceni_sve(modeli_fit, Xte, yte, rezultati)
display(tabela)
""")

code(C, r"""
# ROC i PR krive za sve modele
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for ime, m in modeli_fit.items():
    if not hasattr(m, "predict_proba") or "Dummy" in ime:
        continue
    p = m.predict_proba(Xte)[:, 1]
    fpr, tpr, _ = roc_curve(yte, p)
    ax[0].plot(fpr, tpr, lw=1.4, label=f"{ime} ({roc_auc_score(yte, p):.3f})")
    pre, rec, _ = precision_recall_curve(yte, p)
    ax[1].plot(rec, pre, lw=1.4, label=f"{ime} ({average_precision_score(yte, p):.3f})")
ax[0].plot([0,1],[0,1],"k--"); ax[0].set_title("ROC krive")
ax[0].set_xlabel("FPR"); ax[0].set_ylabel("TPR"); ax[0].legend(fontsize=7)
ax[1].axhline(yte.mean(), color="k", ls="--")
ax[1].set_title("PR krive"); ax[1].set_xlabel("odziv"); ax[1].set_ylabel("preciznost")
ax[1].legend(fontsize=7)
plt.tight_layout(); plt.show()
""")

code(C, r"""
# matrica konfuzije + izvestaj za najbolji model
najbolji = tabela.model.iloc[0]
m = modeli_fit[najbolji]; p = m.predict(Xte)

fig, ax = plt.subplots(figsize=(5.5, 4.5))
ConfusionMatrixDisplay(confusion_matrix(yte, p)).plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title(f"Matrica konfuzije — {najbolji}"); ax.grid(False)
plt.tight_layout(); plt.show()
print(classification_report(yte, p, digits=4))
""")

code(C, r"""
# kriva ucenja — da li treba vise podataka
from sklearn.model_selection import learning_curve
n, tr, te = learning_curve(modeli_fit[najbolji], Xtr, ytr, cv=cv, n_jobs=-1,
                           train_sizes=np.linspace(0.1, 1.0, 8), scoring="f1_weighted")
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(n, tr.mean(1), "o-", label="trening", color="#4C72B0")
ax.plot(n, te.mean(1), "s-", label="validacija", color="#C44E52")
ax.fill_between(n, te.mean(1)-te.std(1), te.mean(1)+te.std(1), alpha=0.15, color="#C44E52")
ax.set_xlabel("broj trening uzoraka"); ax.set_ylabel("F1"); ax.legend()
ax.set_title("Kriva ucenja")
plt.tight_layout(); plt.show()
""")

md(C, "## 7. Interpretacija")
code(C, r"""
from sklearn.inspection import permutation_importance, PartialDependenceDisplay

pi = permutation_importance(modeli_fit[najbolji], Xte, yte, n_repeats=10,
                            random_state=RS, scoring="f1_weighted", n_jobs=-1)
vazn = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 5))
vazn.head(12)[::-1].plot.barh(ax=ax, color="#4C72B0")
ax.set_xlabel("pad F1"); ax.set_title("Permutaciona vaznost")
plt.tight_layout(); plt.show()
""")

code(C, r"""
import shap

# --- za modele zasnovane na stablima (najbrze) ---
model_ciste = RandomForestClassifier(n_estimators=300, random_state=RS, n_jobs=-1)
Xtr_p = priprema.fit_transform(Xtr); Xte_p = priprema.transform(Xte)
if hasattr(Xtr_p, "toarray"): Xtr_p, Xte_p = Xtr_p.toarray(), Xte_p.toarray()
model_ciste.fit(Xtr_p, ytr)

expl = shap.TreeExplainer(model_ciste)
sv = expl.shap_values(Xte_p)
if isinstance(sv, list): sv = sv[1]
elif sv.ndim == 3: sv = sv[:, :, 1]

shap.summary_plot(sv, Xte_p, feature_names=list(X.columns), max_display=12, show=False)
plt.title("SHAP — globalni pregled", pad=18); plt.tight_layout(); plt.show()
""")

code(C, r"""
# SHAP za JEDNU predikciju (waterfall)
i = 0
shap.plots._waterfall.waterfall_legacy(
    expl.expected_value[1] if isinstance(expl.expected_value, np.ndarray) else expl.expected_value,
    sv[i], Xte.iloc[i], max_display=10, show=False)
plt.title(f"Objasnjenje predikcije za uzorak {i}", pad=18)
plt.tight_layout(); plt.show()
""")

code(C, r"""
# PDP za 3 najvaznija obelezja
top3 = [list(X.columns).index(f) for f in vazn.head(3).index]
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
PartialDependenceDisplay.from_estimator(modeli_fit[najbolji], Xte, vazn.head(3).index.tolist(), ax=ax)
plt.tight_layout(); plt.show()
""")

md(C, "## 8. Neuravnotežene klase")
code(C, r"""
# 1. class_weight="balanced" — najjednostavnije
LogisticRegression(class_weight="balanced", max_iter=3000)
RandomForestClassifier(class_weight="balanced", n_estimators=300)
SVC(class_weight="balanced")

# 2. scale_pos_weight za XGBoost
spw = (ytr == 0).sum() / (ytr == 1).sum()
XGBClassifier(scale_pos_weight=spw, eval_metric="logloss")

# 3. izbor praga na VALIDACIONOM skupu (nikad na test!)
def najbolji_prag(y_val, p_val):
    'Prag koji maksimizuje F1 na validacionom skupu.'
    pre, rec, prag = precision_recall_curve(y_val, p_val)
    f1 = 2 * pre * rec / np.clip(pre + rec, 1e-9, None)
    return prag[int(np.argmax(f1[:-1]))] if len(prag) else 0.5

# 4. metrike koje NE varaju kod neuravnotezenih klasa:
#    balanced_accuracy_score, f1_score, average_precision_score (PR-AUC)
print(f"scale_pos_weight = {spw:.2f}")
""")

md(C, "## 9. Regresija")
code(C, r"""
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

MODELI_REG = {
    "Dummy (prosek)":  DummyRegressor(strategy="mean"),
    "Linearna":        LinearRegression(),
    "Ridge":           Ridge(alpha=1.0),
    "Lasso":           Lasso(alpha=0.01),
    "Stablo":          DecisionTreeRegressor(max_depth=6, random_state=RS),
    "Random Forest":   RandomForestRegressor(n_estimators=300, random_state=RS, n_jobs=-1),
    "SVR":             SVR(),
    "XGBoost":         XGBRegressor(n_estimators=300, random_state=RS, n_jobs=-1),
}

def oceni_regresiju(modeli, Xtr, ytr, Xte, yte, priprema):
    redovi = []
    for ime, m in modeli.items():
        pipe = Pipeline([("prep", priprema), ("m", m)]).fit(Xtr, ytr)
        p = pipe.predict(Xte)
        redovi.append({"model": ime,
                       "RMSE": np.sqrt(mean_squared_error(yte, p)),
                       "MAE": mean_absolute_error(yte, p),
                       "R2": r2_score(yte, p)})
    return pd.DataFrame(redovi).sort_values("R2", ascending=False).round(4).reset_index(drop=True)

print("Koristi ovako:")
print("  tabela = oceni_regresiju(MODELI_REG, Xtr, ytr, Xte, yte, priprema)")
""")

code(C, r"""
# log-transformacija ako je ciljna promenljiva iskosena
# y_log = np.log1p(y)
# ... treniraj na y_log ...
# pred = np.expm1(model.predict(Xte))       # vrati u originalnu skalu

# grafik stvarno vs predvidjeno + reziduali
def dijagnostika_regresije(yte, pred):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].scatter(yte, pred, s=14, alpha=0.6, color="#4C72B0")
    lims = [min(yte.min(), pred.min()), max(yte.max(), pred.max())]
    ax[0].plot(lims, lims, "k--")
    ax[0].set_xlabel("stvarno"); ax[0].set_ylabel("predvidjeno")
    ax[0].set_title("Stvarno vs predvidjeno")
    ax[1].scatter(pred, yte - pred, s=14, alpha=0.6, color="#C44E52")
    ax[1].axhline(0, color="k")
    ax[1].set_xlabel("predvidjeno"); ax[1].set_ylabel("rezidual")
    ax[1].set_title("Grafik reziduala — obrazac znaci problem")
    plt.tight_layout(); plt.show()

print("dijagnostika_regresije(yte, pred)")
""")
upisi(C, "biblioteka_koda.ipynb")
