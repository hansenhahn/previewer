## 1. Modelo e seams

- [x] 1.1 Tabela `changes` + migração (draft/open/changes_requested/merged/closed); verificar Alembic e repositório
- [x] 1.2 Definir o contrato `ProjectExport` (`ensure_fork`, `ensure_branch`, `commit`, `publish`, `sync`, `pr_status`); verificar com fake
- [x] 1.3 Persistir `upstream` (`owner/repo`) e `base_branch` no projeto (modelo + migração + import pelo `parent` do fork); verificar

## 2. Git no working copy

- [x] 2.1 Criar a branch efêmera no 1º edit (`git switch -c previewer/sketch` da base); verificar
- [x] 2.2 Commit por autosave (um commit por edição, sem `--amend`); verificar histórico local
- [x] 2.3 `restore` (descartar), `switch` (retomar com guarda de pendências) e `branch -D` (abandonar); verificar
- [x] 2.4 Backup do rascunho no fork em branch separada (`previewer-backup/sketch`) no Salvar; verificar
- [x] 2.5 `checkout_base` (Novo rascunho) sem publicar/descartar; verificar

## 3. GitHub (fork, PR, sync)

- [x] 3.1 `ensure_fork` (reusar/validar + `merge-upstream`) usando o `upstream` persistido; verificar com fake/mock
- [x] 3.2 `publish`: renomear a efêmera para `previewer/<slug-do-título>`, squash do delta em 1 commit, push no fork, abrir/reusar PR (`fork:branch → upstream:base`) e remover o backup; verificar
- [x] 3.3 `pr_status` (aberto/mudanças solicitadas/merged) via API; verificar
- [x] 3.4 Check do upstream antes de publicar (+ `update-branch`/merge); verificar

## 4. API e credencial

- [x] 4.1 Rotas de alterações (`list`, `create/subir`, `retomar`, `nova`, `backup`, `descartar`, `abandonar`, `status`); verificar
- [x] 4.2 Escopo OAuth de escrita (`public_repo`) no login; verificar re-consentimento e que o token não é exposto
- [x] 4.3 Retomar: registrar PRs abertos do head (`state=open`) e carregar a branch do remoto ao retomar; verificar

## 5. UI

- [x] 5.1 Autosave (~1 min) com indicador discreto (tick efêmero/ícone de erro) e botão Salvar (com backup no fork); verificar desktop e mobile
- [x] 5.2 Chip de estado + menu fixo (Subir/Novo rascunho/Retomar/Descartar com habilitar/desabilitar); verificar
- [x] 5.3 Telas auxiliares: nomear ao subir, retomar (selecionar), confirmar descartar/abandonar; verificar
- [x] 5.4 Rodar `npm test`/`npm run build` e a suíte Python; validar `openspec validate project-export --strict`
