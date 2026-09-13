## Why

O núcleo do previewer (decodificação de fonte NFTR, layout da tela e encoding do
texto) hoje só existe acoplado ao app GTK/Python 2: `nftr.py` importa `gtk`,
`drawer.py` mistura layout com cairo e `editor.py` faz o decode/encode no meio da
UI. Isso impede testar, reusar no web app e estender formatos (OCP). Esta é a
**Fase 1 do MIGRATION.md** ("Domínio puro — maior risco") e precisa vir primeiro,
pois é o alicerce e o único risco técnico real da migração.

## What Changes

- Criar o pacote `domain/` **puro** (sem Flask, sem GTK, sem storage) com as
  regras hoje embutidas na UI.
- Portar `nftr.py` para Python 3: bytes explícitos, `zip` lazy, sem `import gtk`,
  preservando a leitura de `FINF`/`CGLP`/`CWDH`/`CMAP` e a decodificação de
  glifos para mapa de bits (A8).
- Extrair de `drawer.py` a lógica de layout da tela 256×192: posicionamento
  X/Y, avanço de glifo, quebra por `ScreenNewLine`, detecção de linha-pivô
  (`Matches`) e remoção de `Tags`, e o limite de overflow vertical/horizontal.
- Extrair de `editor.py` o codec de texto do projeto: decodificar/encodificar
  usando o `Encoding` do projeto, preservando a escrita round-trip.
- Introduzir os contratos de extensão (`FontFormat` com `sniff`/`load` →
  `Font` genérico + `rasterize`) definidos no MIGRATION.md §3.1, com o NFTR como
  **primeiro adaptador** registrado — sem `if format == ...` no núcleo.
- Adicionar testes unitários do domínio com fixtures de fontes NFTR reais e um
  projeto de exemplo.

**BREAKING** (apenas para o código novo): o domínio passa a ser a única fonte de
verdade dessas regras. O app legado (`editor.py`, `drawer.py`, `nftr.py`) fica
intocado nesta fase e é substituído nas fases seguintes.

## Capabilities

### New Capabilities
- `font-decoding`: contrato `FontFormat`/`Font` e decodificação de fontes, com o
  NFTR como primeiro adaptador (header, CGLP, CWDH, CMAP e glifos em bitmap).
- `screen-layout`: transformar texto + fonte + configuração de tela na sequência
  de posições de glifos da tela 256×192, incluindo quebra, pivô e overflow.
- `project-text`: ler e escrever o texto do projeto respeitando o encoding
  declarado, com round-trip preservado.

### Modified Capabilities
- Nenhuma. Projeto novo, ainda sem specs principais (`openspec/specs/` vazio).

## Impact

- **Novo:** pacote `domain/` (`domain/fonts/`, `domain/layout.py`,
  `domain/text.py`), suíte de testes e fixtures.
- **Não alterado:** `editor.py`, `drawer.py`, `nftr.py`, `writer.py`, `dialogs/`,
  `editor.ui`, scripts de build. O app legado continua como está nesta fase.
- **Dependências novas:** `pytest` (desenvolvimento). Sem dependências de runtime
  além da stdlib (`struct`) para o NFTR.
- **Risco/dado pendente:** não há fontes `.NFTR` versionadas no repositório;
  fixtures reais precisam ser obtidas/anonimizadas antes dos testes (ver design).
- Referência: `MIGRATION.md` §3.1 (OCP) e Fase 1.
