# Roadmap — previewer

> Plano mestre em [`MIGRATION.md`](../MIGRATION.md); ideias e planos detalhados em
> [`docs/ideas/`](ideas/). Este roadmap resume **o que falta** e **em que ordem**,
> ligando cada item ao documento de origem.

## Estado atual

| Frente | Situação | Onde |
|---|---|---|
| Migração web (Fases 0–3) | ✅ domínio puro, Docker, núcleo funcional, CAT/UI | [`MIGRATION.md`](../MIGRATION.md) |
| Identidade (GitHub, identity-only) | ✅ login, sessão, allowlist, isolamento por usuário | PR #3 |
| Import do GitHub | ✅ clone esparso, manifest, selo verde/cinza | [`ideas/github-import-export.md`](ideas/github-import-export.md) |
| Mobile | ✅ prévia fixa, gaveta, edição por segmento | PR #4 |
| **Colaboração (export/push/PR)** | ❌ **não implementado** | [`ideas/git-collaboration-backend.md`](ideas/git-collaboration-backend.md) |
| Endurecimento (Fase 4) | ❌ não implementado | [`ideas/security-hardening.md`](ideas/security-hardening.md) |
| Deploy hospedado | 🟡 validado via túnel (ngrok) | [`MIGRATION.md`](../MIGRATION.md) §8 |

## Roadmap

### R1 — Export: branch + commit + PR ⭐ (próximo de valor)
Transforma o app em **ferramenta de contribuição**: o colaborador publica sem ver
git; a **aceitação/merge fica no GitHub**.
- **R1a (mínimo):** `git status/commit/push` no working copy + **fork → branch →
  PR** via API; mostrar **link/status** do PR; guardar `base_commit`.
- **R1b (check antes de publicar):** comparar com o upstream e **atualizar o
  branch** para não abrir PR velho.
- **Pré-requisito:** credencial de escrita OAuth (`public_repo` no MVP; **GitHub App**
  para privado/enterprise) — troca encapsulada no seam `ProjectExport`.
- Docs: [`ideas/github-import-export.md`](ideas/github-import-export.md),
  [`ideas/git-collaboration-backend.md`](ideas/git-collaboration-backend.md).

### R2 — Sync do upstream e conflito
- **Sync:** `compare` no open + `merge-upstream`/`update-branch`; **auto quando limpo**.
- **Conflito por segmento** (3-vias com a prévia): o diferencial de UX — resolve no
  nível da tradução, não de linhas.
- Docs: [`ideas/git-collaboration-backend.md`](ideas/git-collaboration-backend.md).

### R3 — Endurecimento (Fase 4)
- Limites de upload/quota (~15 MB/projeto; ~2–3 projetos/usuário), **ReDoS** em
  `Tags`/`Matches`, rate limiting.
- Docs: [`ideas/security-hardening.md`](ideas/security-hardening.md),
  [`MIGRATION.md`](../MIGRATION.md) §9.

### R4 — Deploy hospedado (Fase 4)
- Hospedagem (OCI Always Free como alvo do MVP), mantendo portabilidade.
- Docs: [`MIGRATION.md`](../MIGRATION.md) §8.

### R5 — Pequenos
- Excluir projeto; escolher branch/ref no import; repos privados (GitHub App);
  limpar mocks; housekeeping do OpenSpec.

### R6 — Keycloak / Generalização (condicional, YAGNI)
- **Keycloak** para identidade (troca pelo seam `IdentityProvider`).
- **Fase 5:** abstrair formato/plataforma só com o **segundo caso concreto**.
- Docs: [`ideas/iam-keycloak.md`](ideas/iam-keycloak.md),
  [`MIGRATION.md`](../MIGRATION.md) §7 (Fase 5).

## Próximo passo

Abrir o change OpenSpec **`project-export`** cobrindo **R1a + o check de R1b**:
publicar (branch + PR) e sincronizar antes de publicar — sem trazer o merge por
segmento ainda. Seams: `ProjectExport` (e `ProjectSource` para o check de upstream).

## Referências

- [`MIGRATION.md`](../MIGRATION.md) — plano mestre e fases.
- [`ideas/github-import-export.md`](ideas/github-import-export.md) — GitHub-first, import/export.
- [`ideas/git-collaboration-backend.md`](ideas/git-collaboration-backend.md) — colaboração, sync, polling, conflito.
- [`ideas/security-hardening.md`](ideas/security-hardening.md) — limites e segurança.
- [`ideas/iam-keycloak.md`](ideas/iam-keycloak.md) — identidade (Keycloak/GitHub App).
