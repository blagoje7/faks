// oblik imenice uz broj: 1 stavka, 3 stavke, 5 stavki
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
    return `Obrisati narudzbinu ${narudzbina.broj}? Narudzbina nema stavki.`;
  }
  return (
    `Narudzbina ${narudzbina.broj} bice trajno obrisana zajedno sa svojim ` +
    `stavkama (${oblik(narudzbina.broj_stavki, "stavka", "stavke", "stavki")}). ` +
    `Nastaviti?`
  );
}
