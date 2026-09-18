## 1. Credencial

- [x] 1.1 Trocar o escopo OAuth para incluir repositórios privados (`read:user user:email repo`) e atualizar o teste de escopo; verificar com `cd backend && ../.venv/bin/python -m pytest tests/test_github.py -q`

## 2. Listagem

- [x] 2.1 `list_repos` passa a incluir repositórios privados (remover o filtro); verificar com `cd backend && ../.venv/bin/python -m pytest tests/test_github.py -q`
- [x] 2.2 Persistir a marca `private` em `user_repositories` (migração `0008`) e expor na API (`_repository_dict`); verificar com `cd backend && ../.venv/bin/python -m pytest tests/test_migrations.py tests/test_github_import.py -q`
- [x] 2.3 Expor `private` no tipo do client (`GithubRepo`) e marcar repositórios privados com **ícone de cadeado** na lista de import; verificar com `cd frontend && npx tsc --noEmit && npm test`

## 3. Manifest autenticado

- [x] 3.1 `check_manifest` verifica via API de contents com o token (funciona para privados), mantendo fallback público sem token; verificar com `cd backend && ../.venv/bin/python -m pytest tests/test_github_source.py -q`

## 4. Clone/import autenticado

- [x] 4.1 `GitHubSource.fetch`/`import_repository` recebem o token e clonam autenticado (sanitizando erros); rota de import repassa o token; verificar com `cd backend && ../.venv/bin/python -m pytest tests/test_github_source.py tests/test_github_import.py -q`

## 5. Verificação final

- [x] 5.1 Rodar `cd backend && ../.venv/bin/python -m pytest -q`; `cd frontend && npm test && npm run build`; e `openspec validate private-repositories --strict`
