import { describe, expect, it } from "vitest";

import rawCases from "./layout_cases.json";
import { computeLayout } from "./layout";
import type { AtlasMetrics, Screen } from "./api";

interface Expected {
  glyphs?: { codepoint: number; x: number; y: number }[];
  glyph_count?: number;
  overflow_horizontal: boolean;
  overflow_vertical: boolean;
}

interface LayoutCase {
  name: string;
  matches: string[];
  tags: string[];
  cursor_line: number;
  text: string;
  new_line?: number;
  expected: Expected;
}

const data = rawCases as unknown as {
  atlas: AtlasMetrics;
  screen: Screen;
  cases: LayoutCase[];
};

describe("layout conformance", () => {
  for (const testCase of data.cases) {
    it(testCase.name, () => {
      const screen: Screen = {
        ...data.screen,
        new_line: testCase.new_line ?? data.screen.new_line,
      };
      const result = computeLayout(
        testCase.text,
        screen,
        data.atlas,
        testCase.matches,
        testCase.tags,
        testCase.cursor_line,
      );

      if (testCase.expected.glyph_count !== undefined) {
        expect(result.glyphs).toHaveLength(testCase.expected.glyph_count);
      } else {
        expect(
          result.glyphs.map((glyph) => ({
            codepoint: glyph.codepoint,
            x: glyph.x,
            y: glyph.y,
          })),
        ).toEqual(testCase.expected.glyphs);
      }
      expect(result.overflowHorizontal).toBe(testCase.expected.overflow_horizontal);
      expect(result.overflowVertical).toBe(testCase.expected.overflow_vertical);
    });
  }
});
