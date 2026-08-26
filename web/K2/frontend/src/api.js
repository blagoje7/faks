const OSNOVA = "/api";

export class ApiGreska extends Error {
  constructor(poruka, status, greske) {
    super(poruka);
    this.status = status;
    this.greske = greske || {};
  }
}

async function zahtev(putanja, opcije = {}) {
  let odgovor;

  try {
    odgovor = await fetch(OSNOVA + putanja, {
      headers: { "Content-Type": "application/json" },
      ...opcije,
    });
  } catch {
    throw new ApiGreska(
      "Server nije dostupan. Proverite da li Flask aplikacija radi na portu 5000.",
      0,
    );
  }

  const telo = await odgovor.json().catch(() => null);

  if (!odgovor.ok) {
    throw new ApiGreska(
      (telo && telo.poruka) || "Zahtev nije uspeo.",
      odgovor.status,
      telo && telo.greske,
    );
  }

  return telo;
}

function telo(podaci) {
  return JSON.stringify(podaci);
}

export const proizvodApi = {
  lista: (parametri = {}) =>
    zahtev("/proizvodi?" + new URLSearchParams(parametri).toString()),
  jedan: (id) => zahtev(`/proizvodi/${id}`),
  jediniceMere: () => zahtev("/proizvodi/jedinice-mere"),
  dodaj: (podaci) => zahtev("/proizvodi", { method: "POST", body: telo(podaci) }),
  izmeni: (id, podaci) =>
    zahtev(`/proizvodi/${id}`, { method: "PUT", body: telo(podaci) }),
  obrisi: (id) => zahtev(`/proizvodi/${id}`, { method: "DELETE" }),
};

export const narudzbinaApi = {
  lista: (parametri = {}) =>
    zahtev("/narudzbine?" + new URLSearchParams(parametri).toString()),
  jedna: (id) => zahtev(`/narudzbine/${id}`),
  stavke: (id) => zahtev(`/narudzbine/${id}/stavke`),
  statusi: () => zahtev("/narudzbine/statusi"),
  sledeciBroj: () => zahtev("/narudzbine/sledeci-broj"),
  dodaj: (podaci) => zahtev("/narudzbine", { method: "POST", body: telo(podaci) }),
  izmeni: (id, podaci) =>
    zahtev(`/narudzbine/${id}`, { method: "PUT", body: telo(podaci) }),
  obrisi: (id) => zahtev(`/narudzbine/${id}`, { method: "DELETE" }),
};

export const stavkaApi = {
  jedna: (id) => zahtev(`/stavke/${id}`),
  dodaj: (podaci) => zahtev("/stavke", { method: "POST", body: telo(podaci) }),
  izmeni: (id, podaci) =>
    zahtev(`/stavke/${id}`, { method: "PUT", body: telo(podaci) }),
  obrisi: (id) => zahtev(`/stavke/${id}`, { method: "DELETE" }),
};
