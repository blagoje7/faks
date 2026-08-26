# Servis: AuthService (`auth.service.ts`)

## Namena

Centralno mesto za sve što se tiče prijave: proverava kredencijale, čuva podatke o prijavljenom korisniku tokom rada aplikacije (tehnički zahtev), obaveštava komponente o promeni stanja i podržava odjavu.

## Kako radi prijava

1. `LoginComponent` pozove `prijava(korisnickoIme, lozinka)`.
2. Servis šalje **GET** `http://localhost:3000/korisnici?korisnickoIme=X&lozinka=Y` — JSON Server filtrira kolekciju po query parametrima.
3. Neprazan niz ⇒ kredencijali su ispravni; `map` operator pretvara niz u prvog korisnika ili `null`.
4. Pri uspehu se korisnik upiše u `BehaviorSubject` i u `localStorage`.

## Ključne odluke i zašto

- **`BehaviorSubject` + javni `Observable`** — komponente (npr. toolbar u `AppComponent`) se pretplate na `korisnik$` i automatski se ažuriraju pri prijavi/odjavi, bez ručnog obaveštavanja. `BehaviorSubject` (a ne običan `Subject`) zato što pamti poslednju vrednost — novi pretplatnik odmah dobija trenutno stanje. Subject je privatan, spolja se vidi samo read-only `Observable` (enkapsulacija).
- **`localStorage`** (dodatna funkcionalnost iz specifikacije) — bez njega bi F5 odjavio korisnika, jer se memorija aplikacije briše pri osvežavanju. Početna vrednost Subject-a se čita iz storage-a u konstruktoru.
- **`providedIn: 'root'`** — jedan singleton za celu aplikaciju; svi (login, guard, toolbar) dele isto stanje.
- **Sinhrone metode `jePrijavljen()` / `trenutniKorisnik()`** — guard-u treba trenutna vrednost odmah, bez pretplate; `BehaviorSubject.value` to omogućava.

## Bezbednosna napomena (za odbranu)

Provera lozinke GET zahtevom sa lozinkom u query stringu je **simulacija** — JSON Server ne ume ništa pametnije. U pravoj aplikaciji: POST na `/login`, heširana lozinka na serveru, JWT token u odgovoru.

## Gde se koristi

- `LoginComponent` — poziva `prijava()`.
- `authGuard` — poziva `jePrijavljen()`.
- `AppComponent` — pretplata na `korisnik$` (prikaz imena, dugme za odjavu) i `odjava()`.
