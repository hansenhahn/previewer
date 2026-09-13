import { describe, expect, it } from "vitest";

import { apiUrl, atlasImageUrl } from "./api";

describe("helpers de URL", () => {
  it("monta a URL do atlas", () => {
    expect(atlasImageUrl("abc", "fontevent")).toBe(
      "/api/projects/abc/fonts/fontevent/atlas.png",
    );
  });

  it("codifica os segmentos", () => {
    expect(atlasImageUrl("a b", "f/x")).toBe(
      "/api/projects/a%20b/fonts/f%2Fx/atlas.png",
    );
  });

  it("monta a URL base da API", () => {
    expect(apiUrl("/projects")).toBe("/api/projects");
  });
});
