## Why

O backend ficou espalhado na raiz (`app/`, `domain/`, `infra/`, `migrations/`,
`tests/`, `wsgi.py`, `alembic.ini`), misturado com o app legado, enquanto o
frontend já vive em `frontend/`. Isso dificulta o build/CI e não deixa claro o
que é backend, frontend e legado. É um **refactor puro**: sem mudança de
comportamento ou de spec.

## What Changes

- Mover os pacotes do backend para `backend/`: `app/` → `backend/web/`,
  `domain/`, `infra/`, `migrations/`, `tests/`, `wsgi.py`, `alembic.ini`,
  `requirements.txt`, `pyproject.toml`, `conftest.py`, `entrypoint.sh`.
- Renomear `app/` para `web/` (alinhando com a camada `web/` do `MIGRATION.md`).
- Mover o app legado para `legacy/` (`editor.py`, `drawer.py`, `nftr.py`,
  `writer.py`, `dialogs/`, `editor.ui`, `configobj.py`, `setup.py`, `setup2.py`,
  `Pixmaps/`, artefatos de build e arquivos de projeto do Eclipse).
- Ajustar referências: `wsgi.py`/testes (`from web...`), `vite.config.ts`
  (saída do build para `backend/web/static/dist`), `Dockerfile` (caminhos e
  estágios), `.dockerignore`/`.gitignore` (`legacy/`).
- Manter `Dockerfile`, `docker-compose.yml`, `.env.example`, `README.md`,
  `MIGRATION.md`, `docs/` e `openspec/` na raiz.

## Capabilities

### New Capabilities
- Nenhuma. Refactor estrutural: `skip_specs: true`, sem delta de comportamento.

### Modified Capabilities
- Nenhuma.

## Impact

- **Movidos:** código do backend para `backend/`; legado para `legacy/`.
- **Ajustados:** `backend/wsgi.py`, `backend/tests/*`, `frontend/vite.config.ts`,
  `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.gitignore`.
- **Sem alteração:** comportamento, endpoints, specs e frontend (além do caminho
  de saída do build).
- Referência: `MIGRATION.md` §3 (arquitetura) e §8 (Dockerização).

## Não-objetivos

- Qualquer mudança de comportamento, contrato de API ou requisito.
- Migrar o legado para Python 3/GTK3 (permanece intocado em `legacy/`).
- Adotar `src/`-layout instalável (`backend/src/previewer/`) — fica para depois.
