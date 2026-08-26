<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { narudzbinaApi, proizvodApi, stavkaApi } from "@/api";
import { dodajPoruku } from "@/poruke";
import { dinari } from "@/tekst";

const props = defineProps({
  id: { type: String, default: "" }, // izmena postojeće stavke
  narudzbinaId: { type: String, default: "" }, // dodavanje iz detalja narudžbine
});

const router = useRouter();
const izmena = computed(() => Boolean(props.id));

const narudzbine = ref([]);
const proizvodi = ref([]);
const pocetna = ref(null); // stavka kakva je bila pre izmene

const model = ref({ narudzbina_id: null, proizvod_id: null, kolicina: 1 });
const greske = ref({});
const opstaGreska = ref("");
const ucitava = ref(true);
const salje = ref(false);

const povratnaPutanja = computed(() =>
  model.value.narudzbina_id ? `/narudzbine/${model.value.narudzbina_id}` : "/narudzbine",
);

const izabraniProizvod = computed(() =>
  proizvodi.value.find((proizvod) => proizvod.id === model.value.proizvod_id),
);

// Cena se prepisuje iz šifarnika samo kada se proizvod postavlja ili menja.
// Ako se na izmeni proizvod ne dira, važi cena zapamćena pri unosu.
const zadrzavaZapamcenuCenu = computed(
  () => izmena.value && pocetna.value && pocetna.value.proizvod_id === model.value.proizvod_id,
);

const cenaZaPrikaz = computed(() => {
  if (zadrzavaZapamcenuCenu.value) return pocetna.value.cena_po_komadu;
  return izabraniProizvod.value ? izabraniProizvod.value.cena : 0;
});

const iznos = computed(() => cenaZaPrikaz.value * (model.value.kolicina || 0));

onMounted(async () => {
  try {
    // Oba select polja se pune sa servera: narudžbine i proizvodi.
    [narudzbine.value, proizvodi.value] = await Promise.all([
      narudzbinaApi.lista({ sortiranje: "broj", smer: "asc" }),
      proizvodApi.lista({ sortiranje: "naziv" }),
    ]);

    if (izmena.value) {
      const stavka = await stavkaApi.jedna(props.id);
      pocetna.value = stavka;
      model.value = {
        narudzbina_id: stavka.narudzbina_id,
        proizvod_id: stavka.proizvod_id,
        kolicina: stavka.kolicina,
      };
    } else {
      model.value.narudzbina_id =
        Number(props.narudzbinaId) ||
        (narudzbine.value[0] && narudzbine.value[0].id) ||
        null;

      const dostupan = proizvodi.value.find((proizvod) => proizvod.dostupan);
      model.value.proizvod_id = dostupan ? dostupan.id : null;
    }
  } catch (problem) {
    opstaGreska.value = problem.message;
  } finally {
    ucitava.value = false;
  }
});

function nazivNarudzbine(narudzbina) {
  return `${narudzbina.broj} — ${narudzbina.kupac}`;
}

function nazivProizvoda(proizvod) {
  const cena = `${dinari(proizvod.cena)} RSD / ${proizvod.jedinica_mere}`;
  return proizvod.dostupan
    ? `${proizvod.naziv} — ${cena}`
    : `${proizvod.naziv} — ${cena} (nedostupno)`;
}

async function posalji() {
  salje.value = true;
  greske.value = {};
  opstaGreska.value = "";

  try {
    const stavka = izmena.value
      ? await stavkaApi.izmeni(props.id, model.value)
      : await stavkaApi.dodaj(model.value);

    dodajPoruku(izmena.value ? "Stavka je izmenjena." : "Stavka je dodata.");
    router.push(`/narudzbine/${stavka.narudzbina_id}`);
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
      <p class="eyebrow">Forma za stavku</p>
      <h1>{{ izmena ? "Izmena stavke" : "Dodavanje stavke" }}</h1>
    </div>
  </div>

  <p v-if="ucitava" class="muted">Učitavanje...</p>

  <form v-else class="form-card" @submit.prevent="posalji">
    <p v-if="opstaGreska" class="upozorenje">{{ opstaGreska }}</p>

    <label for="narudzbina">Narudžbina</label>
    <select
      id="narudzbina"
      v-model.number="model.narudzbina_id"
      :class="{ neispravno: greske.narudzbina_id }"
    >
      <option v-for="n in narudzbine" :key="n.id" :value="n.id">
        {{ nazivNarudzbine(n) }}
      </option>
    </select>
    <p v-if="greske.narudzbina_id" class="greska-polja">{{ greske.narudzbina_id }}</p>
    <p v-else-if="izmena" class="pomoc">
      Promenom narudžbine stavka se premešta na izabranu narudžbinu.
    </p>

    <label for="proizvod">Proizvod</label>
    <select
      id="proizvod"
      v-model.number="model.proizvod_id"
      :class="{ neispravno: greske.proizvod_id }"
    >
      <option v-for="p in proizvodi" :key="p.id" :value="p.id">
        {{ nazivProizvoda(p) }}
      </option>
    </select>
    <p v-if="greske.proizvod_id" class="greska-polja">{{ greske.proizvod_id }}</p>

    <label for="kolicina">Količina</label>
    <input
      id="kolicina"
      v-model.number="model.kolicina"
      type="number"
      min="1"
      :class="{ neispravno: greske.kolicina }"
    />
    <p v-if="greske.kolicina" class="greska-polja">{{ greske.kolicina }}</p>

    <div class="obracun">
      <div class="obracun-red">
        <span>Cena po komadu</span>
        <strong class="brojevi">{{ dinari(cenaZaPrikaz) }} RSD</strong>
      </div>
      <div class="obracun-red zbir">
        <span>Iznos stavke</span>
        <strong class="brojevi">{{ dinari(iznos) }} RSD</strong>
      </div>
      <p class="pomoc">
        <template v-if="zadrzavaZapamcenuCenu">
          Zadržava se cena zapamćena pri unosu stavke. Tekuća cena iz šifarnika
          je {{ dinari(izabraniProizvod ? izabraniProizvod.cena : 0) }} RSD i
          primeniće se tek ako promenite proizvod.
        </template>
        <template v-else>
          Cena se preuzima iz šifarnika u trenutku čuvanja i od tada se pamti
          uz stavku, pa je kasnija izmena cenovnika neće promeniti.
        </template>
      </p>
    </div>

    <div class="actions">
      <button class="button" type="submit" :disabled="salje">
        {{ salje ? "Čuvanje..." : "Sačuvaj" }}
      </button>
      <RouterLink class="button secondary" :to="povratnaPutanja">Nazad</RouterLink>
    </div>
  </form>
</template>
