<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { narudzbinaApi } from "@/api";
import { dodajPoruku } from "@/poruke";

const props = defineProps({
  id: { type: String, default: "" },
});

const router = useRouter();
const izmena = computed(() => Boolean(props.id));

const danas = new Date().toISOString().slice(0, 10);

const statusi = ref([]);
const model = ref({
  broj: "",
  kupac: "",
  email: "",
  datum: danas,
  status: "u_pripremi",
});
const greske = ref({});
const opstaGreska = ref("");
const ucitava = ref(true);
const salje = ref(false);

onMounted(async () => {
  try {
    statusi.value = await narudzbinaApi.statusi();

    if (izmena.value) {
      const narudzbina = await narudzbinaApi.jedna(props.id);
      model.value = {
        broj: narudzbina.broj,
        kupac: narudzbina.kupac,
        email: narudzbina.email,
        datum: narudzbina.datum,
        status: narudzbina.status,
      };
    } else {
      // server predlaze slobodan broj
      const predlog = await narudzbinaApi.sledeciBroj();
      model.value.broj = predlog.broj;
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
    const narudzbina = izmena.value
      ? await narudzbinaApi.izmeni(props.id, model.value)
      : await narudzbinaApi.dodaj(model.value);

    dodajPoruku(izmena.value ? "Narudzbina je izmenjena." : "Narudzbina je uneta.");
    router.push(`/narudzbine/${narudzbina.id}`);
  } catch (problem) {
    // greske stizu po poljima
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
      <p class="eyebrow">Forma za narudzbinu</p>
      <h1>{{ izmena ? "Izmena narudzbine" : "Nova narudzbina" }}</h1>
    </div>
  </div>

  <p v-if="ucitava" class="muted">Ucitavanje...</p>

  <form v-else class="form-card" @submit.prevent="posalji">
    <p v-if="opstaGreska" class="upozorenje">{{ opstaGreska }}</p>

    <label for="broj">Broj narudzbine</label>
    <input id="broj" v-model="model.broj" type="text" :class="{ neispravno: greske.broj }" />
    <p v-if="greske.broj" class="greska-polja">{{ greske.broj }}</p>

    <label for="kupac">Kupac</label>
    <input
      id="kupac"
      v-model="model.kupac"
      type="text"
      :class="{ neispravno: greske.kupac }"
    />
    <p v-if="greske.kupac" class="greska-polja">{{ greske.kupac }}</p>

    <label for="email">Elektronska posta</label>
    <input
      id="email"
      v-model="model.email"
      type="text"
      :class="{ neispravno: greske.email }"
    />
    <p v-if="greske.email" class="greska-polja">{{ greske.email }}</p>

    <label for="datum">Datum</label>
    <input
      id="datum"
      v-model="model.datum"
      type="date"
      :max="danas"
      :class="{ neispravno: greske.datum }"
    />
    <p v-if="greske.datum" class="greska-polja">{{ greske.datum }}</p>
    <p v-else class="pomoc">Datum narudzbine ne moze biti u buducnosti.</p>

    <label for="status">Status</label>
    <select id="status" v-model="model.status" :class="{ neispravno: greske.status }">
      <option v-for="s in statusi" :key="s.vrednost" :value="s.vrednost">
        {{ s.naziv }}
      </option>
    </select>
    <p v-if="greske.status" class="greska-polja">{{ greske.status }}</p>

    <div class="actions">
      <button class="button" type="submit" :disabled="salje">
        {{ salje ? "Cuvanje..." : "Sacuvaj" }}
      </button>
      <RouterLink class="button secondary" to="/narudzbine">Nazad</RouterLink>
    </div>
  </form>
</template>
