import { defineConfig } from "vitest/config";

export default defineConfig({
  base: "/static/dist/",
  build: {
    outDir: "../backend/web/static/dist",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  test: {
    environment: "node",
  },
});
