# Maturidade do projeto — previewer

> Retrato pontual (2026-09-15), após o `project-export` (R1a + check de R1b) entrar em
> funcionamento. Não substitui o [`MIGRATION.md`](../MIGRATION.md) nem o
> [`roadmap.md`](roadmap.md); é uma avaliação de onde estamos e do que falta.

## Nível geral: **MVP funcional / beta interno** (R1 entregue, R2–R4 pendentes)

| Frente | Nível | Comentário |
|---|---|---|
| Domínio (NFTR, layout, segmentação, prévia) | **Maduro** | Puro, testável, fixtures reais, testes de conformidade. É o núcleo forte do produto. |
| Arquitetura / seams | **Maduro** | `FontFormat`, `ProjectFormat`, `StorageBackend`, `IdentityProvider`, `ProjectExport` — troca de implementação sem retrabalho. |
| Import GitHub | **Maduro** | Clone esparso + manifest + allowlist. |
| UI (desktop/mobile, CAT, chip, autosave) | **Funcional, iterando** | Boa base; UX ainda em ajuste. |
| Colaboração (export/push/PR) | **Beta recém-nascido** | R1a + check de R1b saíram agora; muitas decisões/iterações recentes. |
| Testes | **Bom** | 27 arquivos no backend (~193 testes), 8 no frontend (~42 testes). Falta **E2E**. |
| Operação/Deploy | **Inicial** | Docker/Postgres/ngrok ok, mas **deploy manual**, sem CI/CD, sem backup do volume/DB, log básico. |
| Segurança | **Inicial** | Escopo `public_repo`, mas token em texto no banco, **CSRF** nos endpoints de escrita (cookie de sessão), sem rate limiting/quotas, ReDoS em Tags/Matches. |
| Processo/Docs | **Bom/avançado** | OpenSpec (21 specs, change-driven), `MIGRATION.md` + roadmap + ideas. Delta specs do `project-export` ainda **não sincronizadas/arquivadas**; nada commitado. |

## Riscos e limitações relevantes

- **1 working copy por projeto** (compartilhado entre usuários) — limitação de
  concorrência/escala aceita no MVP; exige *worktree* por usuário ou *locking* no futuro.
- **CSRF** nas rotas de escrita (POST/PUT/DELETE autenticadas por cookie) — alto valor de
  correção.
- **Token OAuth** em texto no banco e embutido na URL de push (sanitizado nos logs, mas
  ainda assim).
- **Sem quotas/limites** (upload, projetos por usuário) e **sem rate limiting**.
- **Sem CI, deploy automatizado nem backup** do storage/DB.
- **R2 (sync do upstream + merge por segmento)** — o diferencial de UX — ainda não existe.

## Para subir de nível (ordem sugerida)

1. **Fechar o processo do `project-export`**: sincronizar as delta specs
   (`/opsx-sync-specs` ou `/opsx-archive`) e commitar.
2. **Segurança mínima**: proteção CSRF, cifrar o token, quotas/limites.
3. **CI** (rodar `pytest` + `vitest`/build) e **deploy reprodutível** (R4) com backup.
4. **E2E** dos fluxos críticos (import → editar → subir PR).
5. **R2** (sync + merge por segmento) para consolidar o diferencial.

## Mapa com o roadmap

- **R1 — Export (branch + commit + PR):** entregue (este change), incluindo o check antes de
  publicar (R1b) e suporte a repo próprio (sem fork).
- **R2 — Sync/conflito por segmento:** pendente.
- **R3 — Endurecimento:** pendente (CSRF, quotas, rate limiting, ReDoS).
- **R4 — Deploy hospedado:** pendente (hoje só túnel ngrok).

## Resumo

Núcleo de domínio sólido e engenharia disciplinada (seams claros, testes, processo
OpenSpec). A camada de colaboração acabou de virar **funcional**. Falta o "cinto de
segurança" (segurança/limites), automação de entrega e o merge por segmento para sair de
beta interno.
