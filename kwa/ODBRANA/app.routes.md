# Rute aplikacije (`app.routes.ts`)

## Pregled ruta

| URL | Komponenta | Zaštićena? |
|---|---|---|
| `/` | → preusmerenje na `/projekti` | — |
| `/login` | `LoginComponent` | ne (jedina javna) |
| `/projekti` | `ProjektiComponent` | **da** |
| `/projekti/:id` | `ProjekatDetaljiComponent` | **da** |
| `/projekti/:projekatId/zadaci/novi` | `ZadatakFormaComponent` | **da** |
| `/projekti/:projekatId/zadaci/:id/izmena` | `ZadatakFormaComponent` | **da** |
| `/statistika` | `StatistikaComponent` | **da** |
| `**` (sve ostalo) | → preusmerenje na `/projekti` | — |

Specifikacija traži zaštitu barem za: prikaz projekata, detalje projekta i forme za dodavanje/izmenu zadataka — sve tri su pokrivene, plus statistika.

## Ključne odluke

- **Hijerarhijski URL-ovi** (`/projekti/3/zadaci/novi`) — URL sam govori kontekst: "novi zadatak u projektu 3". Forma iz parametara rute čita i `projekatId` (kom projektu zadatak pripada) i `id` zadatka (režim izmene).
- **Ista komponenta za dodavanje i izmenu** — `ZadatakFormaComponent` opslužuje obe rute; režim prepoznaje po prisustvu parametra `:id`. Manje dupliranog koda, a specifikacija ionako traži jednu "komponentu za formu za dodavanje/izmenu zadataka".
- **Redosled ruta je bitan** — Router uzima prvo poklapanje odozgo; specifičnije putanje (`projekti/:projekatId/zadaci/novi`) moraju biti definisane, jer bi inače `projekti/:id` "progutao" samo prvi segment. Wildcard `**` je uvek poslednji.
- **`pathMatch: 'full'` na praznoj putanji** — bez toga bi se prazna putanja poklapala sa početkom SVAKOG URL-a i preusmerenje bi se stalno okidalo.
