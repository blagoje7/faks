<script setup>
// potvrda se generise na klijentu, bez confirm() dijaloga
defineProps({
  naslov: { type: String, default: "Potvrda brisanja" },
  tekst: { type: String, required: true },
});

defineEmits(["potvrdi", "otkazi"]);
</script>

<template>
  <div class="modal-pozadina" @click.self="$emit('otkazi')">
    <div class="modal" role="dialog" aria-modal="true">
      <h2>{{ naslov }}</h2>
      <p>{{ tekst }}</p>
      <div class="actions right">
        <button class="button secondary" type="button" @click="$emit('otkazi')">
          Odustani
        </button>
        <button class="button opasno" type="button" @click="$emit('potvrdi')">
          Obrisi
        </button>
      </div>
    </div>
  </div>
</template>
