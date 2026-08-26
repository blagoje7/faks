# Guard: authGuard (`auth.guard.ts`)

## Namena

Sprečava pristup zaštićenim rutama korisnicima koji nisu prijavljeni — zahtev iz odeljka "Login i zaštita ruta". Štiti (vidi `app.routes.ts`): prikaz projekata, detalje projekta, forme za dodavanje/izmenu zadataka i statistiku.

## Kako radi

Angular Router poziva guard **pre** nego što aktivira rutu:

1. Guard preko `inject()` dohvata `AuthService` i `Router`.
2. `authService.jePrijavljen()` — sinhrona provera da li u `BehaviorSubject`-u postoji korisnik.
3. Prijavljen ⇒ vraća `true` (navigacija se nastavlja). Neprijavljen ⇒ vraća `UrlTree` za `/login` (Router sam preusmerava).

## Ključne odluke

- **Funkcionalni guard (`CanActivateFn`) umesto klase** — moderan pristup od Angular-a 15+: manje koda, nema klase ni konstruktora, a `inject()` obezbeđuje dependency injection unutar funkcije. Klasni `CanActivate` je deprecated.
- **Vraćanje `UrlTree` umesto `router.navigate()`** — preporuka Angular tima: guard deklarativno kaže "preusmeri tamo", bez sporednih efekata; Router garantovano izvrši tačno jednu navigaciju.
- **Jedan guard za sve zaštićene rute** — uslov je svuda isti ("da li je prijavljen"), pa se ista funkcija navodi u `canActivate` nizu svake zaštićene rute.

## Veza sa ostatkom aplikacije

- `app.routes.ts` — guard se prikačinje na rute kroz `canActivate: [authGuard]`.
- `AuthService` — izvor istine o tome da li je korisnik prijavljen.
