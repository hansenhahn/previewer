import { describe, expect, it } from "vitest";

import {
  addDocument,
  closeDocument,
  findDocument,
  markModified,
  markSaved,
  pathAfterClose,
  updateContent,
  type OpenDocument,
} from "./documents";

const a: OpenDocument = { path: "texts/a.txt", content: "a", original: null, modified: false };
const b: OpenDocument = { path: "texts/b.txt", content: "b", original: "B", modified: false };

describe("documents", () => {
  it("adiciona sem duplicar", () => {
    expect(addDocument([a], b)).toEqual([a, b]);
    expect(addDocument([a], a)).toEqual([a]);
  });

  it("encontra e fecha", () => {
    expect(findDocument([a, b], "texts/b.txt")).toEqual(b);
    expect(closeDocument([a, b], "texts/a.txt")).toEqual([b]);
  });

  it("atualiza conteúdo preservando o modificado", () => {
    expect(updateContent([a], a.path, "novo")[0]).toMatchObject({
      content: "novo",
      modified: false,
    });
  });

  it("marca modificado e salvo", () => {
    expect(markModified([a], a.path, "x")[0].modified).toBe(true);
    expect(markSaved([a], a.path, "x")[0]).toMatchObject({ content: "x", modified: false });
  });

  it("escolhe o vizinho após fechar", () => {
    expect(pathAfterClose([a, b], "texts/a.txt")).toBe("texts/b.txt");
    expect(pathAfterClose([a, b], "texts/b.txt")).toBe("texts/a.txt");
    expect(pathAfterClose([a], "texts/a.txt")).toBeUndefined();
  });
});
