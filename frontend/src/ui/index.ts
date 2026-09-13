export * from "./kit";

// Ponto único de troca: aponte para outra implementação (ex.: kit-bootstrap.ts)
// para mudar de biblioteca sem tocar no resto do app.
export { kit } from "./kit-webawesome";
