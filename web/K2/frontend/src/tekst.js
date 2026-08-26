// Srpski koristi različit oblik imenice uz 1, uz 2-4 i uz 5 i više,
// pri čemu brojevi 11-14 idu uz oblik za 5 i više.
export function oblik(broj, jednina, paukal, mnozina) {
  const poslednje_dve = broj % 100;
  const poslednja = broj % 10;

  if (poslednje_dve < 11 || poslednje_dve > 14) {
    if (poslednja === 1) return `${broj} ${jednina}`;
    if (poslednja >= 2 && poslednja <= 4) return `${broj} ${paukal}`;
  }

  return `${broj} ${mnozina}`;
}

export function dinari(vrednost) {
  return new Intl.NumberFormat("sr-RS", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(vrednost);
}

export function datum(vrednost) {
  const [godina, mesec, dan] = vrednost.split("-");
  return `${Number(dan)}. ${Number(mesec)}. ${godina}.`;
}

export function tekstBrisanjaNarudzbine(narudzbina) {
  if (!narudzbina.broj_stavki) {
    return `Obrisati narudžbinu ${narudzbina.broj}? Narudžbina nema stavki.`;
  }
  return (
    `Narudžbina ${narudzbina.broj} biće trajno obrisana zajedno sa svojim ` +
    `stavkama (${oblik(narudzbina.broj_stavki, "stavka", "stavke", "stavki")}). ` +
    `Nastaviti?`
  );
}
