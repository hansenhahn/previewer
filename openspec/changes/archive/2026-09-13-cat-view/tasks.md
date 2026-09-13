## 1. Manifesto: segmentação (project-manifest)

- [x] 1.1 Adicionar `Segments` e o campo opcional `segments` em `backend/domain/project.py` com validação (`start`/`end` listas de strings); verificar testes de manifesto válido, ausente e inválido
- [x] 1.2 Atualizar `to_dict`/serialização para incluir `segments`; verificar `GET /api/projects/<id>`

## 2. Segmentação no domínio (text-segmentation)

- [x] 2.1 Criar `backend/domain/segmentation.py` com `Segment`, `Part`, `segment` e `reconstruct` (início/fim, separadores preservados)
- [x] 2.2 Testes de round-trip e casos (bloco simples, vários, sem fim, sem config); verificar `.venv/bin/python -m pytest -k segment`
- [x] 2.3 Criar `frontend/src/segmentation_cases.json` e um teste de conformidade Python sobre os casos

## 3. Segmentação no cliente (text-segmentation)

- [x] 3.1 Implementar `frontend/src/segmentation.ts` espelhando o domínio (segment/align/reconstruct); verificar `npm run build`
- [x] 3.2 Teste vitest de conformidade sobre `segmentation_cases.json` (posições e reconstrução); verificar `npm test`

## 4. Visão CAT (cat-view)

- [x] 4.1 Criar `frontend/src/shell/cat.ts` (caixas com original read-only e traduzido editável, status, não pareados); verificar `npm run build`
- [x] 4.2 Adicionar alternância Editor | Segmentos na barra do texto e integrar no `main.ts`; verificar build
- [x] 4.3 Navegação próximo/anterior e aviso de não pareados; verificar smoke
- [x] 4.4 Mensagem quando o projeto não declara `segments`; verificar smoke

## 5. Edição, salvamento e prévia

- [x] 5.1 Ao editar um segmento, remontar `content` e atualizar o documento/editor plano; verificar smoke
- [x] 5.2 Salvar pelo `PUT` existente usando `content` remontado; verificar round-trip (salvar e reler)
- [x] 5.3 Garantir que a prévia usa o `content` remontado (edições não salvas refletem); verificar smoke

## 6. Verificação final

- [x] 6.1 Rodar a suíte Python (de `backend/`) e confirmar que passa
- [x] 6.2 Rodar `npm test` e `npm run build`; confirmar que passam
- [x] 6.3 Verificar Docker end-to-end (build/compose) e o fluxo CAT
- [x] 6.4 Confirmar isolamento da biblioteca (`grep`) e validar com `openspec validate cat-view --strict`

## 7. Refinamento (abstração e visão inicial)

- [x] 7.1 Separar delimitadores do corpo no domínio e no cliente (`prefix`/`body`/`suffix`), com fixture e testes atualizados
- [x] 7.2 Exibir/editar apenas o corpo nas caixas, preservando os delimitadores na reconstrução
- [x] 7.3 Abrir na visão por segmentos quando o projeto declara `segments`
- [x] 7.4 Ajustar a config do playton-2 (`start` = `^\[.+\]$`, `end` = `^!\D{30}!$`) e reimportar; verificar na API
- [x] 7.5 Caixa traduzida cresce automaticamente com o conteúdo (`autoGrow`), sem precisar redimensionar; verificar build
- [x] 7.6 Skin dos cards (cabeçalho com nº/status, rodapé com contagem, destaque do ativo); verificar build
- [x] 7.7 Selecionar um card dispara a prévia a partir daquele segmento (`onSelect` → `render(cursorLine)`); verificar build
- [x] 7.8 Fonte do preview em preto via tint do atlas (`TEXT_COLOR`); verificar build
- [x] 7.9 Preview para na próxima linha de quebra (`matches`), como o previewer original (domínio + cliente + caso de conformidade)
- [x] 7.10 Separar visualmente original e traduzido (original em bloco próprio; tradução em caixa própria)
- [x] 7.11 Renderizar o painel de arquivos como árvore real (pastas expansíveis, ícones, arquivo ativo) a partir dos caminhos; verificar build e teste de `buildTree`
- [x] 7.12 Remover o prefixo da pasta de origem na exibição da árvore; verificar build
- [x] 7.13 Árvore clássica: linhas da árvore como elementos não-button com reset (sem estilo herdado do `native.css`) e `Cache-Control: no-store` no shell (evita cache do index)
- [x] 7.14 Remover borda/fundo/raio que o `native.css` aplica em `<details>` (e o chevron `::after`); verificar CSS servido
- [x] 7.15 Forçar `justify-content: flex-start` nas linhas da árvore (o `details summary` do `native.css` alinhava o nome à direita)
- [x] 7.16 Barra de comando única (Mock C): projeto como dropdown (encoding só no menu), visão segmentada, Salvar/Original + ponto "não salvo", navegação por ícones, tema por ícone, e Tela/Zoom no cabeçalho da prévia; verificar build/Docker
- [x] 7.17 Mover a árvore de arquivos para dentro da área das abas (alinhada à janela selecionada) e remover o rail/painel de projetos (troca de projeto no dropdown; "Importar .zip" no menu)
- [x] 7.18 Prévia: coluna com largura fixa, rótulos pequenos e uniformes, zoom padrão 1 e "Tela" no cabeçalho da prévia
- [x] 7.19 Reescrever `layout.css` para a nova estrutura (sem rail/painel; árvore dentro da aba; prévia como coluna); verificar build/Docker
- [x] 7.20 Trocar o `wa-select` de tela por um botão "Tela" que abre uma bolha com **mini-preview** (background) + nome de cada tela; verificar build/Docker
- [x] 7.21 Botão "Tela" sem widget de seleção separado; itens da bolha com texto alinhado ao meio, mais espaçamento e check na tela ativa
- [x] 7.22 Modal de seleção de tela (master-detail, Mock B): botão "Tela" abre modal centrada com preview grande (4:3, sem distorção) + lista com miniaturas; Cancelar/Aplicar, Esc e clique no fundo fecham
- [x] 7.23 Ajustes da modal: itens da lista alinhados à esquerda (`justify-content`), preview em resolução nativa (256×192) e botão "Tela" sem seta de dropdown (ícone + rótulo)
- [x] 7.24 Mover a coluna de prévia para dentro da área da aba (junto da árvore e dos painéis), removendo o wrapper `.workspace-main`/`.preview-column`
- [x] 7.25 Prévia adaptável: coluna flexível (`flex: 1 1 340px`, `max-width: 50%`) e canvas preenchendo o painel (`object-fit: contain`, 4:3); slider de zoom removido
- [x] 7.26 Zoom reintroduzido sobre a prévia adaptável: `preview-stage` dimensionado por `zoom × 100%` (1 = encaixa, >1 = amplia com scroll)
- [x] 7.27 Zoom 1× em resolução nativa: `preview-stage` dimensionado em pixels (`SCREEN_WIDTH × zoom`, `SCREEN_HEIGHT × zoom`), centralizado com `margin: auto`
- [x] 7.28 Prévia com largura pelo conteúdo: `.preview-wrap` usa `flex: 0 1 auto` (não reserva espaço), crescendo apenas conforme a imagem/zoom
- [x] 7.29 Corrigir especificidade: `.pane.preview-wrap` (o `.pane { flex: 1 }` posterior sobrescrevia via mesma especificidade)
- [x] 7.30 Fixar a largura da árvore (`#docs-sidebar { flex: 0 0 240px }`) para o CodeMirror não encolhê-la a zero no modo Editor
- [x] 7.31 Manter a prévia visível no modo Editor: `.pane.preview-wrap { flex: 0 0 auto }` e editores encolhem/rolam (`min-width: 0` em `.panes`/`.editor-host`/`.cm-editor`)
