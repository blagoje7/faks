<script setup>
import { computed, onMounted, ref } from "vue";

import { narudzbinaApi, proizvodApi } from "@/api";
import { dinari } from "@/tekst";

const narudzbine = ref([]);
const proizvodi = ref([]);
const ucitava = ref(true);
const greska = ref("");

onMounted(async () => {
  try {
    [narudzbine.value, proizvodi.value] = await Promise.all([
      narudzbinaApi.lista(),
      proizvodApi.lista(),
    ]);
  } catch (problem) {
    greska.value = problem.message;
  } finally {
    ucitava.value = false;
  }
});

const ukupanPromet = computed(() =>
  narudzbine.value.reduce((zbir, narudzbina) => zbir + narudzbina.ukupan_iznos, 0),
);

const uPripremi = computed(
  () => narudzbine.value.filter((n) => n.status === "u_pripremi").length,
);
</script>

<template>
  <section class="hero">
    <p class="eyebrow">Kolokvijum II &middot; Flask REST API + Vue.js</p>
    <h1>Evidencija narudžbina i njihovih stavki</h1>
    <p class="muted">
      Narudžbina je nadređeni entitet, stavka je podređena i briše se zajedno
      sa njom. Proizvod je šifarnik koji stoji sa strane — stavke ga referišu,
      ali on nije njihov roditelj. Sve operacije idu preko REST API-ja.
    </p>

    <div class="actions">
      <RouterLink class="button" to="/narudzbine">Prikaži narudžbine</RouterLink>
      <RouterLink class="button secondary" to="/proizvodi">Šifarnik proizvoda</RouterLink>
    </div>
  </section>

  <p v-if="greska" class="upozorenje">{{ greska }}</p>

  <section v-else-if="!ucitava" class="stats-row">
    <div class="stat">
      <span>Narudžbina</span>
      <strong>{{ narudzbine.length }}</strong>
    </div>
    <div class="stat">
      <span>U pripremi</span>
      <strong>{{ uPripremi }}</strong>
    </div>
    <div class="stat">
      <span>Proizvoda u šifarniku</span>
      <strong>{{ proizvodi.length }}</strong>
    </div>
    <div class="stat">
      <span>Ukupan promet</span>
      <strong>{{ dinari(ukupanPromet) }}</strong>
    </div>
  </section>
</template>
