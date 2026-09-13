## Context

Ver `proposal.md` — Why. A Fase 1 entregou `domain/` puro (fontes, layout,
texto) com testes. O `MIGRATION.md` §7–§9 define a Fase 2 e as regras de
Dockerização e segurança. Decisões já tomadas com o usuário: **Postgres +
SQLAlchemy desde já** (paridade dev/prod) e banco guardando **metadados**, com
bytes no storage. O app legado permanece intocado.

## Goals / Non-Goals

**Goals:**
- Aplicação Flask executável, com tela inicial e `/healthz`.
- `StorageBackend` abstrato com implementação em filesystem sob `STORAGE_ROOT`.
- Postgres + SQLAlchemy 2.0 + Alembic, com a tabela `projects`.
- Imagem Docker e compose (app + Postgres), container stateless e não-root.
- Higiene de repo (`.gitignore`, `.gitattributes`).

**Non-Goals:**
- Endpoints de projeto/arquivo, upload, atlas/preview, editor (Fase 3).
- Auth real e isolamento por usuário (Fase 4) — apenas `owner_id` stub.
- S3, Redis, filas, microservices.
- Build de frontend em Node (só na Fase 3, quando houver TS/CodeMirror).
- Reestruturar `domain/` para `src/`.

## Decisions

### 1. Application factory e layout de pacotes
```
app/
  __init__.py      # create_app(settings) -> Flask
  config.py        # Settings (dataclass) + load_settings(environ)
  routes.py        # "/" e "/healthz"
  templates/       # shell HTML
  static/          # css/js placeholder
infra/
  __init__.py
  storage.py       # StorageBackend (Protocol) + FilesystemStorage
  db.py            # engine/session factory + checagem de conectividade
  models.py        # Project (SQLAlchemy 2.0)
migrations/        # Alembic (env.py lê DATABASE_URL)
alembic.ini
```
`create_app(settings)` recebe configuração explícita, o que torna os testes
determinísticos e evita estado global. Alternativa: módulo único com app global —
rejeitada por dificultar testes e composição.

### 2. Configuração tipada e fail-fast
`load_settings(environ)` monta um dataclass `Settings` (`storage_root`,
`database_url`, `secret_key`, `flask_env`) e valida presença/formatos,
levantando erro explícito na ausência de obrigatórias. `SECRET_KEY` não tem
padrão. Alternativa: `os.environ.get` espalhado — rejeitada por esconder erros.

### 3. Storage: contrato + filesystem seguro
`StorageBackend` (Protocol) com `create_project`, `list_projects`, `write_file`,
`read_file`, `delete_file`. `FilesystemStorage(root)` organiza em
`{root}/{owner_id}/{project_id}/...` e valida cada caminho resolvido com
`Path.resolve()` + `is_relative_to(root)`, rejeitando travessia. Alternativa:
guardar blobs no Postgres — rejeitada; banco é metadado.

### 4. Banco: SQLAlchemy 2.0 + Alembic, `projects` como primeira tabela
`Project`: `id` (UUID, pk), `owner_id` (str, indexado), `name` (str),
`encoding` (str), `created_at`, `updated_at`, `UniqueConstraint(owner_id, name)`.
Sem tabela `users` ainda; `owner_id` é string com um proprietário `local` por
padrão. Driver `psycopg` v3. `DATABASE_URL` também alimenta o Alembic, evitando
duas fontes de verdade. Alternativa: criar o schema inteiro (assets, text_files)
agora — rejeitada por YAGNI; essas tabelas entram na Fase 3 junto dos endpoints.

### 5. Health check com dependência
`/healthz` executa `SELECT 1` na sessão; responde 200 `{"status":"ok"}` ou 503
`{"status":"degraded"}`. É o que prova a dependência de banco sem criar API de
domínio ainda. Alternativa: health raso (sem banco) — rejeitada; não detectaria
o problema mais provável (banco fora).

### 6. Docker: multi-stage, não-root, stateless
Stage de build instala dependências em wheel cache; runtime `python:3.13-slim`
(não 3.14, por maturidade de imagens/ecossistema) com usuário não-root e
`gunicorn`. `compose` sobe `app` + `postgres:16`, com volume nomeado para
`STORAGE_ROOT` e outro para o Postgres. Imagem **sem** Node por ora. Nenhum dado
de usuário na imagem.

### 7. Testes: rápidos por padrão, migração contra Postgres
Smoke de web (`/`, `/healthz` com banco dublê) e storage rodam sem banco.
Repositório testa contra **SQLite in-memory** (modelo portável) para velocidade.
A validação de migração roda contra **Postgres real** via compose, marcada como
integração (pulada se `DATABASE_URL` ausente). Alternativa: testcontainers —
rejeitada por dependência extra agora.

### 8. Higiene de repositório (Fase 0)
`.gitignore` para `*.pyc`, `__pycache__/`, `.venv/`, `editor/`, `editor.rar`,
`.pytest_cache/`. `.gitattributes` normaliza `text=auto eol=lf` e marca binários,
eliminando o ruído de CRLF que hoje polui `configobj.py` e `dialogs/`.

## Risks / Trade-offs

- [Postgres no caminho crítico de dev] → compose com volume e healthcheck;
  app falha explícito, não silencioso.
- [Migração divergir do modelo] → um único `DATABASE_URL`; teste de integração
  aplica migrações do zero e valida a tabela.
- [Travessia de caminho no storage] → `resolve()` + `is_relative_to`, com teste
  de cenário malicioso.
- [Docker em ambiente com snap] → documentar uso; o compose é a fonte de verdade.
- [Escopo virar Fase 3] → proposta e tasks limitam a `projects` + shell + health.

## Migration Plan

- Aditivo: `domain/` e o app legado não mudam.
- Rodar: `docker compose up`, depois `alembic upgrade head`.
- Rollback: remover `app/`, `infra/`, `migrations/`, `alembic.ini`, `Dockerfile`,
  `docker-compose.yml`, `.env.example` e os itens de higiene.

## Open Questions

- Autenticação de serviço (Fase 4) pode exigir reavaliar `owner_id` como FK de
  `users`; decidível depois sem mudar specs ou abordagem.
