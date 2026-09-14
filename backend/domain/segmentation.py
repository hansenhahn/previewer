import re
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Segment:
    index: int
    start_line: int
    end_line: int
    prefix_lines: tuple[str, ...] = ()
    body_lines: tuple[str, ...] = ()
    suffix_lines: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        return "\n".join((*self.prefix_lines, *self.body_lines, *self.suffix_lines))

    @property
    def body(self) -> str:
        return "\n".join(self.body_lines)


@dataclass(frozen=True, slots=True)
class Part:
    kind: Literal["separator", "segment"]
    lines: tuple[str, ...] = ()
    segment: Segment | None = None

    @property
    def is_segment(self) -> bool:
        return self.kind == "segment"


@dataclass(frozen=True, slots=True)
class AlignedPair:
    original: Segment | None = None
    translated: Segment | None = None


def _matches(line: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, line) for pattern in patterns)


def _split_delimiters(
    lines: list[str],
    start_patterns: tuple[str, ...],
    end_patterns: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    prefix = 0
    while prefix < len(lines) and _matches(lines[prefix], start_patterns):
        prefix += 1
    suffix = 0
    while suffix < len(lines) - prefix and _matches(lines[len(lines) - 1 - suffix], end_patterns):
        suffix += 1
    body_end = len(lines) - suffix if suffix else len(lines)
    return (
        tuple(lines[:prefix]),
        tuple(lines[prefix:body_end]),
        tuple(lines[body_end:]),
    )


def segment(
    text: str,
    start_patterns: tuple[str, ...] = (),
    end_patterns: tuple[str, ...] = (),
) -> tuple[Part, ...]:
    lines = text.split("\n")
    if not start_patterns:
        return (Part("separator", tuple(lines)),)

    total = len(lines)
    parts: list[Part] = []
    separator: list[str] = []
    index = 0
    i = 0
    while i < total:
        if _matches(lines[i], start_patterns):
            if separator:
                parts.append(Part("separator", tuple(separator)))
                separator = []
            end: int | None = None
            k = i
            while k < total:
                if k > i and _matches(lines[k], end_patterns):
                    end = k
                    break
                if k > i and _matches(lines[k], start_patterns):
                    end = k - 1
                    break
                k += 1
            if end is None:
                end = total - 1
            prefix, body, suffix = _split_delimiters(lines[i : end + 1], start_patterns, end_patterns)
            parts.append(
                Part(
                    "segment",
                    segment=Segment(index, i, end, prefix, body, suffix),
                )
            )
            index += 1
            i = end + 1
        else:
            separator.append(lines[i])
            i += 1

    if separator:
        parts.append(Part("separator", tuple(separator)))
    return tuple(parts)


def segment_by_separators(
    text: str,
    separator_patterns: tuple[str, ...],
) -> tuple[Part, ...]:
    lines = text.split("\n")
    if not separator_patterns:
        return (Part("separator", tuple(lines)),)

    parts: list[Part] = []
    buffer: list[str] = []
    marks: list[str] = []
    start = 0
    index = 0

    def flush_segment(end: int) -> None:
        nonlocal buffer, index
        if buffer:
            parts.append(
                Part("segment", segment=Segment(index, start, end, (), tuple(buffer), ()))
            )
            index += 1
            buffer = []

    def flush_marks() -> None:
        nonlocal marks
        if marks:
            parts.append(Part("separator", tuple(marks)))
            marks = []

    for position, line in enumerate(lines):
        if _matches(line, separator_patterns):
            flush_segment(position - 1)
            marks.append(line)
        else:
            flush_marks()
            if not buffer:
                start = position
            buffer.append(line)

    flush_segment(len(lines) - 1)
    flush_marks()
    return tuple(parts)


def reconstruct(parts: tuple[Part, ...]) -> str:
    lines: list[str] = []
    for part in parts:
        if part.kind == "segment" and part.segment is not None:
            lines.extend(part.segment.prefix_lines)
            lines.extend(part.segment.body_lines)
            lines.extend(part.segment.suffix_lines)
        else:
            lines.extend(part.lines)
    return "\n".join(lines)


def segments_of(parts: tuple[Part, ...]) -> tuple[Segment, ...]:
    return tuple(part.segment for part in parts if part.is_segment and part.segment)


def align(
    original_parts: tuple[Part, ...],
    translated_parts: tuple[Part, ...],
) -> tuple[AlignedPair, ...]:
    originals = segments_of(original_parts)
    translated = segments_of(translated_parts)
    count = max(len(originals), len(translated))
    return tuple(
        AlignedPair(
            original=originals[i] if i < len(originals) else None,
            translated=translated[i] if i < len(translated) else None,
        )
        for i in range(count)
    )
