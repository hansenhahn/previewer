## Context

Ver `proposal.md` — Why. Hoje: `domain/project.py` parseia o `manifest.json`
(formato/versão, name, encoding, texts, fonts, backgrounds, screens, tags,
matches); `domain/layout.py` usa `matches`/`tags` para a prévia; o cliente tem
`frontend/src/layout.ts` espelhando o domínio com casos de conformidade
compartilhados; a UI tem visão de editor e comparação. O legado detectava blocos
por regex (`legacy/editor.py`). Referência de UX: memoQ (caixas por segmento).

## Goals / Non-Goals

**Goals:**
- Configurar segmentação no manifesto (início/fim).
- Segmentar e reconstruir com fidelidade (separadores preservados).
- Alinhar original×traduzido por ordem, sinalizando não pareados.
- Visão de caixas editáveis, com status/navegação e salvamento por reconstrução.
- Manter preview, tokens, adaptador e isolamento da biblioteca.

**Non-Goals:**
- Memória de tradução, glossário, QA, propagação.
- IDs/marcadores dentro do texto; diff linha a linha; múltiplos arquivos por vez.
- Novo endpoint: salvamento continua via `PUT /files/<path>`.

## Decisions

### 1. Manifesto: seção `segments` (aditiva)
```json
"segments": { "start": ["^<dialogo>"], "end": ["^</dialogo>"] }
```
`domain/project.py` ganha `Segments(start: tuple[str, ...], end: tuple[str, ...])`
(ou `None`). `parse_manifest` valida: objeto opcional com `start`/`end` como
listas de strings. Projetos sem a seção continuam válidos.

### 2. Modelo de parts para reconstrução fiel
`domain/segmentation.py` expõe:
```python
@dataclass(frozen=True) class Segment:  index: int; text: str; start_line: int; end_line: int
@dataclass(frozen=True) class Part:     kind: Literal["separator","segment"]; lines: tuple[str,...]; segment: Segment | None
def segment(text, start_patterns, end_patterns) -> tuple[Part, ...]
def reconstruct(parts) -> str
```
- Split por `\n` (o codec normaliza newlines); classificar linhas com padrões de
  início/fim via `search` (casa em qualquer posição da linha).
- Um bloco vai da linha de início até a linha de fim (inclusive); sem fim, até a
  linha anterior ao próximo início ou o fim do arquivo.
- **Reconstrução**: `parts.flatMap(p => p.is_segment ? p.text.split("\n") : p.lines).join("\n")`
  reproduz o texto exatamente quando nada foi editado.

### 3. Espelho no cliente + conformidade
`frontend/src/segmentation.ts` espelha a mesma lógica (JS `RegExp(...).test` /
`search`), com casos compartilhados em `frontend/src/segmentation_cases.json`
rodando no pytest e no vitest (mesmo padrão do layout). Cobre: bloco simples,
vários blocos, sem fim, sem configuração, texto com separadores nas bordas e
round-trip de reconstrução.

### 4. Alinhamento por ordem
`align(original_segments, translated_segments) -> { pairs: [(o?, t?)], unpaired: ... }`.
Pareia por índice até o mínimo; excedentes viram "sem par" (original-only ou
translated-only). A UI sinaliza.

### 5. Visão CAT (`frontend/src/shell/cat.ts`)
- Alternância **Editor | Segmentos** na barra do texto.
- Cada par vira uma caixa: original (somente-leitura) + traduzido (editável).
- Status por segmento: `vazio` (traduzido só com espaços) ou `preenchido`.
- Navegação próximo/anterior; aviso quando houver não pareados; mensagem quando o
  projeto não tem `segments`.

### 6. Fonte da verdade e prévia
O documento mantém `content` (texto cru). A visão CAT segmenta `content`; ao
editar um segmento, remonta `content` (`reconstruct`) e atualiza o documento (e o
editor plano, se visível). A prévia continua consumindo `content`, então reflete
edições não salvas. Salvar faz `PUT` de `content`.

### 7. Compatibilidade
Projetos sem `segments` seguem iguais; a visão CAT apenas informa indisponível. A
segmentação não altera o formato dos textos nem o empacotamento.

## Risks / Trade-offs

- [Fidelidade da reconstrução] → função pura + testes de round-trip (original ==
  reconstruct(parts)); conformidade Python×JS.
- [Divergência de regex Python×JS] → mesmo trade-off do layout; padrões simples e
  documentado.
- [Bloco sem fim configurado] → regra explícita (termina no próximo início/fim de
  arquivo), coberta por teste.
- [Editor plano vs CAT divergirem] → estado único (`content`); CAT sempre
  re-segmenta ao abrir e remonta ao editar.

## Migration Plan

- Aditivo: novo campo no manifesto, novos módulos e uma visão opcional.
- Rollback: remover `segments`, `segmentation.*` e `shell/cat.ts`; a UI volta ao
  editor/comparação.

## Open Questions

- Alinhamento por IDs e sincronização de rolagem entre caixas — decidível depois.
- Próximas features de CAT (memória, glossário, QA) — changes futuros.
