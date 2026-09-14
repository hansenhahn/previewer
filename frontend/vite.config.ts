import { defineConfig } from "vitest/config";

export default defineConfig({
  base: "/static/dist/",
  build: {
    target: "es2022",
    cssTarget: "chrome120",
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
