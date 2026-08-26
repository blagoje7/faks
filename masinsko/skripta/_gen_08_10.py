# -*- coding: utf-8 -*-
"""Generise notebook-e 08-10 skripte iz Masinskog ucenja."""
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

# ═══════════════════════════════════════════════════════ 08 K-MEANS
C = novi()
md(C, r"""
# 8. k-srednjih vrednosti (k-Means)

## Nadgledano vs. nenadgledano učenje

| | nadgledano | nenadgledano |
|---|---|---|
| podaci | $(x^{(1)}, y^{(1)}), \dots, (x^{(m)}, y^{(m)})$ | $x^{(1)}, x^{(2)}, \dots, x^{(m)}$ |
| oznake | **postoje** | **ne postoje** |
| cilj | naučiti preslikavanje $x \to y$, naći granicu odlučivanja | pronaći **strukturu** u podacima |

Kod nenadgledanog učenja ne znamo „tačne odgovore" — algoritam sam pokušava da otkrije
kako su podaci organizovani.

## Gde se koristi klasterovanje

1. **Segmentacija tržišta** — podela korisnika u grupe kupaca; omogućava ciljani marketing i prilagođene ponude
2. **Analiza društvenih mreža** — otkrivanje koherentnih grupa ljudi, zajednica prijatelja ili saradnika
3. **Organizacija računarskih sistema i data centara** — klasterovanje računara koji često rade zajedno i intenzivno razmenjuju podatke
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.datasets import make_blobs, make_moons, load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42

X, y_pravo = make_blobs(n_samples=300, centers=4, cluster_std=1.1, random_state=RS)
print(f"Podaci: {X.shape[0]} tacaka u {X.shape[1]}D — BEZ oznaka")
""")

md(C, r"""
## Algoritam

**Ulaz:** broj klastera $K$ (biramo ga mi) i neoznačen skup $x^{(1)}, \dots, x^{(m)}$,
gde je $x^{(i)} \in \mathbb{R}^n$.

**1. Inicijalizacija**
Nasumično izabrati $K$ centroida $\mu_1, \dots, \mu_K \in \mathbb{R}^n$ (obično $K$
nasumičnih trening tačaka).

**2. Ponavljati do konvergencije:**

**(a) Korak dodele klastera** — za svaki primer $x^{(i)}$:
$$c^{(i)} := \arg\min_{k} \lVert x^{(i)} - \mu_k \rVert^2$$
Svaka tačka se dodeljuje **najbližem centroidu**.

**(b) Korak pomeranja centroida** — za svaki klaster $k$:
$$\mu_k := \frac{1}{|\{i : c^{(i)} = k\}|} \sum_{i : c^{(i)} = k} x^{(i)}$$
Centroid se pomera u **aritmetičku sredinu** svojih tačaka.

**Zaustavljanje:** kada se centroidi više ne pomeraju **ili** kada se dodele klastera više
ne menjaju.

> Ako neki klaster ostane bez ijedne tačke, najčešće se eliminiše ili se centroid ponovo
> nasumično inicijalizuje.
""")

code(C, r"""
def kmeans_rucno(X, K, max_iter=10, seed=3):
    'Rucna implementacija — da se vidi sta algoritam radi u svakoj iteraciji.'
    r = np.random.RandomState(seed)
    mu = X[r.choice(len(X), K, replace=False)].copy()     # 1. inicijalizacija
    istorija = []
    for it in range(max_iter):
        # (a) dodela: svaka tacka najblizem centroidu
        d = np.linalg.norm(X[:, None, :] - mu[None, :, :], axis=2)
        c = d.argmin(axis=1)
        # funkcija cilja J
        J = np.mean(np.sum((X - mu[c]) ** 2, axis=1))
        istorija.append((mu.copy(), c.copy(), J))
        # (b) pomeranje: centroid = prosek svojih tacaka
        novi = np.array([X[c == k].mean(axis=0) if (c == k).any() else mu[k] for k in range(K)])
        if np.allclose(novi, mu):
            break
        mu = novi
    return istorija

ist = kmeans_rucno(X, K=4)
print(f"Konvergiralo posle {len(ist)} iteracija\n")
print(f"{'iteracija':>10} {'J (funkcija cilja)':>20}")
for i, (_, _, J) in enumerate(ist):
    print(f"{i:>10} {J:>20.4f}")
print("\n-> J NIKADA ne raste. To je garancija konvergencije.")
""")

code(C, r"""
prikaz = [0, 1, 2, len(ist) - 1]
fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
for a, i in zip(ax, prikaz):
    mu, c, J = ist[i]
    a.scatter(X[:, 0], X[:, 1], c=c, s=16, cmap="viridis", alpha=0.65)
    a.scatter(mu[:, 0], mu[:, 1], c="red", s=250, marker="X", edgecolor="k", linewidth=1.5)
    a.set_title(f"iteracija {i}\nJ = {J:.2f}"); a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()
print("Crveni X su centroidi. Vidi se kako se pomeraju ka centrima svojih grupa.")
""")

md(C, r"""
## Optimizacioni cilj

Kao i algoritmi nadgledanog učenja, k-means ima **funkciju cilja** koju minimizuje:

$$J(c^{(1)},\dots,c^{(m)}, \mu_1,\dots,\mu_K) = \frac{1}{m}\sum_{i=1}^{m}\big\lVert x^{(i)} - \mu_{c^{(i)}} \big\rVert^2$$

To je **prosečno kvadratno rastojanje** tačaka od centroida svog klastera. Manje $J$ znači
kompaktnije klastere.

### Zašto $J$ nikada ne raste

k-means radi **naizmeničnu optimizaciju**:

| korak | šta je fiksno | šta se minimizuje |
|---|---|---|
| **(a) dodela** | centroidi $\mu$ | bira se $c^{(i)}$ koje minimizuje $J$ |
| **(b) pomeranje** | dodele $c$ | biraju se $\mu_k$ koji minimizuju $J$ |

Oba koraka smanjuju (ili ostavljaju istim) $J$, pa algoritam uvek **konvergira** — ali u
**lokalni** minimum.

**Provera ispravnosti:** ako $J$ raste ili osciluje kroz iteracije, nešto nije u redu
sa implementacijom.
""")

md(C, r"""
## Lokalni optimum i višestruka inicijalizacija

k-means **ne garantuje globalni optimum** — rezultat zavisi od nasumične inicijalizacije.

**Loša rešenja** se prepoznaju po tome što jedan klaster „proguta" previše tačaka, dok
neki imaju vrlo malo ili samo jednu tačku. Distorzija $J$ je veća, a algoritam više ne
može da se popravi.

**Rešenje:** pokrenuti k-means više puta (npr. 50–1000), svaki put sa drugom nasumičnom
inicijalizacijom, izračunati $J$, i izabrati klasterizaciju sa **najmanjom** vrednošću.

U `scikit-learn` to radi parametar **`n_init`**.
""")

code(C, r"""
Xl, _ = make_blobs(n_samples=300, centers=5, cluster_std=1.3, random_state=7)

print(f"{'seed':>6} {'J (inertia)':>14}")
J_vrednosti = []
for s in range(8):
    km = KMeans(n_clusters=5, n_init=1, init="random", random_state=s).fit(Xl)
    J_vrednosti.append(km.inertia_)
    print(f"{s:>6} {km.inertia_:>14.2f}")

print(f"\nRazlika najbolje-najgore: {max(J_vrednosti)-min(J_vrednosti):.2f}")
kmb = KMeans(n_clusters=5, n_init=50, random_state=RS).fit(Xl)
print(f"Sa n_init=50 (bira najbolje od 50): J = {kmb.inertia_:.2f}")
""")

code(C, r"""
najgori = int(np.argmax(J_vrednosti))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for a, (km, naslov) in zip(ax, [
        (KMeans(n_clusters=5, n_init=1, init="random", random_state=najgori).fit(Xl),
         f"LOS lokalni optimum (J={max(J_vrednosti):.0f})"),
        (kmb, f"DOBRO resenje (J={kmb.inertia_:.0f})")]):
    a.scatter(Xl[:, 0], Xl[:, 1], c=km.labels_, s=16, cmap="viridis", alpha=0.7)
    a.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1],
              c="red", s=200, marker="X", edgecolor="k")
    velicine = np.bincount(km.labels_, minlength=5)
    a.set_title(f"{naslov}\nvelicine klastera: {velicine.tolist()}")
    a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()
""")

md(C, r"""
## Kako izabrati broj klastera $K$

U nenadgledanom učenju **nema tačnog odgovora** — broj klastera je često subjektivan.
Isti podaci nekome izgledaju kao 2, nekome kao 3 ili 4 grupe, i sve interpretacije mogu
biti razumne.

### Elbow metoda („lakat")

1. Pokrenuti k-means za različite $K = 1, 2, 3, \dots$
2. Za svako $K$ izračunati distorziju $J$
3. Kako $K$ raste, $J$ **uvek opada**
4. Tražiti tačku gde smanjenje **naglo usporava** — kriva pravi „lakat"

**Prednost:** intuitivna i laka za vizuelnu interpretaciju.
**Nedostatak:** često **ne postoji jasan lakat**, pa izbor ostaje neodređen.

### Silhouette skor

Dopunska mera: koliko je tačka bliža svom klasteru nego najbližem susednom. Opseg
$[-1, 1]$, veće je bolje.

### Downstream kriterijum

U praksi se k-means koristi za neki **kasniji cilj**, pa se $K$ bira prema tome koliko
dobro klasteri služe toj svrsi.

> **Primer (veličine majica):** $K=3$ daje S, M, L; $K=5$ daje XS, S, M, L, XL.
> Pitanje nije *„koji je $K$ matematički tačan?"* nego *„koji je $K$ bolji za poslovanje?"*
""")

code(C, r"""
opseg = range(1, 11)
J_lista, sil = [], []
for k in opseg:
    km = KMeans(n_clusters=k, n_init=20, random_state=RS).fit(X)
    J_lista.append(km.inertia_)
    sil.append(silhouette_score(X, km.labels_) if k > 1 else np.nan)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(list(opseg), J_lista, "o-", lw=2, color="#4C72B0")
ax[0].axvline(4, color="#C44E52", ls="--", label="lakat na K=4")
ax[0].set_xlabel("broj klastera K"); ax[0].set_ylabel("J (inertia)")
ax[0].set_title("Elbow metoda"); ax[0].legend()

ax[1].plot(list(opseg), sil, "s-", lw=2, color="#55A868")
ax[1].axvline(4, color="#C44E52", ls="--")
ax[1].set_xlabel("broj klastera K"); ax[1].set_ylabel("silhouette")
ax[1].set_title("Silhouette skor")
plt.tight_layout(); plt.show()
print(f"Najbolji silhouette: K = {list(opseg)[int(np.nanargmax(sil))]}")
""")

md(C, r"""
### Primer: veličine majica

k-means se ne koristi samo kada postoje jasno razdvojeni klasteri, već i kada podaci čine
**kontinuiran skup bez očiglednih granica**. Visina i težina su pozitivno korelisane i ne
postoje prirodno odvojene grupe — ali nam ipak treba podela na S, M i L.

**Centroid klastera** postaje tipična visina i težina za tu veličinu.
""")

code(C, r"""
r = np.random.RandomState(RS)
visina = r.normal(172, 9, 400)
tezina = 0.9 * (visina - 172) + r.normal(72, 9, 400)
majice = np.c_[visina, tezina]

km_t = KMeans(n_clusters=3, n_init=20, random_state=RS).fit(StandardScaler().fit_transform(majice))
sc = StandardScaler().fit(majice)
centri = sc.inverse_transform(km_t.cluster_centers_)
poredak = np.argsort(centri[:, 0])
oznake = {poredak[0]: "S", poredak[1]: "M", poredak[2]: "L"}

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(majice[:, 0], majice[:, 1], c=km_t.labels_, s=16, cmap="viridis", alpha=0.6)
for i, (cv, ct) in enumerate(centri):
    ax.scatter(cv, ct, c="red", s=250, marker="X", edgecolor="k", zorder=5)
    ax.annotate(oznake[i], (cv, ct), fontsize=15, fontweight="bold",
                xytext=(12, 8), textcoords="offset points")
ax.set_xlabel("visina (cm)"); ax.set_ylabel("tezina (kg)")
ax.set_title("K=3 -> tri velicine majice; centroid = tipicne dimenzije")
plt.tight_layout(); plt.show()

for i in poredak:
    print(f"   {oznake[i]}: visina {centri[i,0]:.1f} cm, tezina {centri[i,1]:.1f} kg, "
          f"{(km_t.labels_==i).sum()} ljudi")
""")

md(C, r"""
## Ograničenja k-means algoritma

1. **Pretpostavlja sferične klastere** — ne radi dobro za izdužene ili nepravilne oblike
2. **Pretpostavlja sličnu veličinu** klastera — grupe različitih gustina se loše razdvajaju
3. **Zasnovan na Euklidskom rastojanju** → rezultat zavisi od skale, **normalizacija je neophodna**
4. **Osetljiv na outliere** — jedna ekstremna tačka može značajno pomeriti centroid
5. **Zavisi od inicijalizacije** — može se zaglaviti u lokalnom optimumu

### Kada k-means nije dobar izbor

Kada su klasteri nepravilnog oblika, različite gustine, ili ima mnogo šuma i outliera.
Tada se koriste: **hijerarhijsko klasterovanje**, **DBSCAN**, **HDBSCAN**.
""")

code(C, r"""
Xmo, ymo = make_moons(n_samples=300, noise=0.06, random_state=RS)

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
km = KMeans(n_clusters=2, n_init=20, random_state=RS).fit(Xmo)
ax[0].scatter(Xmo[:,0], Xmo[:,1], c=km.labels_, s=16, cmap="coolwarm")
ax[0].set_title(f"k-means (ARI = {adjusted_rand_score(ymo, km.labels_):.3f})")

db = DBSCAN(eps=0.22, min_samples=5).fit(Xmo)
ax[1].scatter(Xmo[:,0], Xmo[:,1], c=db.labels_, s=16, cmap="coolwarm")
ax[1].set_title(f"DBSCAN (ARI = {adjusted_rand_score(ymo, db.labels_):.3f})")

hi = AgglomerativeClustering(n_clusters=2, linkage="single").fit(Xmo)
ax[2].scatter(Xmo[:,0], Xmo[:,1], c=hi.labels_, s=16, cmap="coolwarm")
ax[2].set_title(f"Hijerarhijsko (ARI = {adjusted_rand_score(ymo, hi.labels_):.3f})")
for a in ax: a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()
print("k-means secе polumesece popola jer trazi sfericne grupe.")
print("DBSCAN i hijerarhijsko sa single linkage prate OBLIK i uspevaju.")
""")

code(C, r"""
# osetljivost na skalu — zasto je normalizacija obavezna
plata = r.normal(60000, 15000, 200)
godine = r.normal(35, 8, 200)
Xs = np.c_[plata, godine]

km_bez = KMeans(3, n_init=20, random_state=RS).fit(Xs)
km_sa = KMeans(3, n_init=20, random_state=RS).fit(StandardScaler().fit_transform(Xs))

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for a, (lab, t) in zip(ax, [(km_bez.labels_, "BEZ skaliranja"), (km_sa.labels_, "SA skaliranjem")]):
    a.scatter(Xs[:, 0], Xs[:, 1], c=lab, s=16, cmap="viridis")
    a.set_xlabel("plata"); a.set_ylabel("godine"); a.set_title(t)
plt.tight_layout(); plt.show()
print("Bez skaliranja klasteri se dele SAMO po plati — godine su numericki")
print("premale da bi uticale na Euklidsko rastojanje.")
""")
upisi(C, "08_kmeans.ipynb")

# ═══════════════════════════════════════════════════════ 09 PCA
C = novi()
md(C, r"""
# 9. Analiza glavnih komponenti (PCA)

## Dimenzionalna redukcija

Postupak smanjenja broja atributa (dimenzija) u podacima, **uz zadržavanje što više
korisne informacije**.

Često imamo veliki broj atributa koji su **međusobno snažno korelisani** ili
**redundantni** — nose skoro istu informaciju.

**Klasičan primer:** dva atributa mere istu fizičku veličinu — dužina u centimetrima i
dužina u inčima. Podaci leže blizu prave linije, pa ih možemo opisati **jednom** dimenzijom.

### Šta se dobija

- kompresija podataka (manje memorije)
- brže izvršavanje algoritama učenja
- mogućnost **vizualizacije** (50D → 2D)
- uklanjanje redundantnih i korelisanih osobina
- uz **mali gubitak** informacije
""")

code(C, r"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris, load_digits, load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score, train_test_split

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42
rng = np.random.RandomState(RS)

# dva atributa koji mere istu stvar: duzina u cm i u incima
cm = rng.uniform(10, 60, 120)
inci = cm / 2.54 + rng.normal(0, 0.35, 120)
Xd = np.c_[cm, inci]
print(f"Korelacija dva atributa: {np.corrcoef(cm, inci)[0,1]:.4f}  <- skoro savrsena")
""")

md(C, r"""
## Prva glavna komponenta

**Pravac najveće varijanse** (principal direction) je pravac duž koga projekcija podataka
ima **maksimalnu varijansu**. U PCA se naziva **prva glavna komponenta (PC1)**.

Svaki podatak $x^{(i)}$ projektujemo na taj pravac i umesto dva broja dobijamo jedan:

$$x^{(i)} \in \mathbb{R}^2 \longrightarrow z^{(i)} \in \mathbb{R}$$

## Projekciona greška

**Projekciona greška** je **ortogonalno** (najkraće) rastojanje između originalne tačke i
njene projekcije na izabrani pravac. PCA uvek koristi normalnu (90°) projekciju.

> PCA traži pravac $u^{(1)}$ takav da **zbir kvadrata projekcionih grešaka bude minimalan** —
> odnosno pravac na koji projekcija „najmanje kvari" originalne podatke.

Napomena: ako PCA vrati vektor $u^{(1)}$ ili njegov negativ $-u^{(1)}$, to je **isto rešenje** —
oba definišu istu liniju u prostoru.
""")

code(C, r"""
Xc = Xd - Xd.mean(axis=0)                       # centriranje
pca2 = PCA(n_components=2).fit(Xc)
pc1 = pca2.components_[0]

Z1 = Xc @ pc1                                    # projekcija na PC1
proj = np.outer(Z1, pc1)                         # nazad u 2D

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].scatter(Xc[:, 0], Xc[:, 1], s=22, color="#4C72B0", label="podaci", zorder=3)
duz = 3 * np.sqrt(pca2.explained_variance_)
for i, (v, d, boja) in enumerate(zip(pca2.components_, duz, ["#C44E52", "#55A868"])):
    ax[0].plot([-v[0]*d, v[0]*d], [-v[1]*d, v[1]*d], color=boja, lw=3,
               label=f"PC{i+1} ({pca2.explained_variance_ratio_[i]:.1%} varijanse)")
for p, q in zip(Xc[:40], proj[:40]):
    ax[0].plot([p[0], q[0]], [p[1], q[1]], color="gray", lw=0.8, alpha=0.7)
ax[0].set_aspect("equal"); ax[0].legend(fontsize=8)
ax[0].set_title("Sive linije su projekcione greske (ortogonalne!)")

ax[1].scatter(Z1, np.zeros_like(Z1), s=22, color="#C44E52", alpha=0.6)
ax[1].set_yticks([]); ax[1].set_xlabel("z (PC1)")
ax[1].set_title("Isti podaci u 1D — 2 broja svedena na 1")
plt.tight_layout(); plt.show()

print(f"PC1 objasnjava {pca2.explained_variance_ratio_[0]:.2%} varijanse")
print(f"PC2 objasnjava {pca2.explained_variance_ratio_[1]:.2%}  -> moze se odbaciti")
""")

md(C, r"""
## PCA nije linearna regresija

Na prvi pogled slično — obe metode traže pravu i minimizuju neku grešku. Ali su
**suštinski različite**:

| | linearna regresija | PCA |
|---|---|---|
| ciljna promenljiva $y$ | **postoji**, posebna je | **ne postoji**, sve osobine su ravnopravne |
| šta se minimizuje | **vertikalna** greška $y - \hat y$ | **ortogonalna** (projekciona) greška |
| cilj | predvideti $y$ | naći potprostor koji čuva najviše varijanse |
""")

code(C, r"""
from sklearn.linear_model import LinearRegression
lr = LinearRegression().fit(Xc[:, [0]], Xc[:, 1])

fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
xx = np.linspace(Xc[:, 0].min(), Xc[:, 0].max(), 50)

ax[0].scatter(Xc[:, 0], Xc[:, 1], s=20, color="#4C72B0")
ax[0].plot(xx, lr.predict(xx.reshape(-1, 1)), color="#C44E52", lw=2)
for p in Xc[:30]:
    ax[0].plot([p[0], p[0]], [p[1], lr.predict([[p[0]]])[0]], color="gray", lw=0.9)
ax[0].set_title("Linearna regresija — VERTIKALNE greske")

ax[1].scatter(Xc[:, 0], Xc[:, 1], s=20, color="#4C72B0")
ax[1].plot([-pc1[0]*duz[0], pc1[0]*duz[0]], [-pc1[1]*duz[0], pc1[1]*duz[0]], color="#55A868", lw=2)
for p, q in zip(Xc[:30], proj[:30]):
    ax[1].plot([p[0], q[0]], [p[1], q[1]], color="gray", lw=0.9)
ax[1].set_title("PCA — ORTOGONALNE greske")
for a in ax: a.set_aspect("equal")
plt.tight_layout(); plt.show()
""")

md(C, r"""
## Pretprocesiranje — obavezan korak

Pre PCA podaci se **moraju** pripremiti, inače komponente budu besmislene.

**1. Mean normalization** (centriranje):
$$\mu_j = \frac{1}{m}\sum_{i=1}^{m} x_j^{(i)}, \qquad x_j^{(i)} \leftarrow x_j^{(i)} - \mu_j$$
Posle ovog koraka svaka osobina ima srednju vrednost 0.

**2. Feature scaling:**
$$x_j^{(i)} \leftarrow \frac{x_j^{(i)} - \mu_j}{s_j}$$
gde je $s_j$ mera raspona (najčešće standardna devijacija).

> **Zašto je obavezno:** PCA traži pravce **najveće varijanse**. Bez skaliranja, osobine sa
> velikim numeričkim vrednostima automatski imaju najveću varijansu i **dominiraju** —
> rezultat je pogrešna glavna komponenta.
""")

code(C, r"""
bc = load_breast_cancer()
Xb = bc.data

pca_bez = PCA(n_components=5).fit(Xb)
pca_sa = PCA(n_components=5).fit(StandardScaler().fit_transform(Xb))

print("Varijansa originalnih atributa (5 najvecih):")
var = pd.Series(Xb.var(axis=0), index=bc.feature_names).sort_values(ascending=False)
print(var.head(5).round(1).to_string())

print(f"\nBEZ skaliranja — PC1 objasnjava {pca_bez.explained_variance_ratio_[0]:.2%}")
dom = np.abs(pca_bez.components_[0]).argmax()
print(f"   PC1 najvise zavisi od: '{bc.feature_names[dom]}' (varijansa {Xb[:,dom].var():.0f})")
print(f"\nSA skaliranjem — PC1 objasnjava {pca_sa.explained_variance_ratio_[0]:.2%}")
print(f"   -> Bez skaliranja PC1 je samo najveci atribut, ne prava struktura.")
""")

md(C, r"""
## Algoritam PCA

**Korak 1 — matrica kovarijanse.** Nad centriranim (i skaliranim) podacima:

$$\Sigma = \frac{1}{m}\sum_{i=1}^{m} x^{(i)} \big(x^{(i)}\big)^\top$$

$\Sigma$ je dimenzije $n \times n$ i opisuje kako su osobine međusobno povezane.

**Korak 2 — glavne komponente preko SVD.** Na $\Sigma$ se primenjuje **Singular Value
Decomposition**, koji vraća matricu $U$.

| pojam | značenje |
|---|---|
| **eigenvektor** | pravac glavne komponente |
| **eigenvrednost** | količina varijanse u tom pravcu |

SVD vraća komponente **već sortirane** po važnosti.

**Korak 3 — smanjenje dimenzije.** Zadržavamo prvih $k$ kolona:
$$U_{\text{reduce}} = \big[u^{(1)}, \dots, u^{(k)}\big] \in \mathbb{R}^{n \times k}$$

**Korak 4 — projekcija:**
$$z^{(i)} = U_{\text{reduce}}^\top \, x^{(i)} \in \mathbb{R}^{k}$$
""")

code(C, r"""
iris = load_iris()
Xi = StandardScaler().fit_transform(iris.data)

# --- rucno, korak po korak ---
Sigma = np.cov(Xi, rowvar=False)                          # korak 1
U, S, Vt = np.linalg.svd(Sigma)                           # korak 2
U_reduce = U[:, :2]                                       # korak 3
Z_rucno = Xi @ U_reduce                                   # korak 4

# --- sklearn ---
Z_sk = PCA(n_components=2).fit_transform(Xi)

print(f"Matrica kovarijanse Sigma: {Sigma.shape}")
print(f"Eigenvrednosti (varijansa po pravcu): {S.round(3)}")
print(f"Udeo varijanse: {(S/S.sum()).round(4)}")
print(f"\nRucno i sklearn daju isto (do znaka): "
      f"{np.allclose(np.abs(Z_rucno), np.abs(Z_sk))}")
""")

md(C, r"""
## Kako birati broj komponenti $K$

U praksi se **ne bira $K$ direktno**, već **procenat zadržane varijanse**.

Najčešće vrednosti: **95%** ili **99%**.

U `scikit-learn`:
- `PCA(n_components=k)` — zadržava tačno $k$ dimenzija
- `PCA(n_components=0.95)` — zadržava onoliko komponenti koliko treba za **95% varijanse**
""")

code(C, r"""
digits = load_digits()
Xg = StandardScaler().fit_transform(digits.data)

pca_pun = PCA().fit(Xg)
kum = np.cumsum(pca_pun.explained_variance_ratio_)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].bar(range(1, 31), pca_pun.explained_variance_ratio_[:30], color="#4C72B0")
ax[0].set_xlabel("komponenta"); ax[0].set_ylabel("udeo varijanse")
ax[0].set_title("Objasnjena varijansa po komponenti")

ax[1].plot(range(1, len(kum)+1), kum, lw=2, color="#4C72B0")
for prag, boja in [(0.90, "#DD8452"), (0.95, "#C44E52"), (0.99, "#55A868")]:
    k = int(np.argmax(kum >= prag)) + 1
    ax[1].axhline(prag, color=boja, ls="--", lw=1)
    ax[1].axvline(k, color=boja, ls=":", lw=1)
    ax[1].annotate(f"{prag:.0%} -> {k} komp.", (k, prag), fontsize=9,
                   xytext=(8, -14), textcoords="offset points", color=boja)
ax[1].set_xlabel("broj komponenti"); ax[1].set_ylabel("kumulativna varijansa")
ax[1].set_title("Koliko komponenti zadrzati")
plt.tight_layout(); plt.show()

print(f"Originalno dimenzija: {Xg.shape[1]}")
for p in (0.90, 0.95, 0.99):
    print(f"   za {p:.0%} varijanse potrebno: {int(np.argmax(kum >= p))+1} komponenti")
""")

md(C, r"""
## Vizualizacija visokodimenzionalnih podataka

Jedna od najkorisnijih primena: podatke u 50 ili 64 dimenzije ne možemo direktno
vizualizovati. PCA ih mapira u 2D i time omogućava da vidimo strukturu.

> **Važno:** ose $z_1$ i $z_2$ **nemaju unapred definisano značenje**. PCA ne zna šta je
> koji atribut — on samo pronalazi pravce najveće varijanse. **Značenje osama tumačimo
> naknadno**, mi ljudi.
""")

code(C, r"""
Z = PCA(n_components=2).fit_transform(Xg)
fig, ax = plt.subplots(figsize=(7.5, 5.5))
s = ax.scatter(Z[:, 0], Z[:, 1], c=digits.target, s=12, cmap="tab10", alpha=0.75)
plt.colorbar(s, label="cifra")
ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
ax.set_title("64 dimenzije svedene na 2 — cifre se grupisu")
plt.tight_layout(); plt.show()
""")

md(C, r"""
## PCA u praksi — sklearn i česta greška

```python
pca = PCA(n_components=2)
Z = pca.fit_transform(X)

pca.explained_variance_ratio_          # udeo varijanse po komponenti
pca.explained_variance_ratio_.sum()    # ukupna zadrzana varijansa
pca.components_                        # matrica U^T (pravci komponenti)
```

> **Česta greška:** na test skupu se poziva `fit_transform`. To je **data leakage** —
> PCA bi naučila pravce iz test podataka.
> Ispravno: `fit_transform(X_train)` i **samo** `transform(X_test)`.

Najsigurnije je koristiti `Pipeline`.
""")

code(C, r"""
Xtr, Xte, ytr, yte = train_test_split(digits.data, digits.target, test_size=0.3,
                                      random_state=RS, stratify=digits.target)
print(f"{'broj komponenti':>18} {'tacnost':>9} {'dimenzija':>11}")
print("-" * 42)
for k in (2, 5, 10, 20, 40, 0.95, None):
    if k is None:
        pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000))
        opis, dim = "bez PCA", Xtr.shape[1]
    else:
        pipe = make_pipeline(StandardScaler(), PCA(n_components=k),
                             LogisticRegression(max_iter=3000))
        opis = f"{k:.0%} varijanse" if isinstance(k, float) else str(k)
        dim = "-"
    pipe.fit(Xtr, ytr)
    if k is not None:
        dim = pipe.named_steps["pca"].n_components_
    print(f"{opis:>18} {pipe.score(Xte, yte):>9.4f} {str(dim):>11}")
""")

md(C, r"""
## Rekonstrukcija podataka

Iz kompresovane reprezentacije možemo približno vratiti originalne podatke:

$$x_{\text{approx}}^{(i)} = U_{\text{reduce}} \, z^{(i)}$$

Rezultat **nije identičan** originalu — razlika je upravo **projekciona greška**.

> PCA ne pamti originalne tačke, već njihovu **najbolju aproksimaciju** u izabranom
> potprostoru.
""")

code(C, r"""
fig, ax = plt.subplots(4, 8, figsize=(13, 6.5))
uzorci = [0, 3, 8, 15, 22, 30, 44, 51]
for j, i in enumerate(uzorci):
    ax[0, j].imshow(digits.images[i], cmap="gray_r"); ax[0, j].axis("off")
for red, k in enumerate((5, 20, 40), start=1):
    p = PCA(n_components=k).fit(digits.data)
    rek = p.inverse_transform(p.transform(digits.data))
    for j, i in enumerate(uzorci):
        ax[red, j].imshow(rek[i].reshape(8, 8), cmap="gray_r"); ax[red, j].axis("off")
for red, t in enumerate(["original (64)", "k = 5", "k = 20", "k = 40"]):
    ax[red, 0].set_ylabel(t)
    ax[red, 0].axis("on"); ax[red, 0].set_xticks([]); ax[red, 0].set_yticks([])
plt.suptitle("Rekonstrukcija iz sve veceg broja komponenti", y=0.99)
plt.tight_layout(); plt.show()

for k in (5, 20, 40):
    p = PCA(n_components=k).fit(digits.data)
    greska = np.mean((digits.data - p.inverse_transform(p.transform(digits.data))) ** 2)
    print(f"k = {k:>2}: zadrzano {p.explained_variance_ratio_.sum():.1%} varijanse, "
          f"greska rekonstrukcije {greska:.2f}")
""")
upisi(C, "09_pca.ipynb")
print("\nGotovo za 08-09.")
