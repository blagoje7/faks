<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { proizvodApi } from "@/api";
import { dodajPoruku } from "@/poruke";

const props = defineProps({
  id: { type: String, default: "" },
});

const router = useRouter();
const izmena = computed(() => Boolean(props.id));

const jedinice = ref([]);
const model = ref({
  naziv: "",
  opis: "",
  cena: 0,
  jedinica_mere: "kom",
  dostupan: true,
});
const greske = ref({});
const opstaGreska = ref("");
const ucitava = ref(true);
const salje = ref(false);

onMounted(async () => {
  try {
    jedinice.value = await proizvodApi.jediniceMere();

    if (izmena.value) {
      const proizvod = await proizvodApi.jedan(props.id);
      model.value = {
        naziv: proizvod.naziv,
        opis: proizvod.opis,
        cena: proizvod.cena,
        jedinica_mere: proizvod.jedinica_mere,
        dostupan: proizvod.dostupan,
      };
    }
  } catch (problem) {
    opstaGreska.value = problem.message;
  } finally {
    ucitava.value = false;
  }
});

async function posalji() {
  salje.value = true;
  greske.value = {};
  opstaGreska.value = "";

  try {
    if (izmena.value) {
      await proizvodApi.izmeni(props.id, model.value);
    } else {
      await proizvodApi.dodaj(model.value);
    }

    dodajPoruku(izmena.value ? "Proizvod je izmenjen." : "Proizvod je dodat.");
    router.push("/proizvodi");
  } catch (problem) {
    greske.value = problem.greske;
    if (!Object.keys(problem.greske).length) {
      opstaGreska.value = problem.message;
    }
  } finally {
    salje.value = false;
  }
}
</script>

<template>
  <div class="page-title">
    <div>
      <p class="eyebrow">Forma za proizvod</p>
      <h1>{{ izmena ? "Izmena proizvoda" : "Novi proizvod" }}</h1>
    </div>
  </div>

  <p v-if="ucitava" class="muted">Učitavanje...</p>

  <form v-else class="form-card" @submit.prevent="posalji">
    <p v-if="opstaGreska" class="upozorenje">{{ opstaGreska }}</p>

    <label for="naziv">Naziv</label>
    <input
      id="naziv"
      v-model="model.naziv"
      type="text"
      :class="{ neispravno: greske.naziv }"
    />
    <p v-if="greske.naziv" class="greska-polja">{{ greske.naziv }}</p>

    <label for="opis">Opis</label>
    <textarea
      id="opis"
      v-model="model.opis"
      rows="4"
      :class="{ neispravno: greske.opis }"
    ></textarea>
    <p v-if="greske.opis" class="greska-polja">{{ greske.opis }}</p>

    <label for="cena">Cena u dinarima</label>
    <input
      id="cena"
      v-model.number="model.cena"
      type="number"
      min="0"
      step="0.01"
      :class="{ neispravno: greske.cena }"
    />
    <p v-if="greske.cena" class="greska-polja">{{ greske.cena }}</p>
    <p v-else class="pomoc">
      Izmena cene ne menja iznose već unetih narudžbina — one pamte cenu iz
      trenutka poručivanja.
    </p>

    <label for="jedinica">Jedinica mere</label>
    <select
      id="jedinica"
      v-model="model.jedinica_mere"
      :class="{ neispravno: greske.jedinica_mere }"
    >
      <option v-for="jedinica in jedinice" :key="jedinica" :value="jedinica">
        {{ jedinica }}
      </option>
    </select>
    <p v-if="greske.jedinica_mere" class="greska-polja">{{ greske.jedinica_mere }}</p>

    <label class="prekidac samostalni">
      <input v-model="model.dostupan" type="checkbox" />
      Dostupan za poručivanje
    </label>

    <div class="actions">
      <button class="button" type="submit" :disabled="salje">
        {{ salje ? "Čuvanje..." : "Sačuvaj" }}
      </button>
      <RouterLink class="button secondary" to="/proizvodi">Nazad</RouterLink>
    </div>
  </form>
</template>
