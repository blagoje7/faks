<script setup>
import { onMounted, ref, watch } from "vue";

import { narudzbinaApi } from "@/api";
import { dodajPoruku } from "@/poruke";
import { datum, dinari, tekstBrisanjaNarudzbine } from "@/tekst";
import PotvrdaBrisanja from "@/components/PotvrdaBrisanja.vue";

const narudzbine = ref([]);
const statusi = ref([]);
const ucitava = ref(true);
const greska = ref("");

const pretraga = ref("");
const status = ref("");
const sortiranje = ref("datum");
const smer = ref("desc");

const zaBrisanje = ref(null);

let tajmer;

async function ucitaj() {
  ucitava.value = true;
  greska.value = "";

  try {
    narudzbine.value = await narudzbinaApi.lista({
      pretraga: pretraga.value,
      status: status.value,
      sortiranje: sortiranje.value,
      smer: smer.value,
    });
  } catch (problem) {
    greska.value = problem.message;
    narudzbine.value = [];
  } finally {
    ucitava.value = false;
  }
}

// Filteri se šalju serveru; kratko odlaganje sprečava slanje zahteva
// na svaki otkucani karakter.
watch([pretraga, status, sortiranje, smer], () => {
  clearTimeout(tajmer);
  tajmer = setTimeout(ucitaj, 250);
});

onMounted(async () => {
  try {
    statusi.value = await narudzbinaApi.statusi();
  } catch {
    statusi.value = [];
  }
  await ucitaj();
});

function promeniSortiranje(kolona) {
  if (sortiranje.value === kolona) {
    smer.value = smer.value === "asc" ? "desc" : "asc";
  } else {
    sortiranje.value = kolona;
    smer.value = "asc";
  }
}

function oznakaSmera(kolona) {
  if (sortiranje.value !== kolona) return "";
  return smer.value === "asc" ? "▲" : "▼";
}

function resetuj() {
  pretraga.value = "";
  status.value = "";
  sortiranje.value = "datum";
  smer.value = "desc";
}

async function obrisi() {
  const narudzbina = zaBrisanje.value;
  zaBrisanje.value = null;

  try {
    const odgovor = await narudzbinaApi.obrisi(narudzbina.id);
    dodajPoruku(odgovor.poruka);
    await ucitaj();
  } catch (problem) {
    dodajPoruku(problem.message, "greska");
  }
}
</script>

<template>
  <div class="page-title">
    <div>
      <p class="eyebrow">Master entitet</p>
      <h1>Narudžbine</h1>
    </div>
    <RouterLink class="button" to="/narudzbine/nova">Nova narudžbina</RouterLink>
  </div>

  <div class="toolbar">
    <input
      v-model="pretraga"
      type="text"
      placeholder="Pretraži po broju ili kupcu"
      aria-label="Pretraga narudžbina"
    />
    <select v-model="status" aria-label="Filter po statusu">
      <option value="">Svi statusi</option>
      <option v-for="s in statusi" :key="s.vrednost" :value="s.vrednost">
        {{ s.naziv }}
      </option>
    </select>
    <select v-model="sortiranje" aria-label="Kolona za sortiranje">
      <option value="datum">Datum</option>
      <option value="broj">Broj</option>
      <option value="kupac">Kupac</option>
    </select>
    <select v-model="smer" aria-label="Smer sortiranja">
      <option value="asc">Rastuće</option>
      <option value="desc">Opadajuće</option>
    </select>
    <button class="button secondary" type="button" @click="resetuj">Resetuj</button>
  </div>

  <p v-if="greska" class="upozorenje">{{ greska }}</p>

  <p v-else-if="ucitava" class="muted">Učitavanje...</p>

  <div v-else-if="narudzbine.length" class="table-card">
    <table>
      <thead>
        <tr>
          <th class="sortabilna" @click="promeniSortiranje('broj')">
            Broj {{ oznakaSmera("broj") }}
          </th>
          <th class="sortabilna" @click="promeniSortiranje('kupac')">
            Kupac {{ oznakaSmera("kupac") }}
          </th>
          <th class="sortabilna" @click="promeniSortiranje('datum')">
            Datum {{ oznakaSmera("datum") }}
          </th>
          <th>Status</th>
          <th class="desno">Stavki</th>
          <th class="desno">Ukupno</th>
          <th>Akcije</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="narudzbina in narudzbine" :key="narudzbina.id">
          <td class="mono">{{ narudzbina.broj }}</td>
          <td>{{ narudzbina.kupac }}</td>
          <td>{{ datum(narudzbina.datum) }}</td>
          <td>
            <span :class="['pilula', narudzbina.status]">
              {{ narudzbina.status_naziv }}
            </span>
          </td>
          <td class="desno brojevi">{{ narudzbina.broj_stavki }}</td>
          <td class="desno brojevi">{{ dinari(narudzbina.ukupan_iznos) }}</td>
          <td class="table-actions">
            <RouterLink :to="`/narudzbine/${narudzbina.id}`">Detalji</RouterLink>
            <RouterLink :to="`/narudzbine/${narudzbina.id}/izmeni`">Izmeni</RouterLink>
            <button
              type="button"
              class="veza opasno"
              @click="zaBrisanje = narudzbina"
            >
              Obriši
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-else class="empty">
    <h2>Nema narudžbina za prikaz.</h2>
    <p>Promenite uslove pretrage ili unesite prvu narudžbinu.</p>
  </div>

  <PotvrdaBrisanja
    v-if="zaBrisanje"
    :tekst="tekstBrisanjaNarudzbine(zaBrisanje)"
    @potvrdi="obrisi"
    @otkazi="zaBrisanje = null"
  />
</template>
