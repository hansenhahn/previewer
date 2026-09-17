## Why

Hoje não há como **remover um projeto importado**. Depois de importar, o registro no banco
e o **working copy** (clone esparso) ficam ocupando espaço e presos ao projeto, sem forma de
descartá-los — o que impede reimportar/atualizar mais tarde. É o item **R5 (Excluir
projeto)** do [`docs/roadmap.md`](../../../docs/roadmap.md).

## What Changes

- Nova rota **`DELETE /api/projects/<id>`** (somente o dono), que:
  - remove as **alterações** (`changes`) do projeto (necessário antes, por causa da FK);
  - remove o **registro** do projeto;
  - remove o **working copy** do storage.
- A remoção é **local**: **não** toca no GitHub (fork, PRs e branches remotas permanecem).
- Na interface, uma ação **Remover projeto** (com confirmação), disponível no seletor de
  projetos; ao remover o projeto aberto, a tela volta ao estado "sem projeto".
- Novo método no client (`deleteProject`) e no repositório de alterações
  (`delete_for_project`).

## Capabilities

### New Capabilities
(nenhuma)

### Modified Capabilities
- `project-catalog`: novo requisito para **remover um projeto** (registro + working copy +
  alterações), restrito ao proprietário.
- `web-ui`: ação de **remover projeto** na interface, com confirmação.

## Impact

- **Backend:** `backend/web/api.py` (rota de remoção), `backend/infra/repository.py`
  (`ChangeRepository.delete_for_project`), reuso de `ProjectRepository.delete` e
  `StorageBackend.delete_project`.
- **Frontend:** `frontend/src/api.ts` (`deleteProject`), `frontend/src/shell/` /
  `frontend/src/main.ts` (seletor de projetos) e CSS do item de remoção.
- **Testes:** rota (`backend/tests/test_api.py` ou novo `test_project_delete.py`) cobrindo
  remoção com e sem alterações, isolamento por dono e 404.
- **Não alterado:** import, colaboração (o GitHub não é afetado) e domínio.

## Não-objetivos

- Remover **fork/PR/branches remotas** no GitHub (a remoção é só local).
- **Soft-delete**, lixeira ou desfazer (por ora).
- Remover projetos de **outros usuários** ou expor a ação a administradores.
- Excluir **conta/usuário** ou limpar dados órfãos além do projeto escolhido.
