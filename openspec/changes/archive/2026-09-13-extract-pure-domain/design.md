## Context

Ver `proposal.md` — Why. Hoje `nftr.py`, `drawer.py` e `editor.py` concentram as
regras de fonte, layout e encoding acopladas a GTK/UI. O `MIGRATION.md` define a
arquitetura em camadas (`web → domain`, `infra → domain`) e o contrato de
extensão (OCP) em §3.1. Esta fase cria o `domain/` puro, sem ainda integrá-lo a
um web app. Não existem fontes `.NFTR` versionadas no repositório e `nftr.py`
usa semântica de Python 2.

## Goals / Non-Goals

**Goals:**
- Pacote `domain/` puro, sem dependências de Flask/GTK/storage.
- Contratos `FontFormat`/`Font` extensíveis, com NFTR como primeiro adaptador.
- Portar com fidelidade o comportamento observável de decoding NFTR, layout da
  tela 256×192 e codec de texto.
- Suíte de testes executável em Python 3.13+.

**Non-Goals:**
- Integrar o domínio ao `editor.py`/`drawer.py` legados (fases seguintes).
- Renderização real em pixels (cairo/canvas) — esta fase produz dados, não imagem.
- Adaptador TTF/OTF, segundo `ProjectFormat`, upload de projeto, web app, Docker.
- Plugin discovery de terceiros.

## Decisions

### 1. Pacote `domain/` no topo do repositório
Estrutura nova, legível e isolável:
```
domain/
  fonts/
    base.py       # Protocol FontFormat, Protocol Font, dataclass Glyph
    registry.py   # register(fmt), load_font(data)
    nftr.py       # NftrFontFormat (adaptador)
    __init__.py   # registro dos adaptadores embutidos
  layout.py       # ScreenConfig, layout(text, font, config) -> list[PlacedGlyph]
  text.py         # decode_text / encode_text
  errors.py       # exceções do domínio
tests/
  fixtures/fonts/
pyproject.toml
```
Alternativa: layout `src/previewer/domain/` (ideal quando o web app chegar).
Adiada para não reestruturar o repo legado agora; a mudança é aditiva.

### 2. Contratos com `typing.Protocol` (structural typing)
`FontFormat` e `Font` como `Protocol`, em vez de ABC/herança. Motivo: adaptadores
não precisam herdar de uma base comum e o domínio depende da estrutura, não de
uma classe concreta — melhor para OCP e para testes com dublês. O contrato:

```python
class FontFormat(Protocol):
    name: str
    def sniff(self, data: bytes) -> bool: ...
    def load(self, data: bytes) -> "Font": ...

class Font(Protocol):
    line_height: int
    def glyph(self, codepoint: int, size: int | None = None) -> "Glyph | None": ...
    def advance(self, codepoint: int) -> int: ...
```

`size` existe para acomodar formatos vetoriais depois; adaptadores bitmap
(NFTR) o ignoram e devolvem o tamanho nativo — evita mudar o contrato na fase do
TTF.

### 3. Registro explícito como único ponto de extensão
`registry.load_font(data)` percorre os adaptadores registrados e usa `sniff`
(magic bytes) para escolher. Os adaptadores embutidos são registrados em
`domain/fonts/__init__.py`. Adicionar formato = **novo módulo + uma linha de
registro**; `registry`, `layout` e consumidores não mudam. Alternativa: entry
points/`pkgutil` (OCP "puro" sem tocar em arquivo existente) — rejeitada agora
por YAGNI e por esconder erros de carga; é o caminho de upgrade quando houver
plugins de terceiros.

### 4. Glifos normalizados para bitmap A8 no domínio
O adaptador NFTR entrega `Glyph(codepoint, pixels: bytes, width, height,
advance)`, com `width`/`height` já ajustados ao passo de byte e `pixels` em A8
(1 byte/pixel). Motivo: é o denominador comum que mantém o front/atlas
agnóstico de formato e evita vazar detalhes do CGLP. Alternativa: guardar os
bits brutos e padding no renderizador — rejeitada por espalhar regras de formato.

### 5. Layout sem cairo
`layout` recebe texto, `Font` e `ScreenConfig` e devolve glifos posicionados
(`PlacedGlyph(codepoint, x, y, glyph)`) mais sinalizações de transbordo
horizontal/vertical. Nada de cairo/pixels no domínio. Isso espelha os limites
256×192 e a quebra por `ScreenNewLine` do `drawer.py` atual, mas como dados
testáveis. Alternativa: manter o desenho junto do layout (como hoje) —
rejeitada por violar a pureza da camada.

### 6. Codec de texto com falha explícita
`decode_text(data, encoding) -> str` normaliza `\r\n`/`\r` para `\n` e propaga
erro em bytes inválidos; `encode_text(text, encoding) -> bytes` garante
round-trip. As exceções de `codecs` são encapsuladas em erros do domínio
(`errors.py`) para não vazar detalhes de baixo nível. Alternativa: `errors=replace`
silencioso — rejeitada por mascarar corrupção de arquivo.

### 7. Testes com pytest e fixtures
`pytest` como runner; fixtures em `tests/fixtures/fonts/`. Como não há fontes
versionadas, os testes usam **um NFTR mínimo sintético** gerado por helper
(determinístico, sem dependência externa) e, **se disponível**, ao menos uma
fonte real obtida do projeto original. Fidelidade do parser depende de pelo menos
uma fonte real; o sintético cobre os caminhos de erro e contrato. Alternativa:
só sintético — mais frágil quanto a formatos reais do CGLP/CMAP.

### 8. `pyproject.toml` mínimo
Configura `requires-python = ">=3.13"`, o pacote `domain` e as opções do pytest.
Motivo: dá ao domínio um runner e empacotamento próprios e prepara o terreno do
web app sem trazer dependências de runtime além da stdlib.

## Risks / Trade-offs

- [Ausência de fontes NFTR reais] → incluir ao menos uma fixture real; se
  indisponível, tratar como bloqueio parcial e registrar em `tests/fixtures/README`.
- [Fidelidade da portabilidade] → os testes de NFTR devem reproduzir métricas e
  bitmaps do `nftr.py` original para casos conhecidos (golden values).
- [Vazamento de regra de formato para o layout] → proibir `import` de
  `domain.fonts.nftr` em `layout.py`; revisão de código + teste que troca o
  adaptador por um dublê.
- [`Protocol` não valida em runtime] → testes de contrato carregam cada adaptador
  registrado e exercitam `sniff`/`load`/`glyph`/`advance`.

## Migration Plan

- Mudança **aditiva**: nenhum arquivo legado é alterado. O app atual continua
  funcionando; a integração ocorre nas fases seguintes.
- Rollback: remover `domain/`, `tests/` e `pyproject.toml`.
- Ordem: `text` e `fonts` primeiro, `layout` depois (depende de `Font`); testes
  acompanham cada módulo.

## Open Questions

- Framework de teste além do pytest (cobertura mínima exigida)? Pode ser definido
  na implementação sem afetar specs ou abordagem.
