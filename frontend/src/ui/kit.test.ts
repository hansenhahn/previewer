import { describe, expect, it } from "vitest";

import { classNames, variantClass } from "./kit";

describe("helpers do kit", () => {
  it("junta apenas classes não vazias", () => {
    expect(classNames("a", false, undefined, null, "b")).toBe("a b");
    expect(classNames()).toBe("");
  });

  it("adiciona sufixo apenas para variantes não padrão", () => {
    expect(variantClass("pv-button")).toBe("pv-button");
    expect(variantClass("pv-button", "default")).toBe("pv-button");
    expect(variantClass("pv-button", "primary")).toBe("pv-button pv-button--primary");
  });
});
