<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { narudzbinaApi, stavkaApi } from "@/api";
import { dodajPoruku } from "@/poruke";
import { datum, dinari, tekstBrisanjaNarudzbine } from "@/tekst";
import PotvrdaBrisanja from "@/components/PotvrdaBrisanja.vue";

const props = defineProps({
  id: { type: String, required: true },
});

const router = useRouter();

const narudzbina = ref(null);
const ucitava = ref(true);
const greska = ref("");

// Pamti se i vrsta entiteta jer narudžbina i stavka mogu imati isti id.
const zaBrisanje = ref(null);

async function ucitaj() {
  ucitava.value = true;
  greska.value = "";

  try {
    narudzbina.value = await narudzbinaApi.jedna(props.id);
  } catch (problem) {
    greska.value = problem.message;
    narudzbina.value = null;
  } finally {
    ucitava.value = false;
  }
}

onMounted(ucitaj);
watch(() => props.id, ucitaj);

const tekstPotvrde = computed(() => {
  if (!zaBrisanje.value) return "";

  const { vrsta, stavka } = zaBrisanje.value;

  if (vrsta === "narudzbina") {
    return tekstBrisanjaNarudzbine(stavka);
  }
  return `Ukloniti stavku „${stavka.proizvod_naziv}“ sa ove narudžbine?`;
});

async function potvrdiBrisanje() {
  const { vrsta, stavka } = zaBrisanje.value;
  zaBrisanje.value = null;

  try {
    if (vrsta === "narudzbina") {
      const odgovor = await narudzbinaApi.obrisi(stavka.id);
      dodajPoruku(odgovor.poruka);
      router.push("/narudzbine");
      return;
    }

    const odgovor = await stavkaApi.obrisi(stavka.id);
    dodajPoruku(odgovor.poruka);
    await ucitaj();
  } catch (problem) {
    dodajPoruku(problem.message, "greska");
  }
}
</script>

<template>
  <p v-if="ucitava" class="muted">Učitavanje...</p>

  <div v-else-if="greska" class="empty">
    <h2>{{ greska }}</h2>
    <RouterLink class="button secondary" to="/narudzbine">
      Nazad na narudžbine
    </RouterLink>
  </div>

  <template v-else-if="narudzbina">
    <div class="page-title">
      <div>
        <p class="eyebrow">Master-detail prikaz</p>
        <h1>Narudžbina {{ narudzbina.broj }}</h1>
      </div>
      <div class="actions right">
        <RouterLink class="button secondary" :to="`/narudzbine/${narudzbina.id}/izmeni`">
          Izmeni narudžbinu
        </RouterLink>
        <RouterLink class="button" :to="`/narudzbine/${narudzbina.id}/stavke/nova`">
          Dodaj stavku
        </RouterLink>
      </div>
    </div>

    <section class="card details">
      <div class="zaglavlje-kartice">
        <h2>Podaci o narudžbini</h2>
        <span :class="['pilula', narudzbina.status]">
          {{ narudzbina.status_naziv }}
        </span>
      </div>
      <div class="stats">
        <div>
          <span>Kupac</span>
          <strong>{{ narudzbina.kupac }}</strong>
        </div>
        <div>
          <span>Elektronska pošta</span>
          <strong>{{ narudzbina.email }}</strong>
        </div>
        <div>
          <span>Datum</span>
          <strong>{{ datum(narudzbina.datum) }}</strong>
        </div>
        <div>
          <span>Broj stavki</span>
          <strong>{{ narudzbina.broj_stavki }}</strong>
        </div>
        <div>
          <span>Ukupan iznos</span>
          <strong class="istaknuto">{{ dinari(narudzbina.ukupan_iznos) }} RSD</strong>
        </div>
      </div>
    </section>

    <section class="section-heading">
      <h2>Stavke narudžbine</h2>
    </section>

    <div v-if="narudzbina.stavke.length" class="table-card">
      <table>
        <thead>
          <tr>
            <th>Proizvod</th>
            <th class="desno">Količina</th>
            <th class="desno">Cena po komadu</th>
            <th class="desno">Iznos</th>
            <th>Akcije</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="stavka in narudzbina.stavke" :key="stavka.id">
            <td>{{ stavka.proizvod_naziv }}</td>
            <td class="desno brojevi">
              {{ stavka.kolicina }} {{ stavka.jedinica_mere }}
            </td>
            <td class="desno brojevi">{{ dinari(stavka.cena_po_komadu) }}</td>
            <td class="desno brojevi">{{ dinari(stavka.iznos) }}</td>
            <td class="table-actions">
              <RouterLink :to="`/stavke/${stavka.id}/izmeni`">Izmeni</RouterLink>
              <button
                type="button"
                class="veza opasno"
                @click="zaBrisanje = { vrsta: 'stavka', stavka }"
              >
                Ukloni
              </button>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3">Ukupno</td>
            <td class="desno brojevi jako">
              {{ dinari(narudzbina.ukupan_iznos) }}
            </td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div v-else class="empty">
      <h2>Ova narudžbina još nema stavki.</h2>
      <p>Dodajte prvu stavku da bi master-detail prikaz bio potpun.</p>
    </div>

    <div class="actions">
      <RouterLink class="button secondary" to="/narudzbine">
        Nazad na narudžbine
      </RouterLink>
      <button
        type="button"
        class="button opasno"
        @click="zaBrisanje = { vrsta: 'narudzbina', stavka: narudzbina }"
      >
        Obriši narudžbinu
      </button>
    </div>

    <PotvrdaBrisanja
      v-if="zaBrisanje"
      :tekst="tekstPotvrde"
      @potvrdi="potvrdiBrisanje"
      @otkazi="zaBrisanje = null"
    />
  </template>
</template>
