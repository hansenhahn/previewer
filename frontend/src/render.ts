import type { LayoutGlyph, AtlasMetrics } from "./api";

export interface DrawCommand {
  sx: number;
  sy: number;
  sw: number;
  sh: number;
  dx: number;
  dy: number;
}

export function buildDrawCommands(
  glyphs: LayoutGlyph[],
  atlas: AtlasMetrics,
): DrawCommand[] {
  const commands: DrawCommand[] = [];
  for (const glyph of glyphs) {
    const sprite = atlas.glyphs[String(glyph.codepoint)];
    if (!sprite) {
      continue;
    }
    commands.push({
      sx: sprite.x,
      sy: sprite.y,
      sw: sprite.width,
      sh: sprite.height,
      dx: glyph.x,
      dy: glyph.y,
    });
  }
  return commands;
}
