import { describe, expect, it } from "vitest";

import { buildTree, stripPrefix } from "./tree";

describe("árvore de arquivos", () => {
  it("remove o prefixo da pasta de origem", () => {
    expect(stripPrefix("texts/event/en/a.txt", "texts/")).toBe("event/en/a.txt");
    expect(stripPrefix("outro/a.txt", "texts/")).toBe("outro/a.txt");
  });

  it("agrupa pastas e arquivos e ordena pastas primeiro", () => {
    const tree = buildTree([
      { display: "event/en/a.txt", path: "texts/event/en/a.txt" },
      { display: "event/en/b.txt", path: "texts/event/en/b.txt" },
      { display: "raiz.txt", path: "texts/raiz.txt" },
    ]);
    expect(tree.map((node) => node.name)).toEqual(["event", "raiz.txt"]);
    const event = tree[0];
    expect(event.path).toBeUndefined();
    expect(event.children[0].name).toBe("en");
    expect(event.children[0].children.map((node) => node.name)).toEqual(["a.txt", "b.txt"]);
    expect(event.children[0].children[0].path).toBe("texts/event/en/a.txt");
  });
});
