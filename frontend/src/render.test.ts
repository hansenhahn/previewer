import { describe, expect, it } from "vitest";

import { buildDrawCommands } from "./render";
import type { AtlasMetrics } from "./api";

const atlas: AtlasMetrics = {
  line_height: 12,
  default_advance: 4,
  image: { width: 256, height: 24, url: "/atlas.png" },
  glyphs: {
    "65": { index: 31, x: 0, y: 0, width: 16, height: 12, advance: 7, leading: 0 },
  },
};

describe("buildDrawCommands", () => {
  it("mapeia glifos posicionados para comandos do atlas", () => {
    const commands = buildDrawCommands([{ codepoint: 65, index: 31, x: 8, y: 16 }], atlas);
    expect(commands).toEqual([
      { sx: 0, sy: 0, sw: 16, sh: 12, dx: 8, dy: 16 },
    ]);
  });

  it("ignora glifos ausentes do atlas", () => {
    const commands = buildDrawCommands([{ codepoint: 90, index: 1, x: 0, y: 0 }], atlas);
    expect(commands).toEqual([]);
  });
});
