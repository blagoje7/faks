# Seminarski rad — uputstvo

## Pravila ispita

> Završni ispit se realizuje kroz izradu projekta iz oblasti mašinskog učenja.
> Projekat treba da obuhvata sledeće:
>
> - odabir odgovarajućeg dataset-a
> - definisanje problema
> - preprocesiranje podataka
> - treniranje više modela mašinskog učenja po izboru
> - evaluaciju i poređenje rezultata modela
> - interpretaciju modela i dobijenih rezultata

## Šta se konkretno traži po tački

### 1. Odabir odgovarajućeg dataset-a

**Traži se:** skup podataka koji dozvoljava da se problem stvarno reši.

| kriterijum | preporuka |
|---|---|
| broj uzoraka | **najmanje ~500**, poželjno 1.000+ |
| broj obeležja | 5–50; ako ih je 100+, treba selekcija ili PCA |
| ciljna promenljiva | mora postojati i biti **jasno definisana** |
| poreklo | navesti izvor i licencu |

**Znaci lošeg izbora:**

- skup je toliko poznat da svi modeli daju 99% (iris, titanic bez dodatnog ugla)
- manje od 200 uzoraka — rezultat je šum
- ciljna promenljiva se trivijalno izvodi iz jednog obeležja

### 2. Definisanje problema

**Traži se:** jasno reći šta se predviđa, iz čega, i kako se meri uspeh.

Najkraći put je formulacija po Mitchell-u:

| | |
|---|---|
| **Zadatak (Z)** | šta model treba da uradi |
| **Iskustvo (I)** | koji podaci, koliko uzoraka |
| **Performanse (P)** | koja metrika i **zašto baš ona** |

Obavezno objasniti **zašto je to problem mašinskog učenja** — zašto se pravilo ne može
napisati eksplicitno. Ako se problem rešava jednim `if`-om, tema nije dobra.

### 3. Preprocesiranje podataka

**Traži se:** pripremiti podatke i **obrazložiti svaku odluku**.

| korak | kada |
|---|---|
| podela na train/test | **uvek, pre svega ostalog** |
| nedostajuće vrednosti | ako ih ima |
| kodiranje kategoričkih | ako ima tekstualnih kolona |
| skaliranje | obavezno za kNN, SVM, mreže, PCA |
| balansiranje klasa | ako su jako neuravnotežene |

**Najvažnije pravilo:** sve što se **uči** iz podataka (skaler, imputer, PCA, kodiranje)
mora se naučiti **samo na trening skupu**. Najsigurnije je koristiti `Pipeline`.

Nije dovoljno *uraditi* preprocesiranje — treba **napisati zašto**. Rečenica
*„nedostajuće vrednosti popunjene medijanom jer je raspodela iskošena"* vredi više od
tri ćelije koda bez objašnjenja.

### 4. Treniranje više modela

**Traži se:** više modela, iz **različitih porodica**.

Preporuka: **5–8 modela plus bazni**.

| porodica | model | predavanje |
|---|---|---|
| bazni | `DummyClassifier` | 07 |
| linearni | logistička / linearna regresija | 02 |
| instance-based | kNN | 03 |
| stabla | `DecisionTree` | 04 |
| probabilistički | `GaussianNB` | 05 |
| margine | SVM | 06 |
| ansambli | RandomForest, XGBoost, Voting, Stacking | 12 |
| duboko učenje | MLP | 10 |

**Bazni model je obavezan.** Bez njega se ne zna šta je „loše" — 90% tačnosti ne znači
ništa ako 90% uzoraka pripada jednoj klasi.

Svi modeli moraju biti obučeni i ocenjeni **istim postupkom**, inače poređenje nije pošteno.

### 5. Evaluacija i poređenje

**Traži se:** uporediti modele istim metrikama i prikazati pregledno.

Obavezno:

- **zbirna tabela** svih modela
- **matrica konfuzije** najboljeg modela
- bar jedna **kriva** (ROC ili PR)
- rezultat sa **standardnom devijacijom** iz kros-validacije

**Izbor metrike zavisi od raspodele klasa:**

| situacija | metrika |
|---|---|
| balansirane klase | tačnost je u redu |
| neuravnotežene klase | **F1**, balanced accuracy, **PR-AUC** |
| regresija | RMSE, MAE, R² |

### 6. Interpretacija

**Traži se:** objasniti **zašto** model donosi odluke koje donosi.

Preporuka: **bar dve metode**, jedna model-specifična i jedna model-agnostička.

| metoda | tip |
|---|---|
| koeficijenti / `feature_importances_` | model-specifična |
| permutaciona važnost | model-agnostička |
| **SHAP** | model-agnostička |
| PDP / ICE | model-agnostička |

Nije dovoljno nacrtati SHAP grafik — treba ga **protumačiti rečima**. Da li najvažnija
obeležja imaju smisla u domenu? Ako obeležje bez veze sa problemom ispadne najvažnije, to
je često znak **curenja informacija**.

---

## Struktura rada

Koristi `seminarski_sablon.ipynb` — poglavlja već odgovaraju tačkama pravila.

```
1. Definisanje problema
2. Odabir dataset-a
3. Istraživačka analiza (EDA)
4. Preprocesiranje
5. Treniranje modela
6. Evaluacija i poređenje
7. Interpretacija
8. Zaključak
```

Poglavlje 3 nije eksplicitno u pravilima, ali se podrazumeva — bez njega se ne može
opravdati nijedna odluka u preprocesiranju.

---

## Deset najčešćih grešaka

| # | greška | posledica |
|---|---|---|
| 1 | **skaliranje pre podele** na train/test | data leakage, lažno visok rezultat |
| 2 | **nema baznog modela** | ne zna se šta je dobar rezultat |
| 3 | **tačnost kod neuravnoteženih klasa** | model koji uvek predviđa većinsku klasu izgleda odlično |
| 4 | prag odlučivanja biran **na test skupu** | test prestaje da bude neviđen |
| 5 | grafici bez tumačenja | ne pokazuje se razumevanje |
| 6 | rezultat bez standardne devijacije | ne zna se da li je razlika stvarna |
| 7 | `fit_transform` pozvan i na test skupu | leakage |
| 8 | grupisani podaci uz običnu `KFold` | model prepoznaje grupu, ne obrazac |
| 9 | SHAP nacrtan, ali nije protumačen | tačka 6 nije ispunjena |
| 10 | zaključak bez navedenih **ograničenja** | prvo pitanje na odbrani |

---

## Kontrolna lista pre predaje

- [ ] svih 6 tačaka iz pravila ima svoje poglavlje
- [ ] naveden izvor podataka
- [ ] problem formulisan po Mitchell-u (Z / I / P)
- [ ] podela na train/test urađena **pre** svega ostalog
- [ ] preprocesiranje kroz `Pipeline`, sa obrazloženjem svake odluke
- [ ] **bazni model** uključen u poređenje
- [ ] najmanje 5 modela iz različitih porodica
- [ ] hiperparametri bar jednog modela podešeni `GridSearchCV`-om
- [ ] zbirna tabela + matrica konfuzije + bar jedna kriva
- [ ] metrika opravdana raspodelom klasa
- [ ] bar dve metode interpretacije, **protumačene rečima**
- [ ] zaključak sa navedenim **ograničenjima**
- [ ] notebook se izvršava **od početka do kraja bez grešaka** (Kernel → Restart & Run All)
- [ ] `random_state` postavljen svuda — rezultat je ponovljiv
