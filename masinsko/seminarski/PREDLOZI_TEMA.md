# Predlozi tema i skupova podataka

## Kako izabrati temu

Dobra tema ima tri osobine:

1. **problem se ne rešava jednim `if`-om** — pravilo mora da se uči iz podataka
2. **podaci postoje i dostupni su** — proveri to **pre** nego što se vežeš za temu
3. **rezultat nekome nešto znači** — može se protumačiti u domenu

---

## Gde tražiti podatke

| izvor | šta ima | napomena |
|---|---|---|
| [Kaggle Datasets](https://www.kaggle.com/datasets) | najveći izbor | traži nalog |
| [UCI ML Repository](https://archive.ics.uci.edu/) | klasični skupovi za nastavu | mali i čisti |
| [OpenML](https://www.openml.org/) | hiljade skupova | ima Python API |
| `sklearn.datasets` | ugrađeni skupovi | bez preuzimanja, ali preterano poznati |
| javni API-ji | sopstveno prikupljanje | **najjača opcija** — vidi ispod |
| [data.gov.rs](https://data.gov.rs/) | otvoreni podaci Srbije | domaći kontekst |

---

## Predlozi tema po tipu problema

### Binarna klasifikacija

| tema | skup | zašto je dobra |
|---|---|---|
| Predviđanje odliva korisnika (churn) | Telco Customer Churn (Kaggle) | neuravnotežene klase → opravdava F1 i PR-AUC |
| Odobravanje kredita | German Credit (UCI) | mešani tipovi obeležja, jasna interpretacija |
| Detekcija prevare | Credit Card Fraud (Kaggle) | ekstremno neuravnotežen (0,17%) — odlična tema za evaluaciju |
| Predviđanje ishoda sportskog meča | javni API-ji | zahteva pažljivo preprocesiranje vremena |

### Višeklasna klasifikacija

| tema | skup |
|---|---|
| Klasifikacija vrste pokrivača zemljišta | Covertype (UCI) — veliki, 54 obeležja |
| Prepoznavanje aktivnosti sa senzora telefona | UCI HAR Dataset |
| Klasifikacija muzičkog žanra | GTZAN / Spotify audio features |

### Regresija

| tema | skup |
|---|---|
| Predviđanje cene nekretnine | Ames Housing, California Housing |
| Potrošnja energije | UCI Energy / Individual Household Power |
| Predviđanje potražnje za deljenje bicikala | Bike Sharing (UCI) — ima i vremensku komponentu |

### Rad sa tekstom

| tema | skup |
|---|---|
| Analiza sentimenta recenzija | IMDB, Amazon Reviews, Steam recenzije preko API-ja |
| Klasifikacija vesti po kategoriji | 20 Newsgroups (`sklearn.datasets`) |
| Detekcija spama | SMS Spam Collection (UCI) |

### Slike (za CNN)

| tema | skup |
|---|---|
| Klasifikacija cifara | `load_digits`, MNIST |
| Klasifikacija odeće | Fashion-MNIST |
| Detekcija bolesti biljaka | PlantVillage |

---

## Najjača opcija — sopstveno prikupljanje podataka

Rad u kojem si **sam prikupio podatke** je uvek jači od onog sa gotovog Kaggle skupa, jer:

- pokazuje da razumeš ceo tok, ne samo modelovanje
- tema je originalna, nema gotovih rešenja na internetu
- preprocesiranje je stvarno, a ne dekorativno

Javni API-ji koji ne traže plaćanje:

| API | šta daje |
|---|---|
| chess.com / Lichess | partije, rejtinzi, statistika |
| OpenDota | Dota 2 mečevi, detaljne statistike igrača |
| Steam Web API | recenzije igara, sati igranja |
| Reddit API | objave i komentari |
| OpenWeather, NASA, Eurostat | vremenski i statistički podaci |

**Napomena:** ako prikupljaš podatke, počni **odmah**. Prikupljanje obično traje danima
zbog ograničenja API-ja, i to je najčešći razlog kašnjenja sa radom.

---

## Šta izbegavati

| tema | zašto |
|---|---|
| Iris, Titanic bez dodatnog ugla | previše obrađeni; svi modeli daju isto |
| skup sa manje od 200 uzoraka | rezultat je šum, razlike nisu statistički značajne |
| ciljna promenljiva izvedena iz jednog obeležja | model dostiže 100% i nema šta da se tumači |
| skup bez ijednog kategoričkog ili nedostajućeg podatka | preprocesiranje ostaje prazno poglavlje |
