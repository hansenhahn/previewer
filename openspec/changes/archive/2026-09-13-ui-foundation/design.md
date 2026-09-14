## Context

Ver `proposal.md` — Why. O frontend é Vite + TypeScript sem framework; hoje
`frontend/src/style.css` é CSS solto, `index.html` tem markup estático e
`main.ts`/`ui.ts` criam elementos crus. Já temos os fluxos (importar/abrir,
editar/salvar, preview). Decisão do usuário: adotar **Web Awesome**, mas com
**integração generalizada** para permitir fallback (ex.: Bootstrap) sem dor.

## Goals / Non-Goals

**Goals:**
- Tokens de design próprios com tema claro/escuro.
- Adaptador de UI que isola a biblioteca; app só fala com o adaptador.
- Trocar de biblioteca = novo arquivo de adaptador + mapeamento de tema.
- Manter comportamento e a suíte atual.

**Non-Goals:**
- Implementar o adaptador Bootstrap agora.
- Componentes Pro, novas features de UX, mudar editores/canvas.

## Decisions

### 1. Tokens próprios, tema por CSS variables
`frontend/src/ui/tokens.css` define `--pv-color-*`, `--pv-space-*`,
`--pv-radius-*`, `--pv-font-*`, `--pv-shadow-*` para `:root` e
`[data-theme="dark"]` (com `prefers-color-scheme`). A UI usa **só** `--pv-*`; nada
de variáveis da biblioteca no app.

### 2. Mapeamento biblioteca → tokens (um arquivo por lib)
`frontend/src/ui/theme-webawesome.css` liga os tokens da lib aos nossos
(`--wa-color-* → --pv-*`, `--wa-font-*`, `--wa-border-radius-*`, etc.). Um futuro
`theme-bootstrap.css` faria o mesmo com as variáveis do Bootstrap. Trocar de lib
= trocar esse arquivo.

### 3. Adaptador `UiKit` (única coisa que conhece a lib)
`frontend/src/ui/kit.ts` define a interface com os primitivos que usamos:
```ts
export interface UiKit {
  button(o: ButtonOptions): HTMLElement;
  select(o: SelectOptions): HTMLElement;
  toast(o: ToastOptions): void;
  callout(message: string, variant?: CalloutVariant): HTMLElement;
}
```
- `kit-webawesome.ts` implementa criando elementos (`wa-button`, `wa-select`,
  `wa-callout`, toasts) com classes nossas (`pv-*`) e handlers.
- `ui/index.ts` exporta a implementação ativa (ponto único de troca).
- **Regra:** `<wa-*>`/classes da lib só aparecem em `kit-*.ts` e no
  `theme-*.css`. Um teste de `grep` garante isso.

### 4. Estrutura e layout agnósticos
`index.html` mantém apenas o esqueleto semântico (containers com `id`) + classes
`pv-*`; o layout (flex/grid) é nosso, em `frontend/src/ui/layout.css`. Controles
dinâmicos (botões/select/lista) são criados pelo adaptador em `main.ts`/`ui.ts`.

### 5. Carregamento sob demanda
Importar apenas os componentes Web Awesome usados (ex.: `button`, `select`,
`callout`, `toast`) em `kit-webawesome.ts`, evitando puxar a lib inteira.
Confirmar a **versão estável** no momento da instalação e **fixar** no
`package.json`.

## Risks / Trade-offs

- [Web Awesome ainda em beta] → versão fixada e adaptador fino; fallback trivial
  para outra lib.
- [Vazamento da lib para o app] → regra de `<wa-*>` só no adaptador + teste de
  `grep` no CI/local.
- [Bundle maior] → importar só os componentes usados.
- [Tema inconsistente] → tokens próprios como contrato; o mapping da lib só
  reescreve `--wa-*`.

## Migration Plan

- Introduzir tokens+adaptador e migrar a UI em passos pequenos; comportamento
  inalterado; testes e build a cada passo.
- Rollback: voltar `index.html`/`main.ts`/`ui.ts` e remover `frontend/src/ui/`.

## Open Questions

- Qual biblioteca de fallback (Bootstrap) e quando — decidível depois, sem mudar
  a abordagem.
