## 1. Listagem de repositórios

- [x] 1.1 Introduzir `Authorization(identity, access_token)` e fazer `exchange` devolvê-lo; adicionar `GitHubOAuthProvider.list_repos(token)` (só públicos); verificar com HTTP mockado
- [x] 1.2 Criar a tabela `user_repositories` e a migração Alembic `0004`, com repositório (refresh/upsert/lista por usuário); verificar com SQLite in-memory
- [x] 1.3 Atualizar o cache no `/auth/callback` com o token e descartá-lo em seguida; verificar com `FakeProvider`
- [x] 1.4 Expor `GET /api/github/repos` (autenticado) retornando o cache; verificar 200 e 401

## 2. Import via clone parcial + esparso

- [x] 2.1 Adicionar `FilesystemStorage.local_path` (seam do working copy) e excluir `.git` de `list_files`; verificar teste
- [x] 2.2 Extrair da ingestão a finalização comum (validação anti-traversal, assets referenciados, criação/rollback); manter a suíte de ingestão verde
- [x] 2.3 Implementar `infra/github_source.py`: clone `--filter=blob:none --sparse --depth=1`, `git show HEAD:manifest.json`, `sparse-checkout` dos caminhos do manifest e checagem de existência; verificar com um repositório git local (protocolo `file`, só em teste)
- [x] 2.4 Implementar `POST /api/projects/github` validando público, manifest, nome duplicado e rollback; verificar testes
- [x] 2.5 Garantir segurança do git (env, timeout, `protocol.file.allow=never` em produção) e limites; verificar por teste de caminho inválido no manifest

## 3. Docker, frontend e verificação

- [x] 3.1 Instalar `git` no estágio `runtime` do Dockerfile; verificar build da imagem
- [x] 3.2 UI "Importar do GitHub…" (modal com a lista, nome/fork/branch e importar) reusando a abertura de projeto; verificar `npm run build`
- [x] 3.3 Importar um repo público de exemplo no Docker ponta a ponta e validar com `openspec validate github-import --strict` (verificação feita no container com repo git local, a seu pedido; o import de repo público real fica como teste manual no navegador)

## 4. Selo de manifest e atualização sob demanda

- [x] 4.1 Migração `0005`: `user_identities.access_token` e, em `user_repositories`, `manifest_ok`/`manifest_error`/`checked_at`; verificar `alembic upgrade head`
- [x] 4.2 `check_manifest(full_name, branch, opener=None)` em `github_source.py` (raw + `parse_manifest`); verificar válido/ausente/inválido com HTTP mockado
- [x] 4.3 Reter o token no login (`upsert_identity(..., access_token=)`) e verificar que não é exposto em `/auth/me`
- [x] 4.4 `refresh_repositories` (list_repos + validação paralela + gravação) e endpoint `POST /api/github/repos/refresh`; erros viram `github_error`, não silêncio
- [x] 4.5 `POST /api/projects/github` recusa repo sem manifest válido (422); `GET /api/github/repos` devolve `manifest_ok`/`manifest_error`
- [x] 4.6 UI: ✅/⚪ por repo (⚪ desabilitado com motivo), botão **Atualizar** e refresh automático quando vazio; `npm run build`
- [x] 4.7 Rodar suítes (Python e frontend) e validar `openspec validate github-import --strict`
