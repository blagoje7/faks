# -*- coding: utf-8 -*-
"""Generise notebook-e 10-11 skripte iz Masinskog ucenja."""
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

# ═══════════════════════════════════════════════════════ 10 DUBOKO UČENJE
C = novi()
md(C, r"""
# 10. Duboko učenje

## Šta je duboko učenje

| oblast | opis |
|---|---|
| **Veštačka inteligencija (AI)** | razvoj inteligentnih sistema sposobnih za učenje, zaključivanje i rešavanje problema |
| **Mašinsko učenje (ML)** | podoblast AI; modeli uče obrasce iz podataka bez eksplicitnih pravila |
| **Duboko učenje (DL)** | podoblast ML; **neuronske mreže sa više slojeva** za automatsko učenje reprezentacija |
| **Generativna VI** | grana DL koja se bavi generisanjem novih podataka (tekst, slike, zvuk) |

## Ključni faktori uspeha dubokog učenja

1. **Velike količine podataka** — digitalizacija, internet, senzori, društvene mreže
2. **Povećana računarska snaga** — GPU, paralelno računanje, cloud
3. **Efikasni algoritmi treniranja** — backpropagation i poboljšane metode optimizacije
4. **Poboljšane arhitekture** — stabilnije i dublje mreže
5. **Razvoj softverskih alata** — biblioteke i okviri

## Tipovi neuronskih mreža

| tip | primena |
|---|---|
| **MLP** (višeslojne) | tabelarni podaci, opšta namena |
| **CNN** (konvolucione) | slike i prostorni podaci |
| **RNN / LSTM / GRU** | sekvence i vremenski nizovi |
| **Transformers** | mehanizam pažnje; dominantni u NLP-u i multimodalnim sistemima |
| **Generativne** | generisanje novih podataka |
""")

code(C, r"""
import warnings, os
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.datasets import load_breast_cancer, make_moons
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True; plt.rcParams["grid.alpha"] = 0.3
RS = 42
np.random.seed(RS); tf.random.set_seed(RS)
print(f"TensorFlow {tf.__version__}")
""")

md(C, r"""
## Logistička regresija kao jedan neuron

Logistička regresija se može posmatrati kao **najjednostavnija neuronska mreža** — jedan
neuron koji:

1. prima ulazni vektor $x \in \mathbb{R}^{n_x}$
2. računa **linearni deo**: $z = w^\top x + b$
3. primenjuje **aktivacionu funkciju**: $\hat y = a = \sigma(z)$

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

Parametri koji se uče su **težine** $w$ i **bias** $b$.
""")

code(C, r"""
bc = load_breast_cancer()
Xtr, Xte, ytr, yte = train_test_split(bc.data, bc.target, test_size=0.25,
                                      random_state=RS, stratify=bc.target)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

# 1. logisticka regresija iz sklearn-a
log = LogisticRegression(max_iter=5000).fit(Xtr_s, ytr)

# 2. ISTA stvar kao mreza sa jednim neuronom
neuron = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(Xtr_s.shape[1],)),
    tf.keras.layers.Dense(1, activation="sigmoid"),      # z = w'x + b, pa sigmoid
])
neuron.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
neuron.fit(Xtr_s, ytr, epochs=120, batch_size=32, verbose=0)

print(f"sklearn LogisticRegression : {log.score(Xte_s, yte):.4f}")
print(f"Keras — jedan neuron       : {neuron.evaluate(Xte_s, yte, verbose=0)[1]:.4f}")
print(f"\nBroj parametara neurona: {neuron.count_params()}  = {Xtr_s.shape[1]} tezina + 1 bias")
""")

md(C, r"""
## Funkcija greške i funkcija troška

**Funkcija greške (loss)** meri grešku za **jedan** trening primer.

| funkcija | formula | kada |
|---|---|---|
| **Kvadratna greška** | $\mathcal{L} = \tfrac{1}{2}(\hat y - y)^2$ | **regresija** |
| **Cross-entropy** | $\mathcal{L} = -\big[y\log\hat y + (1-y)\log(1-\hat y)\big]$ | **binarna klasifikacija** |

Kvadratna greška nije pogodna za klasifikaciju sa sigmoidom; cross-entropy daje stabilnije
i efikasnije učenje.

### Zašto log „kažnjava" samouverene greške

Ako je pravi odgovor $y = 1$:

| predikcija | $\log \hat y$ | greška |
|---|---|---|
| $\hat y \approx 1$ | $\approx 0$ | mala |
| $\hat y \approx 0$ | $\to -\infty$ | **ogromna** |

Model se **strogo kažnjava** kada je veoma siguran, a pogrešan.

**Funkcija troška (cost)** je **prosek** funkcije greške nad celim trening skupom:

$$J(w, b) = \frac{1}{m}\sum_{i=1}^{m} \mathcal{L}\big(\hat y^{(i)}, y^{(i)}\big)$$
""")

code(C, r"""
p = np.linspace(0.001, 0.999, 400)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(p, -np.log(p), lw=2.5, color="#4C72B0", label="y = 1:  -log(p)")
ax[0].plot(p, -np.log(1-p), lw=2.5, color="#C44E52", label="y = 0:  -log(1-p)")
ax[0].set_xlabel("predvidjena verovatnoca p"); ax[0].set_ylabel("greska")
ax[0].set_title("Cross-entropy"); ax[0].legend(); ax[0].set_ylim(0, 7)

ax[1].plot(p, 0.5*(p-1)**2, lw=2.5, color="#4C72B0", label="y = 1")
ax[1].plot(p, 0.5*p**2, lw=2.5, color="#C44E52", label="y = 0")
ax[1].set_xlabel("predvidjena verovatnoca p"); ax[1].set_ylabel("greska")
ax[1].set_title("Kvadratna greska"); ax[1].legend()
plt.tight_layout(); plt.show()

print("Kada je y=1, a model kaze p=0.01:")
print(f"   cross-entropy : {-np.log(0.01):.3f}   <- ogromna kazna")
print(f"   kvadratna     : {0.5*(0.01-1)**2:.3f}   <- blaga, gradijent skoro nestaje")
""")

md(C, r"""
## Gradient Descent

Iterativni algoritam optimizacije koji traži vrednosti $w$ i $b$ koje **minimizuju
funkciju troška**.

**Ideja:** izračunaj gradijent funkcije troška, pa pomeri parametre u smeru **suprotnom**
od gradijenta.

$$w := w - \alpha \frac{\partial J(w,b)}{\partial w} \qquad
b := b - \alpha \frac{\partial J(w,b)}{\partial b}$$

gde je $\alpha$ **korak učenja** (learning rate).

- **veliki gradijent** → veliki korak
- **mali gradijent** → mali korak

Iteracijama se približavamo minimumu. Gradient Descent je osnovni mehanizam učenja u
neuronskim mrežama.
""")

code(C, r"""
def J(w): return (w - 3) ** 2 + 2          # jednostavna funkcija troska
def dJ(w): return 2 * (w - 3)              # njen gradijent

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
ww = np.linspace(-2, 8, 200)
for a, alfa in zip(ax, (0.05, 0.3, 1.02)):
    a.plot(ww, J(ww), color="gray", lw=1.5)
    w = -1.0
    putanja = [w]
    for _ in range(14):
        w = w - alfa * dJ(w)
        putanja.append(w)
    putanja = np.array(putanja)
    a.plot(putanja, J(putanja), "o-", color="#C44E52", ms=5, lw=1.2)
    a.set_title(f"alpha = {alfa}\nkraj: w = {w:.3f}")
    a.set_xlabel("w"); a.set_ylim(0, 40)
plt.tight_layout(); plt.show()
print("alpha premali -> sporo. alpha dobar -> brzo konvergira.")
print("alpha prevelik -> koraci preskacu minimum i DIVERGIRA.")
""")

md(C, r"""
## Računski graf, forward i backward propagation

Izračunavanja u mreži se predstavljaju **računskim grafom**.

| korak | šta radi |
|---|---|
| **Forward propagation** | izračunavanje izlaza mreže prolaskom ulaza kroz slojeve |
| **Backpropagation** | izračunavanje gradijenata funkcije troška u odnosu na parametre, propagacijom **unazad** |

Računski graf prikazuje redosled operacija, omogućava efikasno računanje gradijenata i
ažuriranje težina pomoću Gradient Descent-a.

### Računanje u sloju

Svaki neuron računa:
$$z_i^{[l]} = \big(w_i^{[l]}\big)^\top x + b_i^{[l]}, \qquad a_i^{[l]} = \sigma\big(z_i^{[l]}\big)$$

Neuroni u istom sloju rade **paralelno**, a izlaz jednog sloja je **ulaz** sledećem.
""")

code(C, r"""
# forward i backward rucno, na jednom neuronu, preko GradientTape
x = tf.constant([[1.0, 2.0]])
y = tf.constant([[1.0]])
w = tf.Variable([[0.5], [-0.3]])
b = tf.Variable([[0.1]])

with tf.GradientTape() as tape:
    z = tf.matmul(x, w) + b                       # FORWARD: linearni deo
    a = tf.sigmoid(z)                             # FORWARD: aktivacija
    L = -(y * tf.math.log(a) + (1-y) * tf.math.log(1-a))    # cross-entropy

dw, db = tape.gradient(L, [w, b])                 # BACKWARD

print(f"FORWARD:")
print(f"   z = w'x + b   = {z.numpy()[0,0]:.4f}")
print(f"   a = sigmoid(z)= {a.numpy()[0,0]:.4f}")
print(f"   L (loss)      = {L.numpy()[0,0]:.4f}")
print(f"\nBACKWARD (gradijenti):")
print(f"   dL/dw = {dw.numpy().ravel().round(4)}")
print(f"   dL/db = {db.numpy().ravel().round(4)}")
print(f"\nAzuriranje sa alpha=0.1:  w_novo = {(w - 0.1*dw).numpy().ravel().round(4)}")
""")

md(C, r"""
## Aktivacione funkcije

Aktivacione funkcije uvode **nelinearnost**. Bez njih bi neuronska mreža bila
**ekvivalentna linearnom modelu**, bez obzira na broj slojeva.

| funkcija | formula | izlaz | gde se koristi |
|---|---|---|---|
| **Sigmoid** | $\sigma(z) = \dfrac{1}{1+e^{-z}}$ | $(0, 1)$ | izlazni sloj, binarna klasifikacija |
| **ReLU** | $\max(0, z)$ | $[0, \infty)$ | **najčešća u skrivenim slojevima** |
| **Tanh** | $\tanh(z)$ | $(-1, 1)$ | centrirana oko nule, ređe od ReLU |

**Softmax** se koristi u izlaznom sloju za **višeklasnu** klasifikaciju:

$$\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}$$

Pretvara izlaze u verovatnoće u $(0,1)$ čiji je **zbir 1**.

> **Sigmoid bira između dve opcije, Softmax između više.**
""")

code(C, r"""
z = np.linspace(-6, 6, 300)
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for ime, f, boja in [("sigmoid", 1/(1+np.exp(-z)), "#4C72B0"),
                     ("ReLU", np.maximum(0, z), "#C44E52"),
                     ("tanh", np.tanh(z), "#55A868")]:
    ax[0].plot(z, f, lw=2.5, label=ime, color=boja)
ax[0].axhline(0, color="k", lw=0.8); ax[0].axvline(0, color="k", lw=0.8)
ax[0].set_title("Aktivacione funkcije"); ax[0].legend(); ax[0].set_ylim(-1.5, 4)

logiti = np.array([2.0, 1.0, 0.1, -1.0])
sm = np.exp(logiti) / np.exp(logiti).sum()
ax[1].bar(range(4), sm, color="#4C72B0")
ax[1].set_xticks(range(4)); ax[1].set_xticklabels([f"klasa {i}" for i in range(4)])
ax[1].set_ylabel("verovatnoca"); ax[1].set_title(f"Softmax — zbir = {sm.sum():.4f}")
plt.tight_layout(); plt.show()
print(f"Logiti  : {logiti}")
print(f"Softmax : {sm.round(4)}   zbir = {sm.sum():.6f}")
""")

code(C, r"""
# dokaz: bez aktivacije mreza je samo linearan model
Xm, ym = make_moons(n_samples=800, noise=0.22, random_state=RS)
Xm_tr, Xm_te, ym_tr, ym_te = train_test_split(Xm, ym, test_size=0.3, random_state=RS)

def napravi(aktivacija):
    m = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(2,)),
        tf.keras.layers.Dense(32, activation=aktivacija),
        tf.keras.layers.Dense(32, activation=aktivacija),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    m.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return m

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for a, akt in zip(ax, [None, "relu"]):
    m = napravi(akt)
    m.fit(Xm_tr, ym_tr, epochs=80, batch_size=32, verbose=0)
    XX, YY = np.meshgrid(np.linspace(-2, 3, 200), np.linspace(-1.5, 2, 200))
    Z = m.predict(np.c_[XX.ravel(), YY.ravel()], verbose=0).reshape(XX.shape)
    a.contourf(XX, YY, Z, alpha=0.3, cmap="coolwarm", levels=20)
    a.scatter(Xm[:, 0], Xm[:, 1], c=ym, s=12, cmap="coolwarm", edgecolor="k", linewidth=0.2)
    t = m.evaluate(Xm_te, ym_te, verbose=0)[1]
    a.set_title(f"aktivacija = {akt}\ntacnost {t:.3f}")
    a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()
print("Bez aktivacije granica je PRAVA — tri linearna sloja daju opet linearan model.")
""")

md(C, r"""
## Parametri i hiperparametri u neuronskim mrežama

| **parametri** (uče se) | **hiperparametri** (biramo ih) |
|---|---|
| težine $W$ | broj skrivenih slojeva |
| bias vrednosti $b$ | broj neurona po sloju |
| | funkcija aktivacije |
| | learning rate $\alpha$ |
| | broj epoha |
| | batch size |

Parametri se ažuriraju optimizacionim algoritmom (Gradient Descent, SGD, Momentum,
RMSProp, **Adam**).

## Overfitting i underfitting kod mreža

| | trening greška | test greška |
|---|---|---|
| **underfitting** | visoka | visoka |
| **overfitting** | **vrlo niska** | visoka |

### Pet tehnika za smanjenje overfittinga

1. **Više podataka** — veći i raznovrsniji skup
2. **Regularizacija (L1, L2)** — ograničava vrednosti težina
3. **Dropout** — nasumično isključuje neurone tokom treniranja
4. **Early stopping** — prekid kada validaciona greška počne da raste
5. **Smanjenje složenosti** — manje slojeva ili neurona

### L1 i L2 regularizacija

$$J_{\text{reg}} = J + \lambda \sum w^2 \quad (\text{L2, Ridge}) \qquad
J_{\text{reg}} = J + \lambda \sum \lvert w \rvert \quad (\text{L1, Lasso})$$

| | efekat |
|---|---|
| **L2** | kažnjava velike težine; najčešća u mrežama |
| **L1** | podstiče **retke** modele, može „ugasiti" težine na $\approx 0$ |

### Dropout

Nasumično **isključuje neurone tokom treniranja**, pa se mreža ne može osloniti na
pojedinačne neurone. Tokom **testiranja su svi neuroni aktivni**.
Tipične vrednosti: **0.2 – 0.5**.

### Early stopping

Prati se greška na trening i validacionom skupu. Kada validaciona greška prestane da opada
ili počne da raste, treniranje se zaustavlja. Ne zahteva izmene arhitekture.
""")

code(C, r"""
def treniraj(ime, slojevi, epohe=200, **fit_kw):
    m = tf.keras.Sequential([tf.keras.layers.Input(shape=(Xtr_s.shape[1],))] + slojevi)
    m.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    h = m.fit(Xtr_s, ytr, validation_data=(Xte_s, yte), epochs=epohe,
              batch_size=16, verbose=0, **fit_kw)
    return ime, m, h

D = tf.keras.layers.Dense
Dr = tf.keras.layers.Dropout
l2 = tf.keras.regularizers.l2

rezultati = [
    treniraj("bez regularizacije", [D(128, activation="relu"), D(128, activation="relu"), D(1, activation="sigmoid")]),
    treniraj("L2 regularizacija", [D(128, activation="relu", kernel_regularizer=l2(0.01)),
                                   D(128, activation="relu", kernel_regularizer=l2(0.01)), D(1, activation="sigmoid")]),
    treniraj("Dropout 0.4", [D(128, activation="relu"), Dr(0.4),
                             D(128, activation="relu"), Dr(0.4), D(1, activation="sigmoid")]),
]

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for a, (ime, m, h) in zip(ax, rezultati):
    a.plot(h.history["loss"], label="trening", color="#4C72B0")
    a.plot(h.history["val_loss"], label="validacija", color="#C44E52")
    razmak = h.history["val_loss"][-1] - h.history["loss"][-1]
    a.set_title(f"{ime}\nrazmak na kraju = {razmak:.3f}")
    a.set_xlabel("epoha"); a.set_ylabel("gubitak"); a.legend()
plt.tight_layout(); plt.show()
print("Veci razmak izmedju krivih = jaci overfitting.")
""")

code(C, r"""
# early stopping
rano = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=15,
                                        restore_best_weights=True)
ime, m, h = treniraj("early stopping", [D(128, activation="relu"), D(128, activation="relu"),
                                        D(1, activation="sigmoid")],
                     epohe=300, callbacks=[rano])

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(h.history["loss"], label="trening", color="#4C72B0")
ax.plot(h.history["val_loss"], label="validacija", color="#C44E52")
naj = int(np.argmin(h.history["val_loss"]))
ax.axvline(naj, color="#55A868", ls="--", label=f"najbolja epoha = {naj}")
ax.set_xlabel("epoha"); ax.set_ylabel("gubitak"); ax.legend()
ax.set_title("Early stopping vraca tezine iz najbolje epohe")
plt.tight_layout(); plt.show()
print(f"Treniranje prekinuto posle {len(h.history['loss'])} epoha (limit je bio 300).")
print(f"Tacnost na testu: {m.evaluate(Xte_s, yte, verbose=0)[1]:.4f}")
""")

md(C, r"""
## Ograničenja neuronskih mreža

1. **Potreba za velikom količinom podataka**
2. **Veća računarska zahtevnost**
3. **Teža interpretabilnost** — crna kutija
4. **Osetljivost na hiperparametre**

> **Neuronske mreže nisu uvek najbolji izbor.** Na tabelarnim podacima srednje veličine
> ansambl metode (predavanje 12) često daju bolji rezultat uz manje truda.
""")

code(C, r"""
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=300, random_state=RS).fit(Xtr, ytr)
print(f"Neuronska mreza (MLP) : {m.evaluate(Xte_s, yte, verbose=0)[1]:.4f}")
print(f"Random Forest         : {rf.score(Xte, yte):.4f}")
print(f"\nParametara u mrezi: {m.count_params():,}")
print("-> Na tabelarnim podacima ove velicine, RF je jednako dobar uz mnogo manje podesavanja.")
""")
upisi(C, "10_duboko_ucenje.ipynb")

# ═══════════════════════════════════════════════════════ 11 CNN
C = novi()
md(C, r"""
# 11. Konvolucione neuronske mreže (CNN)

## Računarski vid

**Računarski vid** je oblast veštačke inteligencije koja omogućava računarima da
interpretiraju, razumeju i izvuku informacije iz **vizuelnih podataka** (slike, video,
kamere). Cilj je da mašine „vide" i razumeju svet na način sličan ljudskoj percepciji.

Primene: klasifikacija slika, detekcija objekata, segmentacija, prepoznavanje lica i
emocija, autonomna vozila, medicinska dijagnostika, maloprodaja (Amazon Go),
poljoprivreda, AI-generisane slike.

## Zašto klasični ML ne radi dobro na slikama

1. Slike imaju **veoma veliki broj ulaznih karakteristika** (piksela)
2. **Gubi se prostorna struktura slike kada se pikseli vektorizuju**
3. Klasični algoritmi ne koriste **lokalne obrasce** (ivice, teksture)
4. Ne skaliraju dobro na visoke dimenzije
5. Ručno izdvajanje karakteristika je složeno, neefikasno i zavisi od domena

### Izazov dimenzionalnosti — konkretno

| slika | broj ulaznih karakteristika |
|---|---|
| $64 \times 64 \times 3$ | 12.288 |
| $1000 \times 1000 \times 3$ | **~3 miliona** |

Potpuno povezan sloj sa 1000 neurona nad slikom od 3 miliona piksela ima
**~3 milijarde parametara** → ogromna memorija, sporo treniranje, neefikasan model.

### Rešenje — CNN

Konvolucija **deli težine** između različitih delova slike, čime se broj parametara
drastično smanjuje. CNN koristi **prostornu strukturu** slike i fokusira se na
**lokalne obrasce**.
""")

code(C, r"""
import warnings, os
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

plt.rcParams["figure.figsize"] = (9, 4.5); plt.rcParams["figure.dpi"] = 110
RS = 42
np.random.seed(RS); tf.random.set_seed(RS)

for h, w, c in [(28, 28, 1), (64, 64, 3), (1000, 1000, 3)]:
    ul = h * w * c
    par = ul * 1000 + 1000
    print(f"slika {h}x{w}x{c}: {ul:>9,} ulaza  ->  FC sloj sa 1000 neurona = {par:>15,} parametara")
""")

md(C, r"""
## Konvoluciona operacija

Osnovni element CNN-a. Koristi se za otkrivanje **lokalnih obrazaca**, kao što su ivice.

**Hijerarhija osobina:**

| nivo | šta detektuje |
|---|---|
| **niski** | ivice, kontrasti |
| **srednji** | delovi objekata (oči, uši, nos) |
| **visoki** | kompletna struktura objekta (lice) |

### Veličina izlaza

$$\text{Output} = \left\lfloor \frac{n + 2p - f}{s} \right\rfloor + 1$$

| oznaka | značenje |
|---|---|
| $n$ | dimenzija ulaza |
| $f$ | veličina filtera (kernela) |
| $p$ | veličina padding-a |
| $s$ | stride |

**Primer:** $n=6$, $f=3$, $p=0$, $s=1$ → $\frac{6+0-3}{1}+1 = 4$

> **Važno:** vrednosti u kernelu **nisu fiksne** — one se **uče tokom treniranja**, kao i
> sve druge težine mreže.
""")

code(C, r"""
def konvolucija(slika, kernel, stride=1, padding=0):
    'Rucna 2D konvolucija — da se vidi sta operacija radi.'
    if padding > 0:
        slika = np.pad(slika, padding, mode="constant")
    n, f = slika.shape[0], kernel.shape[0]
    izlaz_dim = (n - f) // stride + 1
    izlaz = np.zeros((izlaz_dim, izlaz_dim))
    for i in range(izlaz_dim):
        for j in range(izlaz_dim):
            isecak = slika[i*stride:i*stride+f, j*stride:j*stride+f]
            izlaz[i, j] = np.sum(isecak * kernel)      # skalarni proizvod
    return izlaz

ulaz = np.array([[10,10,10,0,0,0]]*6, dtype=float)      # vertikalna ivica u sredini
kernel_v = np.array([[1,0,-1],[1,0,-1],[1,0,-1]], float)

izlaz = konvolucija(ulaz, kernel_v)
print(f"Ulaz {ulaz.shape} * kernel {kernel_v.shape}, stride=1, padding=0")
print(f"Izlaz: (6 + 0 - 3)/1 + 1 = {izlaz.shape}\n")

fig, ax = plt.subplots(1, 3, figsize=(12, 3.2))
for a, (d, t) in zip(ax, [(ulaz, "ulazna slika"), (kernel_v, "kernel (detektor ivice)"),
                          (izlaz, "izlaz — feature map")]):
    im = a.imshow(d, cmap="gray"); a.set_title(t); a.set_xticks([]); a.set_yticks([])
    for (i, j), v in np.ndenumerate(d):
        a.text(j, i, f"{v:.0f}", ha="center", va="center",
               color="red", fontsize=9, fontweight="bold")
plt.tight_layout(); plt.show()
print("-> Kernel je detektovao vertikalnu ivicu: izlaz je nula svuda osim na prelazu.")
""")

md(C, r"""
## Padding

**Problem osnovne konvolucije (bez padding-a):**

1. dimenzije izlaza se **smanjuju** sa svakim slojem ($6\times6 \to 4\times4$)
2. pikseli na **ivicama** slike se nedovoljno koriste
3. gubi se informacija sa ivica

**Rešenje — padding:** dodavanje ivica (najčešće nula) oko ulazne slike. Omogućava
očuvanje dimenzija, ravnopravno korišćenje ivica i **dublje** CNN arhitekture.

| tip | padding | rezultat |
|---|---|---|
| **Valid** | $p = 0$ | dimenzije se smanjuju |
| **Same** | $p$ takav da izlaz = ulaz | dimenzije očuvane |

Najčešće veličine filtera: $3\times3$, $5\times5$, $7\times7$.
U praksi se najčešće koristi **$3\times3$ sa same padding-om**.
""")

code(C, r"""
print(f"{'ulaz':>6} {'filter':>7} {'padding':>8} {'stride':>7} {'izlaz':>7}  tip")
print("-" * 52)
for n, f, p, s in [(6,3,0,1), (6,3,1,1), (7,3,0,2), (28,3,1,1), (28,3,0,1), (28,5,2,1)]:
    izl = (n + 2*p - f)//s + 1
    tip = "same" if izl == n else "valid"
    print(f"{n:>6} {f:>7} {p:>8} {s:>7} {izl:>7}  {tip}")

valid = konvolucija(ulaz, kernel_v, padding=0)
same = konvolucija(ulaz, kernel_v, padding=1)
print(f"\nValid konvolucija: {ulaz.shape} -> {valid.shape}")
print(f"Same konvolucija : {ulaz.shape} -> {same.shape}   (dimenzija ocuvana)")
""")

md(C, r"""
## Strided convolutions

**Stride** ($s$) određuje za koliko piksela se filter pomera po širini i visini.

**Zašto se koristi:**
- smanjuje prostorne dimenzije izlazne mape osobina
- kontroliše veličinu izlaza **bez** pooling sloja
- smanjuje računarsku složenost

**Veći stride ⇒ manji izlaz.**

## 3D konvolucija

Do sada smo posmatrali 2D slike u nijansama sive. Kod **RGB** slika treća dimenzija su
kanali boja.

**Ključni uslov:** broj kanala **ulaza** mora biti jednak broju kanala **filtera**.

Primer: ulaz $6\times6\times3$, filter $3\times3\times3$ → izlaz $4\times4\times1$.

Filter se primenjuje na sve kanale istovremeno, a rezultati se **sabiraju**. Iako je filter
3D, izlaz jedne konvolucije je i dalje **2D mapa osobina**.

> **Više filtera → više izlaznih kanala.** Svaki filter proizvodi jednu feature mapu,
> a mape se slažu po dubini.

Svaka feature mapa ima **sopstveni bias** (skalar) koji se dodaje svim elementima, pa se
na rezultat primenjuje aktivaciona funkcija (ReLU).
""")

code(C, r"""
ulaz3d = np.random.RandomState(RS).rand(6, 6, 3)
filter3d = np.random.RandomState(1).randn(3, 3, 3)

n, f = 6, 3
izlaz_dim = n - f + 1
rez = np.zeros((izlaz_dim, izlaz_dim))
for i in range(izlaz_dim):
    for j in range(izlaz_dim):
        rez[i, j] = np.sum(ulaz3d[i:i+f, j:j+f, :] * filter3d)   # sabira SVE kanale

print(f"Ulaz     : {ulaz3d.shape}  (6x6 RGB)")
print(f"Filter   : {filter3d.shape}  (3x3, mora imati ISTI broj kanala)")
print(f"Izlaz    : {rez.shape}  <- 2D, jedna feature mapa")
print(f"\nSa 8 filtera izlaz bi bio: ({izlaz_dim}, {izlaz_dim}, 8)")
""")

md(C, r"""
## Pooling sloj (subsampling)

Pooling sloj **smanjuje prostorne dimenzije** feature mapa (širinu i visinu):

- zadržava najvažnije informacije
- smanjuje broj parametara i računsku složenost
- povećava otpornost na **male translacije** u slici

| vrsta | operacija | učestalost |
|---|---|---|
| **Max Pooling** | bira **najveću** vrednost | najčešći u CNN-ovima |
| **Average Pooling** | računa **prosek** | ređe u praksi |

> **Pooling ne uči parametre** — on samo sažima informacije.
""")

code(C, r"""
mapa = np.array([[1,3,2,4],[5,6,7,8],[9,2,1,3],[4,5,6,7]], float)

def pooling(x, k=2, s=2, tip="max"):
    d = (x.shape[0]-k)//s + 1
    o = np.zeros((d, d))
    for i in range(d):
        for j in range(d):
            w = x[i*s:i*s+k, j*s:j*s+k]
            o[i, j] = w.max() if tip == "max" else w.mean()
    return o

fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
for a, (d, t) in zip(ax, [(mapa, "feature mapa 4x4"),
                          (pooling(mapa, tip="max"), "Max Pooling 2x2 -> 2x2"),
                          (pooling(mapa, tip="avg"), "Average Pooling 2x2 -> 2x2")]):
    a.imshow(d, cmap="Blues"); a.set_title(t); a.set_xticks([]); a.set_yticks([])
    for (i, j), v in np.ndenumerate(d):
        a.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=11, fontweight="bold")
plt.tight_layout(); plt.show()
print("Pooling NEMA parametre koji se uce — samo sazima.")
""")

md(C, r"""
## Kompletna CNN arhitektura

Tipičan raspored: `Conv → ReLU → Pool` (ponovljeno) → `Flatten` → `Dense` → izlaz.
""")

code(C, r"""
digits = load_digits()
X = digits.images[..., None] / 16.0          # 8x8x1, skalirano na [0,1]
y = digits.target
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=RS, stratify=y)

cnn = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(8, 8, 1)),
    tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu"),
    tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu"),
    tf.keras.layers.MaxPooling2D(2),
    tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu"),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(10, activation="softmax"),      # 10 cifara -> softmax
])
cnn.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
cnn.summary()
""")

code(C, r"""
h = cnn.fit(Xtr, ytr, validation_split=0.2, epochs=30, batch_size=64, verbose=0)
print(f"Tacnost na testu: {cnn.evaluate(Xte, yte, verbose=0)[1]:.4f}")

# poredjenje sa istom mrezom koja NE koristi prostornu strukturu
mlp = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(8, 8, 1)),
    tf.keras.layers.Flatten(),                            # spljosti — gubi prostor!
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(10, activation="softmax"),
])
mlp.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
mlp.fit(Xtr, ytr, validation_split=0.2, epochs=30, batch_size=64, verbose=0)

print(f"\n{'model':<28} {'parametara':>12} {'tacnost':>9}")
print("-" * 52)
print(f"{'CNN (cuva prostor)':<28} {cnn.count_params():>12,} {cnn.evaluate(Xte, yte, verbose=0)[1]:>9.4f}")
print(f"{'MLP (Flatten na pocetku)':<28} {mlp.count_params():>12,} {mlp.evaluate(Xte, yte, verbose=0)[1]:>9.4f}")
""")

code(C, r"""
# sta su filteri prvog sloja naucili
w = cnn.layers[0].get_weights()[0]           # (3, 3, 1, 32)
fig, ax = plt.subplots(3, 8, figsize=(11, 4.2))
for i, a in enumerate(ax.ravel()):
    if i < w.shape[-1]:
        a.imshow(w[:, :, 0, i], cmap="RdBu_r")
        a.set_title(f"f{i}", fontsize=7)
    a.axis("off")
plt.suptitle("Nauceni filteri prvog konvolucionog sloja (3x3)", y=0.99)
plt.tight_layout(); plt.show()
print("Vrednosti u filterima NISU zadate — mreza ih je naucila iz podataka.")
""")

code(C, r"""
# feature mape — sta filter "vidi" na konkretnoj slici
izdvoji = tf.keras.Model(cnn.inputs, cnn.layers[0].output)
slika = Xte[0:1]
mape = izdvoji.predict(slika, verbose=0)[0]

fig, ax = plt.subplots(2, 9, figsize=(13, 3.2))
ax[0, 0].imshow(slika[0, :, :, 0], cmap="gray_r")
ax[0, 0].set_title(f"ulaz\n(cifra {yte[0]})", fontsize=8)
for i, a in enumerate(ax.ravel()[1:]):
    if i < mape.shape[-1]:
        a.imshow(mape[:, :, i], cmap="viridis")
        a.set_title(f"mapa {i}", fontsize=7)
for a in ax.ravel(): a.axis("off")
plt.tight_layout(); plt.show()
""")

md(C, r"""
## Poznate CNN arhitekture

| arhitektura | godina | doprinos |
|---|---|---|
| **LeNet-5** | 1998 | jedna od prvih; prepoznavanje rukom pisanih cifara; `Conv → Pool → FC` |
| **AlexNet** | 2012 | pobednik ImageNet-a; popularizovala duboko učenje; uvela **ReLU**, **dropout**, rad na **GPU** |
| **VGGNet** | 2014 | duboka mreža sa malim **3×3** filterima; jednostavna, ali mnogo parametara |
| **GoogLeNet / Inception** | 2014 | Inception blokovi; smanjuje broj parametara |
| **ResNet** | 2015 | **residual (skip) connections**; omogućava treniranje mreža sa 50+, 100+ slojeva |

## Sažetak

- **konvolucija** — deli težine, hvata lokalne obrasce, drastično smanjuje broj parametara
- **padding** — čuva dimenzije i ivične piksele
- **stride** — kontroliše veličinu izlaza
- **pooling** — sažima, ne uči parametre, daje otpornost na male pomeraje
- filteri se **uče**, ne zadaju
""")
upisi(C, "11_cnn.ipynb")
print("\nGotovo za 10-11.")
