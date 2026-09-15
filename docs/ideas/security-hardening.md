# Segurança e limites (hardening) — previewer

> Status: **plano registrado**. O deploy atual é **local** (dev, praticamente
> single-tenant). Parte das medidas só passa a valer ao **hospedar** para múltiplos
> usuários. Documento para avaliação futura; nada aqui está implementado além do
> "Baseline" abaixo.

## Contexto

Depois de identidade (GitHub) e import de repositórios, a superfície de ataque
mudou: passamos a ler **conteúdo de terceiros** (repos públicos) e a executar
**configuração não confiável** (o `manifest.json`) — inclusive **regex** — no
servidor e no navegador.

Objetivos deste documento:
1. Proteger de **schema quebrado** (manifest inválido/malicioso).
2. Proteger de **repos gigantes** / esgotamento de recursos (disco/CPU).
3. Listar o que já existe e o que falta, separando "agora (local)" de "ao hospedar".

## Modelo de ameaça

| # | Ameaça | Onde | Impacto |
|---|---|---|---|
| 1 | Manifest com schema quebrado/inválido | `domain/project.py` (parse) | Import inconsistente |
| 2 | **ReDoS** por `Tags`/`Matches` (regex do manifest) | cliente (`layout.ts`, `segmentation.ts`) | Aba do usuário **congela** |
| 3 | Repo gigante / muitos arquivos | `infra/github_source.py` | Disco/CPU/tempo |
| 4 | Upload .zip sem teto / zip bomb | `web/api.py` (`upload.read()`) | Memória/disco |
| 5 | Path traversal / zip-slip | `infra/storage.py`, `infra/ingestion.py` | Escrita fora do projeto |
| 6 | Token OAuth em texto puro | `user_identities.access_token` | Vazamento de credencial |
| 7 | Abuso de import/refresh (sem rate limit) | `web/api.py` | Custo/rate limit do GitHub |
| 8 | Sessão/allowlist | `web/auth.py` | Acesso indevido |

## Baseline já implementado

- **Schema**: `parse_manifest` valida formato, versão e campos obrigatórios, com erro
  explícito (`ManifestError`) — cobre a ameaça #1.
- **Paths**: `is_unsafe_path` (zip-slip) e `PathTraversalError` (storage) — #5.
- **Import**: só repositórios públicos; `git` com `GIT_TERMINAL_PROMPT=0` e
  `protocol.file.allow=never`; clone `--depth=1 --filter=blob:none --sparse`
  limitado aos caminhos do manifest; **timeout de 180s** — mitiga parte de #3.
- **Acesso**: `/api` exige sessão (401); `/healthz` isento; onboarding por allowlist.
- **Segredos**: `.env` fora do git; o token **não** é exposto por `/auth/me` — mas
  ainda é guardado em texto puro (#6).

## Limites propostos (MVP hospedado)

- **Por projeto armazenado: ~15 MB** (soma dos arquivos materializados: textos,
  fontes e fundos). Ao exceder, **recusar o import** com erro claro.
- **Por usuário: ~2–3 projetos** (quota de disco). Contabilizar o total do usuário
  antes de aceitar novo import/upload.
- **Upload .zip**: teto de requisição (`MAX_CONTENT_LENGTH`, ex.: 15 MB) **e**
  teto do conteúdo descompactado (proteção contra *zip bomb*).
- **Import**: teto de arquivos e de bytes do clone esparso; abortar e limpar se
  exceder (hoje só há timeout).
- **Regex**: limite de tamanho do padrão (ex.: 512 chars), número de padrões, e
  **limite de tempo de execução**; recusar/avisar padrões com risco de ReDoS.
- **Rate limiting**: por usuário/IP nas rotas de `refresh` e `import` (e no login).

## Lacunas (TODO)

- [ ] `MAX_CONTENT_LENGTH` no upload (hoje sem teto).
- [ ] Limite do conteúdo descompactado (contar bytes/arquivos) — zip bomb.
- [ ] Quotas por projeto (~15 MB) e por usuário (~2–3 projetos).
- [ ] **ReDoS**: validar/limitar regex do manifest (backend **e** cliente); hoje o
  cliente pode travar. Opção no backend: `regex` com *timeout*; no cliente:
  execução com *watchdog* (ex.: Web Worker).
- [ ] Rate limiting em `refresh`/`import`/login.
- [ ] Criptografia em repouso e expiração/renovação do token OAuth.
- [ ] Limpeza de clones órfãos (rollback já remove o dir; conferir em falhas de git).
- [ ] Logs sem segredos (revisar o que é logado).

## Fases

### Agora (local)

Barato e suficiente para dev: `MAX_CONTENT_LENGTH`, limite de arquivos/bytes no
import e no zip, e um limite de complexidade/tempo para as regex do manifest. Sem
quotas multiusuário.

### Ao hospedar (Fase 4)

Quotas por usuário (15 MB/projeto, 2–3 projetos), rate limiting, token cifrado com
renovação, storage S3/equivalente e observabilidade (métricas de uso por usuário).

## Decisões em aberto

- **Onde** barrar ReDoS: só no backend (na validação do manifest, antes de servir) e/ou
  no cliente? Se no cliente, como (Web Worker + *watchdog*)?
- **15 MB** é por projeto *armazenado* ou por *import* (textos + fontes + fundos)?
- Política ao exceder: **recusar** o import ou importar parcialmente e sinalizar?

## Referências

- `MIGRATION.md` — §9 (Segurança), Fase 4.
- `backend/infra/ingestion.py` (validação de zip/caminhos), `backend/infra/github_source.py`
  (clone/limites), `backend/web/api.py` (upload), `backend/domain/project.py` (manifest).
- `frontend/src/layout.ts` e `frontend/src/segmentation.ts` (regex do manifest no cliente).
- `docs/ideas/github-import-export.md` (repo como fonte/escrita).
