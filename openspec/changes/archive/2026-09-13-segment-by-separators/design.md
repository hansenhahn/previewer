## Context

O modo atual (`segments.start`/`segments.end`) cria segmentos iniciados por uma
linha que casa com `start`. No formato do `playton-3` o texto do diálogo vem
**depois** do marcador `!***!`, então esse modo enquadra o nome em vez do diálogo.
Ver `proposal.md`.

## Goals / Non-Goals

**Goals:** segmentar por separadores (blocos como segmentos); paridade
domínio/cliente; reconstrução fiel; manter o modo `start`/`end`.

**Non-Goals:** substituir `start`/`end`; alterar a UI.

## Decisions

### 1. Modo separador
`segment_by_separators(text, patterns)` (e o espelho `segmentBySeparators`):
percorre as linhas; linhas que casam viram separadores (agrupadas em `Part("separator")`);
sequências de linhas que não casam viram `Part("segment")` com `bodyLines` = o bloco.

### 2. Seleção do modo
A visão por segmentos usa o modo separador quando `segments.separators` está
presente/não-vazio; caso contrário, usa `start`/`end`. Sem nenhum dos dois, não há
segmentação.

### 3. Manifesto
`Segments` ganha `separators: tuple[str, ...]`; `parse_manifest` lê
`segments.separators` e `to_dict` o devolve. Ausente = vazio (compatível).

### 4. Reconstrução
`reconstruct` já concatena separadores e segmentos na ordem; o modo separador mantém
essa garantia (verificado no domínio e no cliente).

## Risks / Trade-offs

- [Formatos mistos no mesmo projeto (txt vs nazo)] → o modo separador captura o
  diálogo nos dois; em `rc/nazo` a linha de cabeçalho `[....]` pode aparecer junto do
  bloco. Aceitável; ajustável depois.
- [Duas implementações (Python/TS)] → cobertas por testes equivalentes nos dois lados.

## Migration Plan

- Aditivo e compatível: projetos sem `separators` seguem iguais. `playton-3` passa a
  declarar `segments.separators`.

## Open Questions

- Tratar cabeçalhos de `nazo` como prefixo separado, se necessário.
