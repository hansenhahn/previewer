import type { AtlasMetrics, LayoutGlyph, Screen } from "./api";

export const SCREEN_WIDTH = 256;
export const SCREEN_HEIGHT = 192;

export interface ClientLayoutResult {
  glyphs: LayoutGlyph[];
  overflowHorizontal: boolean;
  overflowVertical: boolean;
}

function stripTags(line: string, tags: string[]): string {
  let result = line;
  for (const tag of tags) {
    result = result.replace(new RegExp(tag, "g"), "");
  }
  return result;
}

function matchesAtStart(line: string, patterns: string[]): boolean {
  return patterns.some((pattern) => line.search(new RegExp(pattern)) === 0);
}

function pivotLine(lines: string[], matches: string[], cursorLine: number): number {
  let index = Math.min(cursorLine, lines.length - 1);
  while (index >= 0) {
    if (matchesAtStart(lines[index], matches)) {
      return index + 1;
    }
    index -= 1;
  }
  return 0;
}

export function computeLayout(
  text: string,
  screen: Screen,
  atlas: AtlasMetrics,
  matches: string[] = [],
  tags: string[] = [],
  cursorLine = 0,
): ClientLayoutResult {
  const lines = text.split("\n");
  const start = matches.length > 0 ? pivotLine(lines, matches, cursorLine) : 0;

  const glyphs: LayoutGlyph[] = [];
  let overflowHorizontal = false;
  let overflowVertical = false;
  let y = screen.y;

  for (let lineIndex = start; lineIndex < lines.length; lineIndex += 1) {
    if (y > SCREEN_HEIGHT) {
      overflowVertical = true;
      break;
    }

    // Limites (matches) sao estruturais: casam na linha crua, mesmo que as tags
    // as apaguem para exibicao.
    if (matches.length > 0 && matchesAtStart(lines[lineIndex], matches)) {
      break;
    }

    const stripped = stripTags(lines[lineIndex], tags);
    if (stripped.length === 0) {
      // linha sem glifos (delimitador/slot vazio): nao ocupa espaco vertical
      continue;
    }

    let x = screen.x;
    for (const character of stripped) {
      const codepoint = character.codePointAt(0) ?? 0;
      const sprite = atlas.glyphs[String(codepoint)];
      const advance = sprite ? sprite.advance : atlas.default_advance;
      const leading = sprite ? sprite.leading : 0;
      glyphs.push({
        codepoint,
        index: sprite ? sprite.index : -1,
        x: x + leading,
        y,
      });
      x += advance + 1;
      if (x > SCREEN_WIDTH) {
        overflowHorizontal = true;
        break;
      }
    }
    y += screen.new_line;
  }

  return { glyphs, overflowHorizontal, overflowVertical };
}
