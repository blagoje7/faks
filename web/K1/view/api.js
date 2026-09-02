// KANAL - jedini put od View-a do Presentera. Bez pravila domena.

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
    odgovor = await fetch(putanja, {
      headers: { "Content-Type": "application/json" },
      ...opcije,
    });
  } catch {
    throw new ApiGreska("Server nije dostupan. Da li je pokrenut pokreni.py?", 0);
  }

  const telo = await odgovor.json().catch(() => null);

  if (!odgovor.ok) {
    throw new ApiGreska(
      (telo && telo.poruka) || "Zahtev nije uspeo.",
      odgovor.status,
      telo && telo.greske
    );
  }

  return telo;
}

function telo(podaci) {
  return JSON.stringify(podaci);
}

export const narudzbinaApi = {
  lista: () => zahtev("/api/narudzbine"),
  jedna: (id) => zahtev("/api/narudzbine/" + id),
  obrisi: (id) => zahtev("/api/narudzbine/" + id, { method: "DELETE" }),
};

export const proizvodApi = {
  lista: () => zahtev("/api/proizvodi"),
  obrisi: (id) => zahtev("/api/proizvodi/" + id, { method: "DELETE" }),
};

export const stavkaApi = {
  dodaj: (podaci) => zahtev("/api/stavke", { method: "POST", body: telo(podaci) }),
  obrisi: (id) => zahtev("/api/stavke/" + id, { method: "DELETE" }),
};
