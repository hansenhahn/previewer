## 1. Higiene do repositório (Fase 0)

- [x] 1.1 Criar `.gitignore` cobrindo `*.pyc`, `__pycache__/`, `.venv/`, `.pytest_cache/`, `editor/`, `editor.rar`; verificar com `git status --short` que esses itens deixam de aparecer
- [x] 1.2 Criar `.gitattributes` com `text=auto eol=lf` e marcação de binários; verificar com `git check-attr text eol -- configobj.py tests/fixtures/fonts/fontevent.NFTR`
- [x] 1.3 Remover `*.pyc` do versionamento; verificar que `git ls-files '*.pyc'` não retorna nada

## 2. Aplicação Flask e tela inicial (web-shell)

- [x] 2.1 Criar `app/config.py` com `Settings` e `load_settings(environ)`; verificar teste de carga completa e de variável obrigatória ausente
- [x] 2.2 Criar `app/__init__.py` com `create_app(settings)`; verificar que a app é criada e a rota `/` responde 200
- [x] 2.3 Criar `app/templates/` e `app/static/` da tela inicial; verificar `GET /` retorna HTML referenciando um ativo e `GET` desse ativo retorna 200
- [x] 2.4 Registrar as rotas em `app/routes.py`; verificar smoke via `Flask.test_client()`

## 3. Health check (service-health)

- [x] 3.1 Implementar `GET /healthz` executando `SELECT 1` na sessão; verificar status 200 quando o banco responde
- [x] 3.2 Tratar banco indisponível; verificar status 503 com corpo indicando estado degradado
- [x] 3.3 Garantir acesso anônimo ao `/healthz`; verificar requisição sem credenciais retorna normalmente

## 4. Storage (project-storage)

- [x] 4.1 Definir `StorageBackend` (Protocol) em `infra/storage.py`; verificar teste de contrato com um dublê
- [x] 4.2 Implementar `FilesystemStorage` em `{STORAGE_ROOT}` com criar/listar projeto e ler/escrever/remover arquivo; verificar teste de escrita+leitura
- [x] 4.3 Rejeitar travessia de caminho com `resolve()` + `is_relative_to`; verificar teste que espera erro para caminho com `../`
- [x] 4.4 Isolar por `owner_id`/projeto; verificar que nenhum arquivo fora da raiz é tocado

## 5. Banco e migrações (project-catalog)

- [x] 5.1 Criar `infra/db.py` com engine e fábrica de sessão a partir de `DATABASE_URL`; verificar handshake `SELECT 1`
- [x] 5.2 Modelar `Project` em `infra/models.py` (id UUID, owner_id, name, encoding, timestamps, `UniqueConstraint(owner_id, name)`); verificar colunas e constraint na metadata
- [x] 5.3 Configurar Alembic (`alembic.ini`, `migrations/env.py` lendo `DATABASE_URL`); verificar `alembic upgrade head` cria `projects` em banco vazio
- [x] 5.4 Verificar idempotência das migrações; rodar `alembic upgrade head` novamente e confirmar ausência de erro
- [x] 5.5 Implementar repositório de `Project` (criar/consultar) e testar criação, leitura e nome duplicado por proprietário; verificar com SQLite in-memory
- [x] 5.6 Teste de integração que aplica as migrações contra Postgres real; verificar que roda no compose e é pulado quando `DATABASE_URL` não estiver definida

## 6. Docker

- [x] 6.1 Criar `Dockerfile` multi-stage, usuário não-root e `gunicorn`; verificar `docker build` conclui
- [x] 6.2 Criar `docker-compose.yml` com `app` + `postgres:16` e volumes para `STORAGE_ROOT` e dados do banco; verificar `docker compose up` e `/healthz` retornando 200
- [x] 6.3 Criar `.env.example` documentando `STORAGE_ROOT`, `DATABASE_URL`, `SECRET_KEY` e `FLASK_ENV`; verificar que todas as variáveis obrigatórias constam
- [x] 6.4 Garantir que a migração é aplicada antes de servir; verificar que o container sobe com o schema criado
- [x] 6.5 Confirmar que a imagem não contém artefatos de usuário nem `.venv`; verificar inspeção da imagem

## 7. Verificação final

- [x] 7.1 Rodar a suíte completa (`.venv/bin/python -m pytest`); verificar que todos os testes passam
- [x] 7.2 Confirmar que `domain/` e o app legado não foram alterados por esta change; verificar com `git status` restrito a esses caminhos
- [x] 7.3 Confirmar que novos pacotes não importam GTK/cairo; verificar com `git grep -n "gtk\|cairo" -- app/ infra/`
- [x] 7.4 Validar a change com `openspec validate bootstrap-platform-skeleton --strict`
