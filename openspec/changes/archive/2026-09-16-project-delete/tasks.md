## 1. Modelo

- [x] 1.1 `ChangeRepository.delete_for_project(project_id)` (apaga as alterações do projeto) + teste em `backend/tests/test_changes.py`; verificar com `cd backend && ../.venv/bin/python -m pytest tests/test_changes.py -q`

## 2. API

- [x] 2.1 Rota `DELETE /api/projects/<id>` (dono): apaga `changes` → registro → working copy; responde 204; 404 para inexistente/não-dono. Testes em `backend/tests/test_project_delete.py` (com e sem alterações, isolamento por dono, inexistente); verificar com `cd backend && ../.venv/bin/python -m pytest tests/test_project_delete.py -q`

## 3. UI

- [x] 3.1 `deleteProject` no client (`frontend/src/api.ts`) + teste de URL em `frontend/src/api.test.ts`; verificar com `cd frontend && npm test`
- [x] 3.2 Ação **Remover projeto** (lixeira por projeto no seletor) com modal de confirmação que exige **digitar `confirmar`** para habilitar o botão; ao remover o projeto aberto, voltar ao estado "sem projeto"; verificar com `cd frontend && npx tsc --noEmit && npm test`

## 4. Verificação final

- [x] 4.1 Rodar `cd backend && ../.venv/bin/python -m pytest -q`; `cd frontend && npm test && npm run build`; e `openspec validate project-delete --strict`
