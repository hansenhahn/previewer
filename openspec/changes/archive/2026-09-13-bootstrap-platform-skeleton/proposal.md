## Why

A Fase 1 entregou o domínio puro (`domain/`), mas ele ainda não tem como ser
executado como serviço. Esta é a **Fase 2 do MIGRATION.md** ("Esqueleto web +
Docker"): provar a arquitetura de ponta a ponta — Flask, Docker, storage
abstraído e banco com migrações — antes de construir o núcleo funcional. É o
passo que troca o destino "app de desktop" por "web app dockerizável e
hostável", validando os *seams* (storage, config, persistência) com o mínimo de
superfície.

## What Changes

- Criar o pacote `app/` com uma aplicação **Flask** executável e uma tela inicial
  mínima (shell HTML), servindo também os estáticos do próprio app.
- Expor `GET /healthz` que verifica a conectividade com o banco.
- Introduzir o contrato `StorageBackend` e a implementação em **filesystem**
  enraizada em `STORAGE_ROOT`, com operações de projeto/arquivo e proteção contra
  travessia de caminho.
- Configuração 12-factor por variáveis de ambiente (`STORAGE_ROOT`,
  `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV`), com falha explícita em valor
  ausente/inválido.
- Introduzir **Postgres + SQLAlchemy 2.0** com **Alembic** e a primeira tabela
  (`projects`, com `owner_id` desde já) — infraestrutura de persistência provada
  por migração + repositório.
- Dockerizar: `Dockerfile` multi-stage + `docker-compose.yml` (app + Postgres),
  container stateless, não-root, com volume para `STORAGE_ROOT`.
- **Fase 0 (higiene)** incorporada: `.gitignore` (`.pyc`, `editor/`,
  `editor.rar`, `.venv/`) e `.gitattributes` para normalizar CR/LF.
- **BREAKING**: nada no app legado; a mudança é aditiva. `domain/` é consumido,
  não alterado.

## Capabilities

### New Capabilities
- `web-shell`: servir a tela inicial e os estáticos do app como ponto de entrada
  do serviço web.
- `service-health`: endpoint de saúde que reporta o estado do serviço e da
  dependência de banco.
- `service-config`: carregar e validar a configuração do serviço a partir de
  variáveis de ambiente.
- `project-storage`: contrato de armazenamento de projetos/arquivos e a
  implementação em filesystem sob `STORAGE_ROOT`.
- `project-catalog`: persistir metadados de projeto em Postgres, com migrações
  aplicáveis do zero.

### Modified Capabilities
- Nenhuma. `openspec/specs/` ainda está vazio (a change `extract-pure-domain`
  não foi arquivada), então não há requisitos existentes a alterar.

## Impact

- **Novo:** `app/` (Flask), `infra/` (storage + banco), `migrations/` (Alembic),
  `Dockerfile`, `docker-compose.yml`, `.env.example`, `.gitignore`,
  `.gitattributes`, testes de smoke.
- **Não alterado:** `domain/` (apenas consumido) e todo o app legado
  (`editor.py`, `drawer.py`, `nftr.py`, `writer.py`, `dialogs/`, `editor.ui`,
  scripts de build).
- **Dependências novas:** Flask, SQLAlchemy 2.0, Alembic, driver `psycopg` v3;
  `pytest` já existe.
- **Infra:** container Postgres no compose; volume para `STORAGE_ROOT`.
- **Não-objetivos:** ver seção própria abaixo.
- Referência: `MIGRATION.md` §7 (Fase 2), §8 (Dockerização) e §9 (Segurança).

## Não-objetivos

- Endpoints de projeto/arquivo (upload, listar, ler/salvar) — Fase 3.
- Renderização de fonte/atlas e preview no canvas — Fase 3.
- Autenticação e isolamento real por usuário — Fase 4 (aqui só o `owner_id` stub).
- S3 ou storage remoto; a implementação é filesystem.
- Filas de background, cache, Redis, microservices/k8s.
- Trocar `domain/` para layout `src/`; a estrutura atual permanece.
