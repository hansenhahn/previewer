## Context

Ver `proposal.md` — Why. A 3a expôs `/api` (projetos, arquivos, atlas) e o
`domain.layout` (Python) já calcula a disposição da tela 256×192. Decisão do
usuário: **layout no cliente** (o preview é efêmero; sem round-trip por edição) e
**UI de fluxo completo**. O serviço Flask atual tem `/`, `/healthz` e `/api`.
Node 24 e npm 11 estão disponíveis no ambiente.

## Goals / Non-Goals

**Goals:**
- SPA em Vite + TypeScript + CodeMirror 6 consumindo `/api`.
- Layout calculado no cliente espelhando `domain.layout`, com suíte de
  conformidade compartilhada; endpoint de background.
- Canvas 256×192 com zoom nítido e atualização pela edição.
- Build do frontend integrado ao `Dockerfile` (stage Node).

**Non-Goals:**
- Auth/GitHub, multiusuário, S3, colaboração (Fases 4/5 e ideia registrada).
- Renderização de imagem no servidor.
- Framework de UI (React/Vue), i18n, tema, mobile.

## Decisions

### 1. Stack e estrutura do frontend
Vite + TypeScript puro (sem framework) + CodeMirror 6.
```
frontend/
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  src/
    main.ts        # bootstrap e roteamento por hash
    api.ts         # cliente HTTP da /api
    state.ts       # projeto/tela/arquivo atuais
    ui.ts          # lista/importação de projetos e árvore de arquivos
    editor.ts      # CodeMirror e salvamento
    layout.ts      # layout no cliente (espelha domain.layout)
    preview.ts     # canvas, atlas, desenho
    render.ts      # funções puras: placements -> comandos de desenho
```
Alternativa: framework SPA — rejeitada por YAGNI (a UI é simples) e alinhada ao
`MIGRATION.md` (sem React por ora).

### 2. Build e entrega dos estáticos
Vite com `base = "/static/dist/"` e `build.outDir = "../app/static/dist"`.
Em produção, o Flask serve `app/static/dist` como estáticos e a rota `/` devolve
o `index.html` construído. Em desenvolvimento, `vite dev` serve o shell e faz
`proxy` de `/api` para o Flask.
Alternativa: fallback de SPA (history API) no Flask — rejeitada; usamos
**roteamento por hash** (`#/`, `#/projects/<id>`), então nenhuma rota do servidor
precisa mudar (mantém `web-shell` satisfeita).

### 3. Layout no cliente (`screen-preview`)
`frontend/src/layout.ts` calcula a disposição espelhando `domain/layout.py`:
parte da tela configurada (`x`, `y`, `new_line`), remove `tags`
(`String.replace` com regex global), respeita a linha-pivô de `matches` a partir
do cursor, avança por `glyph.advance + 1` e sinaliza transbordo em 256/192. Os
avanços/leading vêm do atlas; para codepoint não mapeado usa-se `default_advance`
(exposto nas métricas do atlas).
Motivo: o preview é efêmero e recalcula a cada tecla; buscar no servidor a cada
edição é um round-trip e um payload repetido sem ganho.
Alternativa (servidor, reusando `domain.layout`) — descartada por latência e
tráfego; o endpoint foi removido.

**Divergência**: `domain.layout` continua sendo a referência. Para impedir
divergência, uma **suíte de conformidade** com os mesmos casos
(`frontend/src/layout_cases.json`) roda no pytest e no vitest, cobrindo avanço,
quebra, transbordo, pivô, tags e codepoint não mapeado.

**Limite conhecido**: `tags`/`matches` são regex; `re` (Python) e `RegExp` (JS)
divergem em casos de borda. Para os padrões simples do preview é aceitável;
padrões complexos podem exigir revisão (ver Open Questions).

### 4. Endpoint de ativos (`project-assets`)
`GET /api/projects/<id>/backgrounds/<name>` → bytes da imagem, `Content-Type`
pela extensão (`image/png`). O nome é resolvido pelo manifesto (não é caminho
livre), e a leitura passa pelo `StorageBackend` (isolamento já garantido).
Ativo inexistente → 404.

### 5. Prévia no canvas (`screen-preview`)
`preview.ts` mantém um `<canvas width="256" height="192">`. Fluxo: busca **uma
vez** o atlas (`.../atlas` JSON + `.../atlas.png`); a cada edição calcula o
layout localmente (`layout.ts`) e desenha o background e, para cada glifo, copia
o retângulo do atlas (`drawImage(atlas, sx, sy, sw, sh, x, y, sw, sh)`). O
background é buscado por `/api/projects/<id>/backgrounds/<name>` e cacheado por
URL. Zoom = escala via CSS com `image-rendering: pixelated`. A edição agenda o
redesenho no próximo frame (`requestAnimationFrame`), sem debounce artificial —
a resposta é imediata.
Alternativa: chamar o servidor a cada edição — descartada (ver decisão 3).

### 6. Editor e fluxo (`web-ui`)
CodeMirror 6 (`basicSetup`, modo texto). Fluxos: importar (upload `.zip` via
`multipart`), listar/abrir projeto, carregar a lista de arquivos, abrir o texto
(`GET .../files/<path>`), salvar (`PUT .../files/<path>`), selecionar a tela.
Erros da API (JSON `{error:{code,message}}`) são exibidos na UI.

### 7. Testes
- **Servidor:** pytest para o endpoint de ativos (200, 404 e travessia) e um
  teste de **conformidade** lendo `tests/fixtures/layout_cases.json` e rodando
  `domain.layout`.
- **Frontend:** `npm run build` (type-check + build); `vitest` para as funções
  puras (`layout.ts` com os mesmos casos de conformidade, `render.ts` e `api.ts`).
  O desenho em canvas não é testado em jsdom.

### 8. Docker e higiene
`Dockerfile` ganha `FROM node:22-alpine AS frontend` que roda `npm ci` e
`npm run build`; o runtime copia `--from=frontend /frontend/dist` para
`app/static/dist` **depois** do `COPY . .`. `.dockerignore` e `.gitignore`
passam a ignorar `node_modules/` e `frontend/dist/`.

## Risks / Trade-offs

- [Divergência entre o layout do cliente e o do domínio] → suíte de conformidade
  compartilhada nos testes de Python e TypeScript.
- [Semântica de regex diferente entre Python e JS] → padrões simples no preview;
  documentado e reavaliável (ver Open Questions).
- [Build Node no Docker aumenta tempo/imagem] → estágio separado; `dist` é a
  única saída levada ao runtime.
- [Canvas difícil de testar em CI] → isolar a lógica em `render.ts` puro e testar
  isso; o desenho final é verificação manual.
- [Contrato `/api` mudar] → o front centraliza tudo em `api.ts`.

## Migration Plan

- Aditivo: novo endpoint de ativos e um app estático; `/api` existente
  inalterado.
- Dev: `npm install && npm run dev` com proxy para o Flask.
- Prod: `npm run build` (ou stage Node no `Dockerfile`) → Flask serve `dist`.
- Rollback: remover `frontend/`, o endpoint de ativos e o stage Node; a rota `/`
  volta ao shell Jinja.

## Open Questions

- Como tratar `tags`/`matches` quando exigirem semântica de regex que difere
  entre Python e JS (avaliar mover esses casos ao servidor ou restringir o
  dialeto). Decidível sem afetar specs ou abordagem.
- Roteamento: hash agora; history API só se virar requisito de SEO/deep-link.
