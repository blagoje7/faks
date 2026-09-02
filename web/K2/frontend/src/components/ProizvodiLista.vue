<script setup>
import { onMounted, ref, watch } from "vue";

import { proizvodApi } from "@/api";
import { dodajPoruku } from "@/poruke";
import { dinari } from "@/tekst";
import PotvrdaBrisanja from "@/components/PotvrdaBrisanja.vue";

const proizvodi = ref([]);
const ucitava = ref(true);
const greska = ref("");

const pretraga = ref("");
const sortiranje = ref("naziv");
const smer = ref("asc");
const samoDostupni = ref(false);

const zaBrisanje = ref(null);

let tajmer;

async function ucitaj() {
  ucitava.value = true;
  greska.value = "";

  try {
    proizvodi.value = await proizvodApi.lista({
      pretraga: pretraga.value,
      sortiranje: sortiranje.value,
      smer: smer.value,
      samo_dostupni: samoDostupni.value ? "1" : "",
    });
  } catch (problem) {
    greska.value = problem.message;
    proizvodi.value = [];
  } finally {
    ucitava.value = false;
  }
}

watch([pretraga, sortiranje, smer, samoDostupni], () => {
  clearTimeout(tajmer);
  tajmer = setTimeout(ucitaj, 250);
});

onMounted(ucitaj);

async function obrisi() {
  const proizvod = zaBrisanje.value;
  zaBrisanje.value = null;

  try {
    const odgovor = await proizvodApi.obrisi(proizvod.id);
    dodajPoruku(odgovor.poruka);
    await ucitaj();
  } catch (problem) {
    // 409: proizvod stoji na nekoj stavci
    dodajPoruku(problem.message, "greska");
  }
}
</script>

<template>
  <div class="page-title">
    <div>
      <p class="eyebrow">Sifarnik</p>
      <h1>Proizvodi</h1>
    </div>
    <RouterLink class="button" to="/proizvodi/novi">Dodaj proizvod</RouterLink>
  </div>

  <div class="toolbar">
    <input
      v-model="pretraga"
      type="text"
      placeholder="Pretrazi po nazivu"
      aria-label="Pretraga proizvoda"
    />
    <select v-model="sortiranje" aria-label="Kolona za sortiranje">
      <option value="naziv">Naziv</option>
      <option value="cena">Cena</option>
    </select>
    <select v-model="smer" aria-label="Smer sortiranja">
      <option value="asc">Rastuce</option>
      <option value="desc">Opadajuce</option>
    </select>
    <label class="prekidac">
      <input v-model="samoDostupni" type="checkbox" />
      Samo dostupni
    </label>
  </div>

  <p v-if="greska" class="upozorenje">{{ greska }}</p>

  <p v-else-if="ucitava" class="muted">Ucitavanje...</p>

  <div v-else-if="proizvodi.length" class="table-card">
    <table>
      <thead>
        <tr>
          <th>Naziv</th>
          <th>Jedinica mere</th>
          <th class="desno">Cena</th>
          <th>Dostupnost</th>
          <th>Akcije</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="proizvod in proizvodi" :key="proizvod.id">
          <td>
            {{ proizvod.naziv }}
            <span class="opis">{{ proizvod.opis }}</span>
          </td>
          <td>{{ proizvod.jedinica_mere }}</td>
          <td class="desno brojevi">{{ dinari(proizvod.cena) }}</td>
          <td>
            <span :class="['pilula', proizvod.dostupan ? 'dostupan' : 'nedostupan']">
              {{ proizvod.dostupan ? "Dostupan" : "Nedostupan" }}
            </span>
          </td>
          <td class="table-actions">
            <RouterLink :to="`/proizvodi/${proizvod.id}/izmeni`">Izmeni</RouterLink>
            <button type="button" class="veza opasno" @click="zaBrisanje = proizvod">
              Obrisi
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-else class="empty">
    <h2>Nema proizvoda za prikaz.</h2>
    <p>Promenite uslove pretrage ili dodajte prvi proizvod.</p>
  </div>

  <PotvrdaBrisanja
    v-if="zaBrisanje"
    :tekst="`Obrisati proizvod '${zaBrisanje.naziv}' iz sifarnika? Brisanje nece uspeti ako se proizvod nalazi na nekoj narudzbini.`"
    @potvrdi="obrisi"
    @otkazi="zaBrisanje = null"
  />
</template>
