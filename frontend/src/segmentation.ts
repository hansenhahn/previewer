export interface Segment {
  index: number;
  startLine: number;
  endLine: number;
  prefixLines: string[];
  bodyLines: string[];
  suffixLines: string[];
}

export interface Part {
  kind: "separator" | "segment";
  lines: string[];
  segment?: Segment;
}

export interface AlignedPair {
  original?: Segment;
  translated?: Segment;
}

export function segmentText(segment: Segment): string {
  return [...segment.prefixLines, ...segment.bodyLines, ...segment.suffixLines].join("\n");
}

export function segmentBody(segment: Segment): string {
  return segment.bodyLines.join("\n");
}

function matches(line: string, patterns: string[]): boolean {
  return patterns.some((pattern) => new RegExp(pattern).test(line));
}

function splitDelimiters(
  lines: string[],
  startPatterns: string[],
  endPatterns: string[],
): { prefix: string[]; body: string[]; suffix: string[] } {
  let prefix = 0;
  while (prefix < lines.length && matches(lines[prefix], startPatterns)) {
    prefix += 1;
  }
  let suffix = 0;
  while (
    suffix < lines.length - prefix &&
    matches(lines[lines.length - 1 - suffix], endPatterns)
  ) {
    suffix += 1;
  }
  const bodyEnd = suffix > 0 ? lines.length - suffix : lines.length;
  return {
    prefix: lines.slice(0, prefix),
    body: lines.slice(prefix, bodyEnd),
    suffix: lines.slice(bodyEnd),
  };
}

export function segment(
  text: string,
  startPatterns: string[] = [],
  endPatterns: string[] = [],
): Part[] {
  const lines = text.split("\n");
  if (startPatterns.length === 0) {
    return [{ kind: "separator", lines: [...lines] }];
  }

  const total = lines.length;
  const parts: Part[] = [];
  let separator: string[] = [];
  let index = 0;
  let i = 0;

  while (i < total) {
    if (matches(lines[i], startPatterns)) {
      if (separator.length > 0) {
        parts.push({ kind: "separator", lines: separator });
        separator = [];
      }
      let end: number | undefined;
      let k = i;
      while (k < total) {
        if (k > i && matches(lines[k], endPatterns)) {
          end = k;
          break;
        }
        if (k > i && matches(lines[k], startPatterns)) {
          end = k - 1;
          break;
        }
        k += 1;
      }
      if (end === undefined) {
        end = total - 1;
      }
      const { prefix, body, suffix } = splitDelimiters(
        lines.slice(i, end + 1),
        startPatterns,
        endPatterns,
      );
      parts.push({
        kind: "segment",
        lines: [],
        segment: { index, startLine: i, endLine: end, prefixLines: prefix, bodyLines: body, suffixLines: suffix },
      });
      index += 1;
      i = end + 1;
    } else {
      separator.push(lines[i]);
      i += 1;
    }
  }

  if (separator.length > 0) {
    parts.push({ kind: "separator", lines: separator });
  }
  return parts;
}

export function reconstruct(parts: Part[]): string {
  const lines: string[] = [];
  for (const part of parts) {
    if (part.kind === "segment" && part.segment) {
      lines.push(
        ...part.segment.prefixLines,
        ...part.segment.bodyLines,
        ...part.segment.suffixLines,
      );
    } else {
      lines.push(...part.lines);
    }
  }
  return lines.join("\n");
}

export function segmentsOf(parts: Part[]): Segment[] {
  return parts
    .filter((part) => part.kind === "segment" && part.segment)
    .map((part) => part.segment as Segment);
}

export function align(originalParts: Part[], translatedParts: Part[]): AlignedPair[] {
  const originals = segmentsOf(originalParts);
  const translated = segmentsOf(translatedParts);
  const count = Math.max(originals.length, translated.length);
  const pairs: AlignedPair[] = [];
  for (let i = 0; i < count; i += 1) {
    pairs.push({ original: originals[i], translated: translated[i] });
  }
  return pairs;
}
