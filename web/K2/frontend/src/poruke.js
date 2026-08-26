import { reactive } from "vue";

export const poruke = reactive([]);

let brojac = 0;

export function dodajPoruku(tekst, vrsta = "uspeh") {
  const id = ++brojac;
  poruke.push({ id, tekst, vrsta });
  setTimeout(() => ukloniPoruku(id), 5000);
}

export function ukloniPoruku(id) {
  const indeks = poruke.findIndex((poruka) => poruka.id === id);
  if (indeks !== -1) {
    poruke.splice(indeks, 1);
  }
}
