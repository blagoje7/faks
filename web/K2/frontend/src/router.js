import { createRouter, createWebHistory } from "vue-router";

import NarudzbinaDetalji from "@/components/NarudzbinaDetalji.vue";
import NarudzbinaForma from "@/components/NarudzbinaForma.vue";
import NarudzbineLista from "@/components/NarudzbineLista.vue";
import Pocetna from "@/components/Pocetna.vue";
import ProizvodForma from "@/components/ProizvodForma.vue";
import ProizvodiLista from "@/components/ProizvodiLista.vue";
import StavkaForma from "@/components/StavkaForma.vue";

const routes = [
  { path: "/", name: "pocetna", component: Pocetna },

  { path: "/narudzbine", name: "narudzbine", component: NarudzbineLista },
  { path: "/narudzbine/nova", name: "narudzbina-nova", component: NarudzbinaForma },
  {
    path: "/narudzbine/:id",
    name: "narudzbina-detalji",
    component: NarudzbinaDetalji,
    props: true,
  },
  {
    path: "/narudzbine/:id/izmeni",
    name: "narudzbina-izmena",
    component: NarudzbinaForma,
    props: true,
  },
  {
    path: "/narudzbine/:narudzbinaId/stavke/nova",
    name: "stavka-nova",
    component: StavkaForma,
    props: true,
  },
  {
    path: "/stavke/:id/izmeni",
    name: "stavka-izmena",
    component: StavkaForma,
    props: true,
  },

  { path: "/proizvodi", name: "proizvodi", component: ProizvodiLista },
  { path: "/proizvodi/novi", name: "proizvod-novi", component: ProizvodForma },
  {
    path: "/proizvodi/:id/izmeni",
    name: "proizvod-izmena",
    component: ProizvodForma,
    props: true,
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
});
