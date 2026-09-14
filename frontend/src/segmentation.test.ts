import { describe, expect, it } from "vitest";

import rawCases from "./segmentation_cases.json";
import { align, reconstruct, segment, segmentBody, segmentsOf } from "./segmentation";

interface Case {
  name: string;
  start: string[];
  end: string[];
  text: string;
  segments: { text: string; body: string; start_line: number; end_line: number }[];
  reconstructed: string;
}

const cases = (rawCases as unknown as { cases: Case[] }).cases;

describe("segmentação (conformidade)", () => {
  for (const testCase of cases) {
    it(testCase.name, () => {
      const parts = segment(testCase.text, testCase.start, testCase.end);
      const found = segmentsOf(parts).map((seg) => ({
        text: [...seg.prefixLines, ...seg.bodyLines, ...seg.suffixLines].join("\n"),
        body: segmentBody(seg),
        start_line: seg.startLine,
        end_line: seg.endLine,
      }));
      expect(found).toEqual(testCase.segments);
      expect(reconstruct(parts)).toBe(testCase.reconstructed);
    });
  }

  it("abstrai os delimitadores no body", () => {
    const parts = segment("<d>\nA\n</d>", ["^<d>"], ["^</d>"]);
    const [seg] = segmentsOf(parts);
    expect(seg.prefixLines).toEqual(["<d>"]);
    expect(seg.bodyLines).toEqual(["A"]);
    expect(seg.suffixLines).toEqual(["</d>"]);
  });

  it("marca não pareados no alinhamento por ordem", () => {
    const original = segment("<d>\nA\n</d>\n<d>\nB\n</d>", ["^<d>"], ["^</d>"]);
    const translated = segment("<d>\nA'\n</d>", ["^<d>"], ["^</d>"]);
    const pairs = align(original, translated);
    expect(pairs).toHaveLength(2);
    expect(pairs[1].original).toBeDefined();
    expect(pairs[1].translated).toBeUndefined();
  });
});

