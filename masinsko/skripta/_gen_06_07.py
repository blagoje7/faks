# -*- coding: utf-8 -*-
"""Generise notebook-e 06-07 skripte iz Masinskog ucenja."""
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

# ═══════════════════════════════════════════════════════ 06 SVM
C = novi()
md(C, r"""
# 6. Mehanizam potpornih vektora (SVM)

## Osnovna ideja

Support Vector Machine traži razdvajajuću **hiperravan** koja **maksimizuje marginu**
između dve klase.

$$w \cdot x + b = 0$$

| pojam | značenje |
|---|---|
| **hiperravan** | prava u 2D, ravan u 3D, hiperravan u $n$D |
| **margina** | maksimalni razmak između klasa |
| **potporni vektori** | tačke koje dodiruju margine |

Vektor $w$ je **perpendikularan** na hiperravan i određuje njen pravac. Znak izraza
$w \cdot x + b$ pokazuje na kojoj strani se nalazi tačka:

- $w \cdot x + b > 0$ → jedna klasa
- $w \cdot x + b < 0$ → druga klasa

> Postoji **beskonačno mnogo** hiperravni koje razdvajaju podatke. SVM bira onu sa
> **najvećom marginom**, jer veća margina znači bolju generalizaciju na nove podatke.
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVC, LinearSVC, SVR
from sklearn.datasets import make_blobs, make_circles, load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline, make_pipeline

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42

X, y = make_blobs(n_samples=60, centers=2, cluster_std=1.1, random_state=6)
print(f"Podaci: {X.shape[0]} uzoraka, 2 obelezja, 2 klase (linearno separabilne)")
""")

md(C, r"""
## Uslovi za pravilnu klasifikaciju

Za tačke pozitivne klase: $w \cdot x_i + b \geq 1$
Za tačke negativne klase: $w \cdot x_i + b \leq -1$

Uvođenjem $y_i \in \{+1, -1\}$ oba uslova se spajaju u **jedan**:

$$y_i \, (w \cdot x_i + b) \geq 1$$

## Izračunavanje margine

Za potporne vektore važi $w \cdot x^+ + b = +1$ i $w \cdot x^- + b = -1$. Oduzimanjem:

$$w \cdot x^+ - w \cdot x^- = 2$$

Projekcija razlike na jedinični vektor $\frac{w}{\lVert w \rVert}$ daje širinu margine:

$$\boxed{\text{margina} = \frac{2}{\lVert w \rVert}}$$

Odatle sledi ključni zaključak:

$$\text{maksimizovati marginu} \iff \text{minimizovati } \lVert w \rVert$$

## Optimizacioni problem

$$\min \lVert w \rVert \quad \text{uz ograničenje} \quad y_i(w \cdot x_i + b) \geq 1$$

Rešava se **Lagrangeovim multiplikatorima**:

$$L = \tfrac{1}{2}\lVert w \rVert^2 - \sum_i \alpha_i \big[ y_i (w \cdot x_i + b) - 1 \big]$$

Iz uslova optimalnosti:

$$\frac{\partial L}{\partial w} = 0 \implies w = \sum_i \alpha_i y_i x_i \qquad
\frac{\partial L}{\partial b} = 0 \implies \sum_i \alpha_i y_i = 0$$

> **Ključna posledica:** $w$ je linearna kombinacija trening tačaka, ali **samo one sa
> $\alpha_i > 0$ učestvuju** — to su **potporni vektori**. Većina tačaka ne utiče na rešenje.
""")

code(C, r"""
svm = SVC(kernel="linear", C=1000).fit(X, y)      # veliko C ~ tvrda margina

w, b = svm.coef_[0], svm.intercept_[0]
margina = 2 / np.linalg.norm(w)

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(X[:, 0], X[:, 1], c=y, s=45, cmap="coolwarm", edgecolor="k", zorder=3)

xl = np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 50)
yl = np.linspace(X[:, 1].min() - 1, X[:, 1].max() + 1, 50)
YY, XX = np.meshgrid(yl, xl)
Z = svm.decision_function(np.vstack([XX.ravel(), YY.ravel()]).T).reshape(XX.shape)
ax.contour(XX, YY, Z, colors="k", levels=[-1, 0, 1],
           linestyles=["--", "-", "--"], linewidths=[1.2, 2, 1.2])

ax.scatter(svm.support_vectors_[:, 0], svm.support_vectors_[:, 1],
           s=280, facecolors="none", edgecolors="#55A868", linewidths=2.5,
           label=f"potporni vektori ({len(svm.support_vectors_)})", zorder=4)
ax.set_title(f"Margina = 2/||w|| = {margina:.3f}"); ax.legend()
plt.tight_layout(); plt.show()

print(f"w = {w.round(4)},  b = {b:.4f}")
print(f"||w|| = {np.linalg.norm(w):.4f}   ->   margina = 2/||w|| = {margina:.4f}")
print(f"\nTrening tacaka: {len(X)}, potpornih vektora: {len(svm.support_vectors_)}")
print(f"-> Hiperravan odredjuje samo {len(svm.support_vectors_)} tacaka, ostale ne uticu.")
""")

code(C, r"""
# dokaz: uklonimo tacku koja NIJE potporni vektor -> resenje se ne menja
nije_sv = [i for i in range(len(X)) if i not in svm.support_]
maska = np.ones(len(X), bool); maska[nije_sv[0]] = False

svm2 = SVC(kernel="linear", C=1000).fit(X[maska], y[maska])
print(f"Original bez izmene : w = {svm.coef_[0].round(5)}, b = {svm.intercept_[0]:.5f}")
print(f"Bez jedne NE-SV tacke: w = {svm2.coef_[0].round(5)}, b = {svm2.intercept_[0]:.5f}")
print("-> Identicno. Tacke koje nisu potporni vektori se mogu izbaciti bez posledica.")
""")

md(C, r"""
## Klasifikacija nove tačke

Za novu, nepoznatu tačku $u$:

$$f(u) = \sum_i \alpha_i y_i (x_i \cdot u) + b$$

- $f(u) \geq 0$ → pozitivna klasa
- $f(u) < 0$ → negativna klasa

Računa se **skalarni proizvod** između potpornih vektora $x_i$ i nove tačke $u$.
Ovaj oblik je važan — u njemu se pojavljuje **samo skalarni proizvod**, što će omogućiti
kernel trik.

## Parametar C — meka margina

U praksi podaci retko dozvoljavaju savršeno razdvajanje. Parametar $C$ kontroliše koliko
se kažnjava ulazak tačaka u marginu:

| $C$ | margina | ponašanje |
|---|---|---|
| **malo** | široka | dozvoljava greške, jednostavnija granica, veći bias |
| **veliko** | uska | pokušava savršeno razdvajanje, rizik od overfittinga |
""")

code(C, r"""
Xm, ym = make_blobs(n_samples=120, centers=2, cluster_std=2.4, random_state=RS)

fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
for a, Cv in zip(ax, (0.01, 0.1, 1, 100)):
    m = SVC(kernel="linear", C=Cv).fit(Xm, ym)
    a.scatter(Xm[:, 0], Xm[:, 1], c=ym, s=22, cmap="coolwarm", edgecolor="k", linewidth=0.3)
    x0, x1 = Xm[:, 0].min()-1, Xm[:, 0].max()+1
    y0, y1 = Xm[:, 1].min()-1, Xm[:, 1].max()+1
    XX, YY = np.meshgrid(np.linspace(x0, x1, 60), np.linspace(y0, y1, 60))
    Z = m.decision_function(np.c_[XX.ravel(), YY.ravel()]).reshape(XX.shape)
    a.contour(XX, YY, Z, colors="k", levels=[-1, 0, 1], linestyles=["--","-","--"], linewidths=[1,1.8,1])
    a.set_title(f"C = {Cv}\n{len(m.support_)} SV, margina {2/np.linalg.norm(m.coef_[0]):.2f}")
    a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()
print("Malo C -> siroka margina, mnogo potpornih vektora, jednostavniji model.")
""")

md(C, r"""
## Nelinearno separabilni problemi — XOR

Osnovni (linearni) SVM radi **samo** za linearno separabilne podatke. Klasičan
kontraprimer je **XOR**:

- pozitivna klasa: $(0,0)$ i $(1,1)$
- negativna klasa: $(0,1)$ i $(1,0)$

Ne postoji prava koja razdvaja klase — bez obzira kako je povučemo, uvek greši.

> **Poruka:** problem nije u algoritmu, nego u **prostoru u kome gledamo podatke**.
> Ako promenimo perspektivu, ono što je bilo nelinearno može postati linearno.
> **Ne menjamo algoritam — menjamo prostor.**
""")

code(C, r"""
Xx = np.array([[0,0],[1,1],[0,1],[1,0]], float)
yx = np.array([1, 1, 0, 0])

lin = SVC(kernel="linear", C=100).fit(Xx, yx)
rbf = SVC(kernel="rbf", C=100, gamma=2).fit(Xx, yx)
print(f"XOR — linearni kernel: tacnost {lin.score(Xx, yx):.2f}   <- ne moze")
print(f"XOR — RBF kernel     : tacnost {rbf.score(Xx, yx):.2f}   <- resava")

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for a, (m, ime) in zip(ax, [(lin, "linearni kernel"), (rbf, "RBF kernel")]):
    XX, YY = np.meshgrid(np.linspace(-0.6, 1.6, 250), np.linspace(-0.6, 1.6, 250))
    Z = m.predict(np.c_[XX.ravel(), YY.ravel()]).reshape(XX.shape)
    a.contourf(XX, YY, Z, alpha=0.28, cmap="coolwarm")
    a.scatter(Xx[:, 0], Xx[:, 1], c=yx, s=260, cmap="coolwarm", edgecolor="k", linewidth=1.5)
    for (px, py), kl in zip(Xx, yx):
        a.annotate(f"({px:.0f},{py:.0f})", (px, py), textcoords="offset points",
                   xytext=(12, 10), fontsize=10)
    a.set_title(f"{ime} — tacnost {m.score(Xx, yx):.0%}")
plt.tight_layout(); plt.show()
""")

md(C, r"""
## Kernel trik

**Pretpostavka:** postoji transformacija $T(x)$ koja preslikava podatke u
višedimenzionalni prostor gde je linearno razdvajanje moguće.

**Problem:** u decision function bi trebalo računati $T(x_i) \cdot T(u)$, a to je računski
vrlo skupo (ili nemoguće ako je dimenzionalnost beskonačna).

**Rešenje — kernel funkcija:**

$$K(x_i, u) = T(x_i) \cdot T(u)$$

Kernel **direktno računa skalarni proizvod u višedimenzionalnom prostoru**, bez potrebe da
poznajemo ili računamo samu transformaciju $T$.

> SVM i dalje ostaje **linearan** — ali u novom prostoru osobina.
> Kernel funkcije se mogu tumačiti kao **mere sličnosti** između podataka.

### Popularne kernel funkcije

| kernel | formula |
|---|---|
| **linearni** | $K(u,v) = u \cdot v$ |
| **polinomijalni** | $K(u,v) = (u \cdot v + 1)^n$ |
| **Gaussov (RBF)** | $K(u,v) = \exp\left(-\dfrac{\lVert u-v \rVert^2}{2\sigma^2}\right)$ |

U `scikit-learn` se RBF piše kao $\exp(-\gamma \lVert u-v \rVert^2)$, gde je
$\gamma = \frac{1}{2\sigma^2}$.
""")

code(C, r"""
Xc, yc = make_circles(n_samples=300, factor=0.45, noise=0.12, random_state=RS)

fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
for a, (k, par) in zip(ax, [("linear", {}), ("poly", {"degree": 3}),
                            ("rbf", {"gamma": 1}), ("sigmoid", {})]):
    m = make_pipeline(StandardScaler(), SVC(kernel=k, C=1, **par)).fit(Xc, yc)
    XX, YY = np.meshgrid(np.linspace(-1.6, 1.6, 220), np.linspace(-1.6, 1.6, 220))
    Z = m.predict(np.c_[XX.ravel(), YY.ravel()]).reshape(XX.shape)
    a.contourf(XX, YY, Z, alpha=0.28, cmap="coolwarm")
    a.scatter(Xc[:, 0], Xc[:, 1], c=yc, s=14, cmap="coolwarm", edgecolor="k", linewidth=0.2)
    a.set_title(f"{k}\ntacnost {m.score(Xc, yc):.3f}"); a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()
print("Podaci su koncentricni krugovi — linearni kernel nema sanse, RBF ih razdvaja lako.")
""")

md(C, r"""
### Uticaj parametra $\gamma$ kod RBF kernela

$\gamma$ određuje koliko „daleko" seže uticaj jedne trening tačke:

- **malo $\gamma$** — širok uticaj, glatka granica, rizik od underfittinga
- **veliko $\gamma$** — uzak uticaj, granica se lepi za pojedinačne tačke, overfitting
""")

code(C, r"""
Xg, yg = make_blobs(n_samples=180, centers=3, cluster_std=1.8, random_state=RS)
fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
for a, g in zip(ax, (0.01, 0.1, 1, 20)):
    m = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1, gamma=g)).fit(Xg, yg)
    XX, YY = np.meshgrid(np.linspace(Xg[:,0].min()-1, Xg[:,0].max()+1, 220),
                         np.linspace(Xg[:,1].min()-1, Xg[:,1].max()+1, 220))
    Z = m.predict(np.c_[XX.ravel(), YY.ravel()]).reshape(XX.shape)
    a.contourf(XX, YY, Z, alpha=0.28, cmap="viridis")
    a.scatter(Xg[:,0], Xg[:,1], c=yg, s=16, cmap="viridis", edgecolor="k", linewidth=0.2)
    a.set_title(f"gamma = {g}\ntrening {m.score(Xg, yg):.3f}")
    a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()
""")

md(C, r"""
## SVM u praksi

**Skaliranje je obavezno** — SVM se oslanja na rastojanja i skalarne proizvode, pa
atributi sa velikim vrednostima dominiraju.

Dva hiperparametra se podešavaju zajedno: **`C`** i **`gamma`**.
""")

code(C, r"""
bc = load_breast_cancer()
Xb, yb = bc.data, bc.target

bez = cross_val_score(SVC(kernel="rbf"), Xb, yb, cv=5).mean()
sa = cross_val_score(make_pipeline(StandardScaler(), SVC(kernel="rbf")), Xb, yb, cv=5).mean()
print(f"BEZ skaliranja: {bez:.4f}")
print(f"SA skaliranjem: {sa:.4f}   <- razlika je velika\n")

gs = GridSearchCV(Pipeline([("sc", StandardScaler()), ("svm", SVC())]),
                  {"svm__C": [0.1, 1, 10, 100],
                   "svm__gamma": ["scale", 0.001, 0.01, 0.1],
                   "svm__kernel": ["rbf", "linear"]},
                  cv=5, n_jobs=-1).fit(Xb, yb)
print(f"Najbolji parametri: {gs.best_params_}")
print(f"Najbolji CV rezultat: {gs.best_score_:.4f}")
""")

md(C, r"""
## Ograničenja i sažetak

**Ograničenja osnovnog SVM-a**
- definisan za **binarnu** klasifikaciju (višeklasni se rešava strategijama one-vs-one / one-vs-rest)
- linearni oblik radi samo za **linearno separabilne** podatke — otud kernel trik
- složenost treniranja raste **kvadratno** sa brojem uzoraka, pa je spor na velikim skupovima
- ne daje prirodno verovatnoće (potreban `probability=True`, koji dodatno usporava)

**Prednosti**
- jasna geometrijska interpretacija i teorijska garancija (maksimalna margina)
- efikasan u **visokodimenzionalnim** prostorima
- rešenje zavisi samo od potpornih vektora, pa je memorijski štedljiv
""")
upisi(C, "06_svm.ipynb")

# ═══════════════════════════════════════════════════════ 07 EVALUACIJA
C = novi()
md(C, r"""
# 7. Evaluacija modela u mašinskom učenju

## Generalizacija

Cilj mašinskog učenja je da se model **dobro generalizuje** na nove, neviđene podatke:
visoka tačnost generalizacije, niska greška generalizacije.

$$\text{Tačnost} = 1 - \text{greška}$$

## Overfitting i underfitting

| | trening greška | test greška |
|---|---|---|
| **underfitting** (podobučavanje) | **velika** | velika |
| **overfitting** (preprilagođavanje) | **mala** | **velika** |

| uzroci underfittinga | uzroci overfittinga |
|---|---|
| model previše jednostavan | veliki kapacitet modela |
| mali kapacitet | malo podataka |
| nedovoljno treniranja | predugo treniranje |
| važne osobine nisu uključene | previše parametara |

### Kapacitet modela

Kapacitet govori **koliko je model fleksibilan**. Raste kada model ima više parametara,
dublju strukturu, nelinearne funkcije, ili manje ograničenja (regularizacije).

Primer: stablo dubine 1 (*decision stump*) ima mali kapacitet; duboko stablo veliki.
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import (train_test_split, cross_val_score, KFold, StratifiedKFold,
                                     LeaveOneOut, learning_curve, validation_curve, GridSearchCV)
from sklearn.datasets import make_classification, load_breast_cancer, load_digits
from sklearn.metrics import (confusion_matrix, ConfusionMatrixDisplay, accuracy_score,
                             precision_score, recall_score, f1_score, balanced_accuracy_score,
                             roc_curve, roc_auc_score, classification_report,
                             precision_recall_curve, average_precision_score)

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42
rng = np.random.RandomState(RS)
print("Spremno.")
""")

md(C, r"""
## Bias–Variance razlaganje

$$\text{Greška} = \text{Bias}^2 + \text{Varijansa} + \text{Šum}$$

| komponenta | definicija | uzrok |
|---|---|---|
| **Bias** | $\mathbb{E}[\hat\theta] - \theta$ — sistematska greška | model previše jednostavan → underfitting |
| **Varijansa** | $\mathbb{E}\big[(\hat\theta - \mathbb{E}[\hat\theta])^2\big]$ — osetljivost na podatke | model previše složen → overfitting |
| **Šum** | neizbežna slučajnost | ne može se ukloniti nijednim modelom |

### Intuicija

> **Bias** meri koliko smo daleko od cilja → **tačnost**.
> **Varijansa** meri koliko smo rasuti oko proseka → **stabilnost**.

| bias | varijansa | opis |
|---|---|---|
| nizak | niska | idealno: tačan i stabilan |
| nizak | visoka | u proseku pogađa, ali su predikcije rasute (duboka stabla) |
| visok | niska | konzistentno pogrešan (linearni model za nelinearan problem) |
| visok | visoka | najgore: pogrešan i nestabilan |

### Zašto srednji član nestaje u izvođenju

$$\mathbb{E}\big[2(y - \mathbb{E}[\hat y])(\mathbb{E}[\hat y] - \hat y)\big]
= 2(y - \mathbb{E}[\hat y]) \cdot \underbrace{\mathbb{E}\big[\mathbb{E}[\hat y] - \hat y\big]}_{= \, \mathbb{E}[\hat y] - \mathbb{E}[\hat y] \, = \, 0} = 0$$
""")

code(C, r"""
# simulacija: treniramo isti model na 60 razlicitih trening skupova
def prava_f(x): return np.sin(1.5 * x)

x_test = np.linspace(0, 5, 100).reshape(-1, 1)
y_pravo = prava_f(x_test).ravel()

fig, ax = plt.subplots(1, 3, figsize=(14, 4))
rezultat = []
for a, (ime, napravi) in zip(ax, [
        ("visok bias\n(linearan)", lambda: LinearRegression()),
        ("balansirano\n(polinom 4)", lambda: make_pipeline(PolynomialFeatures(4), LinearRegression())),
        ("visoka varijansa\n(stablo bez ogranicenja)", lambda: DecisionTreeRegressor(random_state=None))]):
    predikcije = []
    for i in range(60):
        r = np.random.RandomState(i)
        xt = r.uniform(0, 5, 30).reshape(-1, 1)
        yt = prava_f(xt).ravel() + r.normal(0, 0.3, 30)
        p = napravi().fit(xt, yt).predict(x_test)
        predikcije.append(p)
        if i < 25:
            a.plot(x_test, p, color="#4C72B0", alpha=0.18, lw=1)
    P = np.array(predikcije)
    bias2 = np.mean((P.mean(0) - y_pravo) ** 2)
    var = np.mean(P.var(0))
    rezultat.append({"model": ime.replace("\n", " "), "bias^2": round(bias2, 4),
                     "varijansa": round(var, 4), "zbir": round(bias2 + var, 4)})
    a.plot(x_test, y_pravo, color="k", lw=2.5, label="prava funkcija")
    a.plot(x_test, P.mean(0), color="#C44E52", lw=2.5, ls="--", label="prosek modela")
    a.set_title(ime); a.legend(fontsize=8); a.set_ylim(-2.5, 2.5)
plt.tight_layout(); plt.show()
pd.DataFrame(rezultat)
""")

md(C, r"""
## Hiperparametri

Hiperparametri se **ne uče iz podataka**, već se postavljaju **pre** treniranja. Kontrolišu
složenost, kapacitet i bias–variance kompromis.

| model | hiperparametri |
|---|---|
| **k-NN** | broj suseda $k$, mera rastojanja |
| **stablo** | `max_depth`, `min_samples_leaf`, `min_samples_split` |
| **logistička regresija** | jačina L2-regularizacije $\lambda$ (u sklearn: $C = 1/\lambda$) |

Za logističku regresiju sa L2-regularizacijom:

$$\mathcal{L}(w) = -\sum_{i=1}^{n}\big[y_i\log\hat y_i + (1-y_i)\log(1-\hat y_i)\big] + \lambda\lVert w\rVert_2^2$$

| $\lambda$ | regularizacija | bias | varijansa |
|---|---|---|---|
| veliko | jača | veći | manja |
| malo | slabija | manji | veća |
""")

code(C, r"""
Xd, yd = load_digits(return_X_y=True)
opseg = np.logspace(-4, 3, 12)
tr, te = validation_curve(
    make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
    Xd, yd, param_name="logisticregression__C", param_range=opseg, cv=5, n_jobs=-1)

fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogx(opseg, tr.mean(1), "o-", label="trening", color="#4C72B0")
ax.fill_between(opseg, tr.mean(1)-tr.std(1), tr.mean(1)+tr.std(1), alpha=0.15, color="#4C72B0")
ax.semilogx(opseg, te.mean(1), "s-", label="validacija", color="#C44E52")
ax.fill_between(opseg, te.mean(1)-te.std(1), te.mean(1)+te.std(1), alpha=0.15, color="#C44E52")
ax.set_xlabel("C = 1/lambda  (desno = slabija regularizacija)"); ax.set_ylabel("tacnost")
ax.set_title("Kriva validacije"); ax.legend()
plt.tight_layout(); plt.show()
print(f"Najbolje C = {opseg[int(np.argmax(te.mean(1)))]:.4f}, tacnost {te.mean(1).max():.4f}")
""")

md(C, r"""
## Podela podataka i izbor hiperparametara

Ispravan postupak, korak po korak:

1. Model se trenira na **trening** skupu, za različite vrednosti hiperparametara
2. Evaluacija na **validacionom** skupu → biraju se najbolji hiperparametri
3. Izbor se **zaključava**, model se ponovo trenira na (train + validation)
4. Performanse se mere **jednom**, isključivo na **test** skupu

> **Test skup se ne koristi tokom izbora hiperparametara.** Ako se koristi, prestaje da bude
> neviđen i procena postaje optimistična.

## Unakrsna validacija

$$\text{Performance} = \frac{1}{k}\sum_{i=1}^{k}\text{Performance}_i$$

Preporučeni izbori u praksi: **$k = 5$** ili **$k = 10$**.

| varijanta | opis |
|---|---|
| **Holdout** | jedna podela; brz, ali nestabilna procena |
| **2-fold** | jednostavan, ali visoka varijansa procene |
| **Ponavljani holdout** | više nasumičnih podela, prosek |
| **LOOCV** ($k = n$) | maksimalno koristi podatke; računski vrlo skup |

Kako $k$ raste: **bias opada**, ali **varijansa i računska cena rastu**.
""")

code(C, r"""
Xs, ys = make_classification(n_samples=220, n_features=12, n_informative=6,
                             random_state=RS)
model = DecisionTreeClassifier(max_depth=4, random_state=RS)

import time
print(f"{'metoda':<28} {'prosek':>8} {'st.dev':>8} {'vreme':>8}")
print("-" * 56)
for ime, cv in [("holdout (2-fold)", KFold(2, shuffle=True, random_state=RS)),
                ("5-fold", StratifiedKFold(5, shuffle=True, random_state=RS)),
                ("10-fold", StratifiedKFold(10, shuffle=True, random_state=RS)),
                ("LOOCV (k = n)", LeaveOneOut())]:
    t0 = time.time()
    s = cross_val_score(model, Xs, ys, cv=cv, n_jobs=-1)
    print(f"{ime:<28} {s.mean():>8.4f} {s.std():>8.4f} {time.time()-t0:>7.2f}s")
""")

md(C, r"""
## Krive učenja — da li treba više podataka

Kriva učenja pokazuje da li je model ograničen **količinom podataka** ili **sopstvenim
kapacitetom**:

- ako validaciona kriva **još raste** → više podataka bi pomoglo
- ako je **ravna**, a razmak od trening krive velik → **overfitting**, treba jednostavniji model ili regularizacija
- ako su **obe niske i blizu** → **underfitting**, treba složeniji model
""")

code(C, r"""
Xb, yb = load_breast_cancer(return_X_y=True)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, (ime, m) in zip(ax, [("Stablo bez ogranicenja (overfitting)", DecisionTreeClassifier(random_state=RS)),
                            ("Logisticka regresija (balansirano)",
                             make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)))]):
    n, tr, te = learning_curve(m, Xb, yb, cv=5, n_jobs=-1,
                               train_sizes=np.linspace(0.1, 1.0, 8))
    a.plot(n, tr.mean(1), "o-", label="trening", color="#4C72B0")
    a.plot(n, te.mean(1), "s-", label="validacija", color="#C44E52")
    a.fill_between(n, te.mean(1)-te.std(1), te.mean(1)+te.std(1), alpha=0.15, color="#C44E52")
    a.set_xlabel("broj trening uzoraka"); a.set_ylabel("tacnost")
    a.set_title(ime); a.legend()
plt.tight_layout(); plt.show()
""")

md(C, r"""
## Mere performansi — matrica konfuzije

|  | predviđeno 0 | predviđeno 1 |
|---|---|---|
| **stvarno 0** | TN | FP |
| **stvarno 1** | FN | TP |

$$ERR = \frac{FP+FN}{TP+TN+FP+FN} \qquad ACC = \frac{TP+TN}{TP+TN+FP+FN} = 1 - ERR$$

$$\text{Precision} = \frac{TP}{TP+FP} \qquad
\text{Recall} = \frac{TP}{TP+FN} \qquad
F_1 = 2\cdot\frac{P \cdot R}{P + R}$$

**Preciznost** odgovara na pitanje: *od svih koje sam označio kao pozitivne, koliko je zaista pozitivno?*
**Odziv** odgovara: *od svih stvarno pozitivnih, koliko sam ih pronašao?*
**F1** je harmonijska sredina te dve mere.
""")

code(C, r"""
Xtr, Xte, ytr, yte = train_test_split(Xb, yb, test_size=0.3, random_state=RS, stratify=yb)
m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(Xtr, ytr)
pred = m.predict(Xte)
cm = confusion_matrix(yte, pred)
tn, fp, fn, tp = cm.ravel()

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay(cm, display_labels=["maligni", "benigni"]).plot(ax=ax, cmap="Blues", colorbar=False)
ax.grid(False); plt.tight_layout(); plt.show()

print(f"TN={tn}  FP={fp}  FN={fn}  TP={tp}\n")
print(f"ERR        = (FP+FN)/n  = {(fp+fn)/cm.sum():.4f}")
print(f"ACC        = (TP+TN)/n  = {(tp+tn)/cm.sum():.4f}   = 1 - ERR")
print(f"Preciznost = TP/(TP+FP) = {tp/(tp+fp):.4f}")
print(f"Odziv      = TP/(TP+FN) = {tp/(tp+fn):.4f}")
print(f"F1                       = {f1_score(yte, pred):.4f}")
""")

md(C, r"""
## Balansirani i nebalansirani skupovi

**Balansiran skup** — sve klase imaju sličan broj uzoraka; tačnost je pouzdana metrika.

**Nebalansiran skup** — jedna klasa je znatno manje zastupljena. Tada model može imati
**visoku tačnost, a da uopšte ne detektuje manjinsku klasu** — koja je često najvažnija
(medicina, prevare).

> **Zato tačnost „vara" kod nebalansiranih podataka.**

Metrike koje treba koristiti: **Precision / Recall**, **F1**, **ROC-AUC**,
**Balanced Accuracy / APC**.

### Balanced / APC accuracy

Svaka klasa je jednako važna bez obzira na veličinu — izračuna se tačnost po klasi, pa
aritmetička sredina:

$$APC = \frac{ACC_{\text{klasa 0}} + ACC_{\text{klasa 1}} + ACC_{\text{klasa 2}}}{3}$$
""")

code(C, r"""
Xi, yi = make_classification(n_samples=3000, n_features=15, n_informative=6,
                             weights=[0.96, 0.04], random_state=RS)
Xtr2, Xte2, ytr2, yte2 = train_test_split(Xi, yi, test_size=0.3, random_state=RS, stratify=yi)
print(f"Raspodela klasa: {np.bincount(yi).tolist()}  ->  manjinska klasa {yi.mean():.1%}\n")

from sklearn.dummy import DummyClassifier
redovi = []
for ime, mod in [("Dummy (uvek vecinska)", DummyClassifier(strategy="most_frequent")),
                 ("LogReg (bez tezina)", make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))),
                 ("LogReg (class_weight)", make_pipeline(StandardScaler(),
                                            LogisticRegression(max_iter=3000, class_weight="balanced")))]:
    mod.fit(Xtr2, ytr2); p = mod.predict(Xte2)
    redovi.append({"model": ime,
                   "tacnost": round(accuracy_score(yte2, p), 4),
                   "balanced_acc": round(balanced_accuracy_score(yte2, p), 4),
                   "preciznost": round(precision_score(yte2, p, zero_division=0), 4),
                   "odziv": round(recall_score(yte2, p), 4),
                   "F1": round(f1_score(yte2, p), 4)})
display(pd.DataFrame(redovi))
print("-> Dummy ima tacnost ~96%, a odziv 0. Tacnost potpuno zavarava.")
print("   Balanced accuracy i F1 to odmah otkrivaju.")
""")

md(C, r"""
## ROC kriva i AUC

ROC prikazuje odnos:

$$TPR = \frac{TP}{TP+FN} \qquad FPR = \frac{FP}{FP+TN}$$

- kriva bliža **gornjem levom uglu** → bolji model
- **dijagonala** → slučajno pogađanje

**AUC** (površina ispod ROC krive) sažima sve u jedan broj:

| AUC | tumačenje |
|---|---|
| 1.0 | savršen model |
| 0.8 | dobar model |
| 0.5 | slučajno pogađanje |

AUC je **verovatnoća da će model dodeliti veći skor pozitivnom nego negativnom primeru**.

> **Napomena:** kod jako nebalansiranih skupova ROC-AUC deluje optimistično, jer u obračun
> ulazi i ogroman broj lako prepoznatljivih negativnih primera. Tada je **PR kriva**
> (preciznost–odziv) informativnija.
""")

code(C, r"""
mod = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(Xtr2, ytr2)
skor = mod.predict_proba(Xte2)[:, 1]

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
fpr, tpr, _ = roc_curve(yte2, skor)
ax[0].plot(fpr, tpr, lw=2, color="#4C72B0", label=f"AUC = {roc_auc_score(yte2, skor):.4f}")
ax[0].plot([0,1],[0,1],"k--", label="slucajno")
ax[0].set_xlabel("FPR"); ax[0].set_ylabel("TPR"); ax[0].set_title("ROC kriva"); ax[0].legend()

pr, rc, _ = precision_recall_curve(yte2, skor)
ax[1].plot(rc, pr, lw=2, color="#C44E52", label=f"PR-AUC = {average_precision_score(yte2, skor):.4f}")
ax[1].axhline(yte2.mean(), color="k", ls="--", label=f"bazna linija = {yte2.mean():.3f}")
ax[1].set_xlabel("odziv"); ax[1].set_ylabel("preciznost"); ax[1].set_title("PR kriva"); ax[1].legend()
plt.tight_layout(); plt.show()

print(f"ROC-AUC = {roc_auc_score(yte2, skor):.4f}   <- deluje odlicno")
print(f"PR-AUC  = {average_precision_score(yte2, skor):.4f}   <- realnija slika pri {yte2.mean():.1%} pozitivnih")
""")

md(C, r"""
## Makro i mikro proseci

Kod **višeklasnih** problema metrike se mogu računati na dva načina:

| | kako se računa | ko dominira | kada koristiti |
|---|---|---|---|
| **Micro** | sabiraju se svi TP, FP, FN preko klasa | **dominantne klase** | klase približno balansirane |
| **Macro** | metrika po klasi, pa aritmetički prosek | **sve klase jednako** | podaci nebalansirani |

> **Micro:** „Koliko sam dobar u proseku **po uzorku**?"
> **Macro:** „Koliko sam dobar u proseku **po klasi**?"

Kod nebalansiranih skupova **macro** daje realniju sliku, jer ne dozvoljava da velika klasa
sakrije loš rezultat na maloj.
""")

code(C, r"""
Xm, ym = make_classification(n_samples=1500, n_features=12, n_informative=6,
                             n_classes=3, n_clusters_per_class=1,
                             weights=[0.75, 0.20, 0.05], random_state=RS)
Xtr3, Xte3, ytr3, yte3 = train_test_split(Xm, ym, test_size=0.3, random_state=RS, stratify=ym)
mm = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(Xtr3, ytr3)
p3 = mm.predict(Xte3)

print(f"Raspodela klasa: {np.bincount(ym).tolist()}\n")
print(classification_report(yte3, p3, digits=4))
print(f"F1 micro = {f1_score(yte3, p3, average='micro'):.4f}")
print(f"F1 macro = {f1_score(yte3, p3, average='macro'):.4f}   <- nizi, jer kaznjava lose")
print("                                       rezultate na maloj klasi 2")
""")

md(C, r"""
## Kontrolna lista za evaluaciju

- [ ] podaci podeljeni na **train / validation / test**, test korišćen **samo jednom**
- [ ] preprocesiranje (skaliranje, imputacija) naučeno **samo na trening skupu**
- [ ] kod grupisanih podataka koristi se `GroupKFold`, ne obična `KFold`
- [ ] metrika izabrana prema **raspodeli klasa** — ne tačnost kod nebalansiranih
- [ ] uvek prijavljena **bazna linija** (`DummyClassifier`), da se vidi šta je „loše"
- [ ] rezultat prijavljen sa **standardnom devijacijom** iz kros-validacije
- [ ] pogledana **kriva učenja** — da se zna da li treba više podataka ili drugi model
""")
upisi(C, "07_evaluacija.ipynb")
print("\nGotovo za 06-07.")
