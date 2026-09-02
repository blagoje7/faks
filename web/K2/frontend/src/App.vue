<script setup>
import { poruke, ukloniPoruku } from "@/poruke";
</script>

<template>
  <header class="topbar">
    <div class="container nav">
      <RouterLink class="logo" to="/">Narudzbine</RouterLink>
      <nav>
        <RouterLink to="/">Pocetna</RouterLink>
        <RouterLink to="/narudzbine">Narudzbine</RouterLink>
        <RouterLink to="/proizvodi">Proizvodi</RouterLink>
        <RouterLink class="button small" to="/narudzbine/nova">
          Nova narudzbina
        </RouterLink>
      </nav>
    </div>
  </header>

  <div class="poruke">
    <div
      v-for="poruka in poruke"
      :key="poruka.id"
      :class="['poruka', poruka.vrsta]"
      @click="ukloniPoruku(poruka.id)"
    >
      {{ poruka.tekst }}
    </div>
  </div>

  <main class="container content">
    <RouterView />
  </main>
</template>
