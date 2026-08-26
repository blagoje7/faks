import { fileURLToPath, URL } from "node:url";

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  // Produkcijski build ide direktno u Flask static folder, pa se na
  // prezentaciji pokreće samo jedan server.
  build: {
    outDir: "../backend/static",
    emptyOutDir: true,
  },
  // U razvoju Vite servira klijent na 5173 i prosleđuje /api Flask-u na 5000,
  // pa klijent uvek poziva iste relativne putanje.
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
