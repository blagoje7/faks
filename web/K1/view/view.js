// VIEW - prikaz i korisnicki dogadjaji. Bez pravila domena i bez proracuna.

import { ApiGreska, narudzbinaApi, proizvodApi, stavkaApi } from "./api.js";

const stanje = {
  narudzbine: [],
  proizvodi: [],
  izabrana: null,
};

const el = (id) => document.getElementById(id);

const bez = (vrednost) =>
  String(vrednost).replace(
    /[&<>"]/g,
    (znak) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[znak]
  );

const brojevi = new Intl.NumberFormat("sr-RS", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const dinara = (iznos) => brojevi.format(iznos) + " RSD";
const datum = (iso) => iso.split("-").reverse().join(".") + ".";

/** 1 stavka, 3 stavke, 5 stavki. */
function stavki(koliko) {
  if (koliko % 10 === 1 && koliko % 100 !== 11) return koliko + " stavka";
  if ([2, 3, 4].includes(koliko % 10) && ![12, 13, 14].includes(koliko % 100)) {
    return koliko + " stavke";
  }
  return koliko + " stavki";
}

/** Statusni kod i poruke stizu iz Presentera; ovde se samo rasporedjuju. */
async function radnja(posao) {
  try {
    await posao();
  } catch (greska) {
    if (!(greska instanceof ApiGreska)) throw greska;

    if (greska.status === 400) {
      prikaziGreskeForme(greska.greske);
    } else {
      obavesti(greska.message, greska.status === 409 ? "sukob" : "");
    }
  }
}

async function ucitajSve() {
  const narudzbine = await narudzbinaApi.lista();
  stanje.narudzbine = narudzbine.narudzbine;

  const proizvodi = await proizvodApi.lista();
  stanje.proizvodi = proizvodi.proizvodi;

  prikaziNarudzbine();
  prikaziProizvode();
}

function prikaziNarudzbine() {
  el("telo-narudzbina").innerHTML = stanje.narudzbine
    .map(
      (narudzbina) => `
      <tr data-id="${narudzbina.id}" class="${
        stanje.izabrana && stanje.izabrana.id === narudzbina.id ? "izabrana" : ""
      }">
        <td><code>${bez(narudzbina.broj)}</code></td>
        <td>${bez(narudzbina.kupac)}</td>
        <td>${datum(narudzbina.datum)}</td>
        <td><span class="znacka znacka--${narudzbina.status}">${bez(
          narudzbina.status_naziv
        )}</span></td>
        <td class="desno">${narudzbina.broj_stavki}</td>
        <td class="desno">${dinara(narudzbina.ukupan_iznos)}</td>
        <td class="desno">
          <button class="dugme dugme--sporedno dugme--sitno" data-radi="otvori">Stavke</button>
          <button class="dugme dugme--opasno dugme--sitno" data-radi="obrisi">Obrisi</button>
        </td>
      </tr>`
    )
    .join("");
}

function prikaziDetalje() {
  const narudzbina = stanje.izabrana;
  el("kartica-detalja").hidden = narudzbina === null;
  if (!narudzbina) return;

  el("opis-narudzbine").innerHTML =
    `<code>${bez(narudzbina.broj)}</code> - ${bez(narudzbina.kupac)} - ` +
    `${datum(narudzbina.datum)} - stavke ispod postoje samo dok postoji ova narudzbina.`;

  el("telo-stavki").innerHTML = narudzbina.stavke.length
    ? narudzbina.stavke
        .map(
          (stavka) => `
          <tr data-id="${stavka.id}">
            <td>${bez(stavka.proizvod_naziv)}</td>
            <td class="desno">${stavka.kolicina} ${bez(stavka.jedinica_mere)}</td>
            <td class="desno">${dinara(stavka.cena_po_komadu)}</td>
            <td class="desno">${dinara(stavka.iznos)}</td>
            <td class="desno">
              <button class="dugme dugme--opasno dugme--sitno">Obrisi</button>
            </td>
          </tr>`
        )
        .join("")
    : `<tr><td colspan="5" class="prazno">Narudzbina jos nema stavki.</td></tr>`;

  el("podnozje-stavki").innerHTML = narudzbina.stavke.length
    ? `<tr><td colspan="3">Ukupno</td>
           <td class="desno">${dinara(narudzbina.ukupan_iznos)}</td><td></td></tr>`
    : "";

  el("izbor-proizvoda").innerHTML = stanje.proizvodi
    .map(
      (proizvod) =>
        `<option value="${proizvod.id}">${bez(proizvod.naziv)} - ${dinara(
          proizvod.cena
        )} / ${bez(proizvod.jedinica_mere)}</option>`
    )
    .join("");
}

function prikaziProizvode() {
  el("telo-proizvoda").innerHTML = stanje.proizvodi
    .map(
      (proizvod) => `
      <tr data-id="${proizvod.id}">
        <td>${bez(proizvod.naziv)}</td>
        <td class="desno">${dinara(proizvod.cena)}</td>
        <td>${bez(proizvod.jedinica_mere)}</td>
        <td class="desno">
          <button class="dugme dugme--opasno dugme--sitno">Obrisi</button>
        </td>
      </tr>`
    )
    .join("");
}

/** Novo stanje stize iz jednog odgovora Presentera; View nista ne racuna. */
async function osveziIzabranu() {
  const narudzbina = await narudzbinaApi.jedna(stanje.izabrana.id);
  stanje.izabrana = narudzbina;

  const indeks = stanje.narudzbine.findIndex((jedna) => jedna.id === narudzbina.id);
  if (indeks !== -1) stanje.narudzbine[indeks] = narudzbina;

  prikaziNarudzbine();
  prikaziDetalje();
}

el("telo-narudzbina").addEventListener("click", (dogadjaj) => {
  const red = dogadjaj.target.closest("tr");
  if (!red) return;

  const id = Number(red.dataset.id);
  const dugme = dogadjaj.target.closest("button");
  const narudzbina = stanje.narudzbine.find((jedna) => jedna.id === id);

  if (dugme && dugme.dataset.radi === "obrisi") {
    const potvrda =
      `Brisanjem narudzbine ${narudzbina.broj} nestaje i ` +
      `${stavki(narudzbina.broj_stavki)}. Nastaviti?`;
    if (!confirm(potvrda)) return;

    radnja(async () => {
      const odgovor = await narudzbinaApi.obrisi(id);
      stanje.izabrana = null;
      await ucitajSve();
      prikaziDetalje();
      obavesti(odgovor.poruka, "uspeh");
    });
    return;
  }

  radnja(async () => {
    stanje.izabrana = await narudzbinaApi.jedna(id);
    ocistiGreske();
    prikaziNarudzbine();
    prikaziDetalje();
  });
});

el("telo-stavki").addEventListener("click", (dogadjaj) => {
  if (!dogadjaj.target.closest("button")) return;

  const id = Number(dogadjaj.target.closest("tr").dataset.id);

  radnja(async () => {
    await stavkaApi.obrisi(id);
    await osveziIzabranu();
  });
});

el("telo-proizvoda").addEventListener("click", (dogadjaj) => {
  if (!dogadjaj.target.closest("button")) return;

  const id = Number(dogadjaj.target.closest("tr").dataset.id);

  radnja(async () => {
    const odgovor = await proizvodApi.obrisi(id);
    await ucitajSve();
    obavesti(odgovor.poruka, "uspeh");
  });
});

el("forma-stavke").addEventListener("submit", (dogadjaj) => {
  dogadjaj.preventDefault();
  ocistiGreske();

  radnja(async () => {
    await stavkaApi.dodaj({
      narudzbina_id: stanje.izabrana.id,
      proizvod_id: el("izbor-proizvoda").value,
      kolicina: el("unos-kolicine").value,
    });

    await osveziIzabranu();
    obavesti("Stavka je dodata.", "uspeh");
  });
});

const POLJA = { proizvod_id: "izbor-proizvoda", kolicina: "unos-kolicine" };

function ocistiGreske() {
  document.querySelectorAll(".greska").forEach((mesto) => (mesto.textContent = ""));
  document
    .querySelectorAll(".neispravno")
    .forEach((polje) => polje.classList.remove("neispravno"));
}

/** Greske stizu po poljima, pa svaka ide ispod svog polja. */
function prikaziGreskeForme(greske) {
  Object.entries(greske).forEach(([polje, poruka]) => {
    const mesto = document.querySelector(`[data-greska="${polje}"]`);
    if (mesto) mesto.textContent = poruka;
    if (POLJA[polje]) el(POLJA[polje]).classList.add("neispravno");
  });
}

let sakrivanje;

function obavesti(poruka, vrsta = "") {
  const traka = el("obavestenje");
  traka.textContent = poruka;
  traka.className = "obavestenje" + (vrsta ? " obavestenje--" + vrsta : "");
  traka.hidden = false;

  clearTimeout(sakrivanje);
  sakrivanje = setTimeout(() => (traka.hidden = true), 7000);
}

radnja(ucitajSve);
