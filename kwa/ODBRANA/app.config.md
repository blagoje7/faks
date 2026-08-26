# Konfiguracija aplikacije (`app.config.ts`) i pokretanje (`main.ts`)

## Namena

`app.config.ts` sadrži **globalne provajdere** — servise i mehanizme koji su potrebni celoj
aplikaciji. U standalone Angularu (bez `NgModule`-a) to je zamena za nekadašnji `AppModule`
i njegov `imports` niz.

## Lanac pokretanja

```
index.html            <app-root></app-root>
   │
main.ts               bootstrapApplication(AppComponent, appConfig)
   │
app.config.ts         providers: [ provideRouter, provideHttpClient, provideAnimationsAsync ]
   │
AppComponent          toolbar + <router-outlet>
   │
Router                bira komponentu prema URL-u i ubacuje je u outlet
```

## Šta koji provajder radi

| Provajder | Bez njega | Gde se koristi |
|---|---|---|
| `provideRouter(routes)` | nema rutiranja; `<router-outlet>`, `routerLink` i guardovi ne rade | `app.routes.ts`, sve komponente sa navigacijom |
| `provideHttpClient()` | `NullInjectorError: No provider for HttpClient` — nijedan servis ne može da pošalje zahtev | `AuthService`, `ProjekatService`, `ZadatakService` |
| `provideAnimationsAsync()` | Material dialog i snackbar se ne prikazuju kako treba | `MatDialog`, `MatSnackBar`, `MatSelect` |

## Ključne odluke

- **Standalone pristup, bez ijednog `NgModule`-a** — svaka komponenta u svom `imports` nizu
  navodi šta koristi, a ovde stoji samo ono što je zajedničko celoj aplikaciji. To je
  preporučeni način od Angulara 15 naviše (podrazumevani od v19).
- **`provideAnimationsAsync()` umesto `provideAnimations()`** — animacije se učitavaju
  *asinhrono*, tek kada zatrebaju, pa početni paket aplikacije ostaje manji.
- **`.catch()` u `main.ts`** — greška pri pokretanju se ispisuje u konzolu umesto da
  aplikacija tiho ostane prazna.

## Česta pitanja

**Zašto ovde, a ne u komponenti?**
Zato što su ovo stvari koje deli cela aplikacija. Provajder naveden u `@Component({ providers: [...] })`
pravi **novu instancu po komponenti**; ovde želimo jednu instancu za sve.

**Šta bi ovde dodao ako bi aplikacija imala JWT prijavu?**
Interceptor koji svakom zahtevu dodaje token:
`provideHttpClient(withInterceptors([authInterceptor]))`.
