import { describe, expect, it } from "vitest";

import { apiUrl, atlasImageUrl, fileUrl } from "./api";

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

  it("monta a URL do arquivo por variante", () => {
    expect(fileUrl("abc", "texts/cap01.txt")).toBe(
      "/api/projects/abc/files/texts/cap01.txt",
    );
    expect(fileUrl("abc", "texts/cap01.txt", "original")).toBe(
      "/api/projects/abc/files/texts/cap01.txt?variant=original",
    );
  });
});
