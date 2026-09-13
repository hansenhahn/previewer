## Context

Ver `proposal.md` — Why. Hoje: `app/` (Flask), `domain/`, `infra/`,
`migrations/`, `tests/`, `wsgi.py`, `alembic.ini`, `requirements.txt`,
`pyproject.toml`, `conftest.py`, `entrypoint.sh` na raiz, junto do legado
(`editor.py`, `drawer.py`, `nftr.py`, `writer.py`, `dialogs/`, `editor.ui`,
`configobj.py`, `setup*.py`, `Pixmaps/`) e do `frontend/`. As specs já estão em
`openspec/specs/` (15) e o comportamento não muda.

## Goals / Non-Goals

**Goals:**
- Backend contido em `backend/`; legado em `legacy/`; raiz com o monorepo.
- Renomear `app/` → `web/`.
- Build, testes e Docker continuando funcionando.

**Non-Goals:**
- Mudar comportamento/API/specs.
- `src/`-layout instalável; migrar o legado.

## Decisions

### 1. Layout alvo
```
backend/
  web/            (ex-app/)
  domain/
  infra/
  migrations/
  tests/
  alembic.ini
  wsgi.py
  requirements.txt
  pyproject.toml
  conftest.py
  entrypoint.sh
legacy/           (ex-raiz: editor.py, ... , Pixmaps/, editor/, editor.rar)
frontend/
Dockerfile        (raiz; contexto do monorepo)
docker-compose.yml
```
`backend/` entra no `sys.path` (via `WORKDIR`/`prepend_sys_path`/`conftest`), então
os imports `from domain...`, `from infra...` e `from web...` continuam válidos.

### 2. `app/` → `web/`
Alinha com a camada `web/` do `MIGRATION.md`. Imports afetados: `wsgi.py` e os
testes (`from app import create_app` → `from web import create_app`;
`from app.config import Settings` → `from web.config import Settings`). Dentro do
pacote, os imports são relativos e não mudam.

### 3. Legado em `legacy/`
Move os fontes e artefatos do app Py2/GTK para `legacy/`, deixando a raiz limpa.
Nada é alterado dentro do legado. `legacy/` entra no `.dockerignore` (não vai
para a imagem).

### 4. Saída do build do frontend
`vite.config.ts` passa a emitir em `../backend/web/static/dist` (Flask serve pelo
`static` do pacote `web/`). `base` continua `/static/dist/`.

### 5. Docker
- Estágio `frontend` builda `frontend/` e copia `backend/web/static/dist`.
- Runtime: `WORKDIR /app/backend`, `entrypoint.sh` (em `backend/`) roda
  `alembic upgrade head` e o `gunicorn wsgi:app`.
- `COPY backend/requirements.txt` no builder.

## Risks / Trade-offs

- [Referências a caminhos esquecidas] → `grep` por `app/` e `tests/`; rodar
  pytest, `npm run build` e o compose.
- [Teste de conformidade lendo o frontend] → ajustar o caminho relativo para a
  raiz do repo (`parents[2]`).
- [Imagem ficar maior com o legado] → `legacy/` no `.dockerignore`.

## Migration Plan

- Mover com `git mv`/`mv` preservando histórico; ajustar referências.
- Verificar: `backend/.venv`? Não — o venv continua em `.venv` na raiz; rodar
  `../.venv/bin/python -m pytest` de dentro de `backend/`, ou a partir da raiz
  com `--rootdir`.
- Rollback: reverter os movimentos (commit dedicado).

## Open Questions

- Adotar `backend/src/previewer/` instalável — decidível depois, sem afetar este
  refactor.
