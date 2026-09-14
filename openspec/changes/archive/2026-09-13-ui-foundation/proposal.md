## Why

A UI atual é básica e feia (CSS solto, sem sistema de design). Queremos adotar o
**Web Awesome** (sucessor do Shoelace, dos criadores do Font Awesome) para um
visual mais polido — mas **sem acoplar o app à biblioteca**: trocar por Bootstrap
(ou outra) deve ser um novo adaptador, não um retrabalho. Isso é um refactor de
apresentação, sem mudança de comportamento (`skip_specs`).

## What Changes

- **Design tokens próprios** (`--pv-*`: cores, espaçamento, tipografia, raio,
  sombra) com tema claro/escuro, independentes da biblioteca.
- **Camada de UI desacoplada** em `frontend/src/ui/`: uma interface `UiKit`
  (botão, select, toast/callout) e uma implementação Web Awesome. O app importa
  só o adaptador — nenhum `<wa-*>` ou classe da lib fora dele.
- **Migrar a UI atual** (sidebar, toolbar, painéis, lista de arquivos, upload,
  feedback de erro) para tokens + adaptador, mantendo o comportamento.
- **Mapeamento de tema** da biblioteca para os nossos tokens (um arquivo por
  biblioteca), viabilizando o fallback.
- **Carregamento sob demanda** dos componentes Web Awesome efetivamente usados.

## Capabilities

### New Capabilities
- Nenhuma. Mudança de apresentação/arquitetura de UI: `skip_specs: true`.

### Modified Capabilities
- Nenhuma (comportamento inalterado).

## Impact

- **Novo:** `frontend/src/ui/` (`tokens.css`, `theme.css`, `kit.ts`,
  `kit-webawesome.ts`, `index.ts`).
- **Alterado:** `frontend/index.html` (esqueleto sem classes da lib),
  `frontend/src/main.ts`, `frontend/src/ui.ts`, `frontend/src/style.css`,
  `frontend/package.json` (Web Awesome).
- **Sem alteração:** backend, API, domínio, preview/canvas e o comportamento.

## Não-objetivos

- Implementar o adaptador Bootstrap agora (só garantir que seja viável e barato).
- Adotar componentes Pro do Web Awesome.
- Novas funcionalidades de UX (busca, diff, redimensionamento de painéis) — vêm
  em changes seguintes.
- Trocar o CodeMirror ou o canvas.
