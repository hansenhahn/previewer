## 1. Legado

- [x] 1.1 Criar `legacy/` e mover os fontes do app antigo (`editor.py`, `drawer.py`, `nftr.py`, `writer.py`, `dialogs/`, `editor.ui`, `configobj.py`, `setup.py`, `setup2.py`, `Pixmaps/`, `.project`, `.pydevproject`, `.settings/`); verificar que a raiz não contém mais esses itens
- [x] 1.2 Mover os artefatos de build do legado (`editor/`, `editor.rar`, `*.pyc`) para `legacy/`; verificar que continuam ignorados pelo git (`git check-ignore`)

## 2. Mover o backend para `backend/`

- [x] 2.1 Mover `app/` → `backend/web/`; verificar a estrutura resultante
- [x] 2.2 Mover `domain/`, `infra/`, `migrations/`, `tests/`, `wsgi.py`, `alembic.ini`, `requirements.txt`, `pyproject.toml`, `conftest.py`, `entrypoint.sh` para `backend/`; verificar a árvore
- [x] 2.3 Atualizar `wsgi.py` e os testes de `from app...` para `from web...`; verificar com `grep -rn "from app" backend/`

## 3. Ajustar referências

- [x] 3.1 Ajustar `backend/tests/test_layout_conformance.py` para ler `frontend/src/layout_cases.json` a partir da raiz (`parents[2]`); verificar o teste de conformidade
- [x] 3.2 Ajustar `pyproject.toml` (mover para `backend/`, `testpaths = ["tests"]`, `pythonpath = ["."]`) e confirmar a coleta do pytest
- [x] 3.3 Ajustar `vite.config.ts` para emitir em `../backend/web/static/dist`; verificar `npm run build`

## 4. Docker e ignores

- [x] 4.1 Atualizar `.gitignore`/`.dockerignore` (`legacy/`, caminhos do build em `backend/web/static/dist`); verificar `git status`
- [x] 4.2 Atualizar `Dockerfile` (caminhos `backend/`, estágio Node → `backend/web/static/dist`, `WORKDIR /app/backend`, `entrypoint.sh` em `backend/`); verificar `docker build`
- [x] 4.3 Ajustar `docker-compose.yml` se necessário; verificar `docker compose up` e `GET /`/`/healthz`

## 5. Verificação final

- [x] 5.1 Rodar a suíte Python a partir de `backend/` e confirmar que passa
- [x] 5.2 Rodar `npm test` e `npm run build` no frontend e confirmar que passam
- [x] 5.3 Confirmar que não há referências quebradas a `app/` ou `tests/` na raiz; verificar com `grep`
- [x] 5.4 Validar a change com `openspec validate restructure-backend --strict`
