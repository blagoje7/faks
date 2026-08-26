# Mašinsko učenje — skripta i materijali

```
masinsko/
├── skripta/                     13 notebook-a, po jedan za svako predavanje
│   ├── 01_uvod.ipynb
│   ├── 02_regresija.ipynb
│   ├── 03_knn.ipynb
│   ├── 04_stabla.ipynb
│   ├── 05_bayes.ipynb
│   ├── 06_svm.ipynb
│   ├── 07_evaluacija.ipynb
│   ├── 08_kmeans.ipynb
│   ├── 09_pca.ipynb
│   ├── 10_duboko_ucenje.ipynb
│   ├── 11_cnn.ipynb
│   ├── 12_ensemble.ipynb
│   └── 13_interpretabilnost.ipynb
│
└── seminarski/                  materijali za završni ispit
    ├── UPUTSTVO.md              pravila + šta se traži po tački + česte greške
    ├── PREDLOZI_TEMA.md         teme, skupovi podataka, gde ih naći
    ├── seminarski_sablon.ipynb  prazan šablon po tačkama pravila
    └── biblioteka_koda.ipynb    gotovi isečci koda za svaku fazu
```

## Skripta

Svaki notebook prati **teoriju sa odgovarajućeg predavanja**, uz izvršive primere koji tu
teoriju pokazuju na podacima.

Raspored unutar notebook-a: teorija u markdown ćeliji, pa kod koji je ilustruje, pa
tumačenje rezultata.

| # | tema | ključni primeri |
|---|---|---|
| 01 | Uvod | Mitchell Z/I/P, stratifikacija, k-fold, overfitting kroz dubinu stabla |
| 02 | Linearna i logistička regresija | RSS i R² ručno, dummy promenljive, reziduali, polinom, interakcija, log-transformacija, sigmoid, prag, ROC |
| 03 | kNN | uticaj k na granicu, mere rastojanja, skaliranje, demonstracija leakage-a, prokletstvo dimenzionalnosti |
| 04 | Stabla | entropija ručno, **Play Tennis sa IG = 0,246 vs 0,029**, vizualizacija stabla, post-pruning |
| 05 | Naivni Bajes | meningitis primer, Bayes-optimalna odluka, **Car Theft ručno + Laplas**, kada nezavisnost škodi |
| 06 | SVM | margina 2/‖w‖, dokaz da samo SV određuju rešenje, uticaj C, XOR, kerneli, gamma |
| 07 | Evaluacija | simulacija bias-variance nad 60 skupova, krive učenja i validacije, neuravnotežene klase, macro vs micro |
| 08 | k-Means | **ručna implementacija sa J po iteraciji**, lokalni optimum, elbow, majice, gde k-means pada |
| 09 | PCA | ortogonalne vs vertikalne greške, PCA ručno preko SVD, izbor broja komponenti, rekonstrukcija cifara |
| 10 | Duboko učenje | logistička regresija kao neuron, gradijenti preko `GradientTape`, dokaz da bez aktivacije mreža je linearna |
| 11 | CNN | **ručna konvolucija**, padding, stride, pooling, naučeni filteri, feature mape, CNN vs MLP |
| 12 | Ansambli | binomna formula greške ansambla, bootstrap 63,2%, **AdaBoost ručno kroz 4 iteracije**, Gradient Boosting na primeru sa predavanja |
| 13 | Interpretabilnost | Shapley sa 2 igrača (sinergija/disinergija), provera efikasnosti, waterfall, beeswarm, SHAP kod overfit modela |

Svih 13 notebook-a je **izvršeno i radi bez grešaka**.

## Pokretanje

Notebook-i koriste `scikit-learn`, `pandas`, `matplotlib`, `seaborn`, `xgboost`, `shap`
i `tensorflow`.

```bash
pip install scikit-learn pandas matplotlib seaborn xgboost shap tensorflow jupyter
jupyter notebook
```

## Seminarski

Materijali su građeni oko **pravila ispita** — šest tačaka koje projekat mora da obuhvati.

Redosled korišćenja:

1. **`PREDLOZI_TEMA.md`** — izaberi temu i proveri da podaci postoje
2. **`UPUTSTVO.md`** — pročitaj šta se traži po svakoj tački i koje su česte greške
3. **`seminarski_sablon.ipynb`** — piši rad u njemu; poglavlja već odgovaraju tačkama pravila
4. **`biblioteka_koda.ipynb`** — kopiraj gotove isečke za svaku fazu

Pred predaju prođi kontrolnu listu na kraju `UPUTSTVO.md`.
