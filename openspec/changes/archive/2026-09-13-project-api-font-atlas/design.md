## Context

Ver `proposal.md` — Why. As Fases 1 e 2 já entregaram `domain/` (fontes, layout,
texto), `infra/` (`StorageBackend`, `Database`, `ProjectRepository`, `Project`) e
o esqueleto Flask com `/` e `/healthz` (specs em `openspec/specs/`). Falta expor
o núcleo por HTTP. Decisão do usuário: a Fase 3 foi dividida em **3a (backend,
este change)** e **3b (frontend Vite/TS/CodeMirror)**; o formato de projeto é um
**`manifest.json` novo**.

## Goals / Non-Goals

**Goals:**
- Contrato `manifest.json` validado.
- Importar bundle `.zip` com extração segura e registro no catálogo.
- Listar projetos; listar/ler/salvar textos respeitando o encoding.
- Atlas de fonte (PNG) + métricas (JSON) para consumo do canvas.
- Tudo testável sem frontend e sem Docker.

**Non-Goals:**
- Frontend, canvas, CodeMirror (3b).
- Auth/isolamento real, limites de upload, rate limiting (Fase 4): `owner_id`
  continua o stub `local`.
- Migrar o formato legado; editar manifesto via API; S3.

## Decisions

### 1. Manifesto `manifest.json` v1
```json
{
  "format": "previewer-project",
  "version": 1,
  "name": "Meu Projeto",
  "encoding": "windows-1252",
  "texts": {"source": "texts", "original": "original"},
  "fonts": [{"name": "fontevent", "path": "fonts/fontevent.NFTR"}],
  "backgrounds": [{"name": "bg1", "path": "backgrounds/bg1.png"}],
  "screens": [{"name": "default", "font": "fontevent", "background": "bg1",
               "x": 8, "y": 16, "new_line": 12}],
  "tags": [],
  "matches": []
}
```
`domain/project.py` (puro) expõe um dataclass `ProjectManifest` e
`parse_manifest(data: bytes) -> ProjectManifest`, validando formato, versão
suportada (`1`), campos obrigatórios (`name`, `encoding`, `texts`) e referências
consistentes (toda `screen.font`/`screen.background` existe na lista). Erros são
`ManifestError` (domínio). Alternativa: uma biblioteca de JSON Schema —
rejeitada por dependência extra e YAGNI. Não introduzimos o registro
`ProjectFormat` completo ainda (OCP fica para a Fase 5); o módulo já isola a
concretude.

### 2. Bundle e extração segura
O bundle é um `.zip` com `manifest.json` na raiz; os caminhos referenciados são
relativos. A ingestão:
1. abre o zip e lê `manifest.json`; valida com `parse_manifest`;
2. valida **todos** os membros antes de escrever: rejeita caminho absoluto,
   `..`, ou que resolva para fora do diretório do projeto (reusa a checagem de
   `_segment`/`_resolve`-like via `infra`); também rejeita membros que
   referenciem os caminhos exigidos pelo manifesto inexistentes;
3. só então escreve, usando `StorageBackend.write_file` (o isolamento já mora
   lá — não duplicamos segurança);
4. registra o projeto no catálogo.
Essa ordem (validar tudo antes de escrever) minimiza escrita parcial.
Alternativa: extrair com `zipfile.extractall` — rejeitada por ser vulnerável a
zip-slip.

### 3. Atomicidade catálogo ↔ storage
Ordem: `parse` → `pre-check` de nome no `ProjectRepository` → `create` da linha
(UUID gerado no app) → `create_project`/escrita dos arquivos. Conflito de nome
via `IntegrityError` vira `409`. Se a escrita falhar, apagamos a linha e os
arquivos já escritos (rastreados) via `storage.delete_file`. Sem transação
distribuída; suficiente para a Fase 3 (limites/robustez maiores vêm na Fase 4).

### 4. API HTTP (`app/api.py`, blueprint em `/api`)
| Método | Rota | Comportamento |
|---|---|---|
| POST | `/api/projects` | multipart `file` (.zip) → 201 `{id,name,encoding}` |
| GET | `/api/projects` | lista `{id,name,encoding,created_at}` |
| GET | `/api/projects/<id>` | manifesto + metadados → 200 / 404 |
| GET | `/api/projects/<id>/files` | lista caminhos relativos |
| GET | `/api/projects/<id>/files/<path>` | `{path,content,encoding}` / 404 |
| PUT | `/api/projects/<id>/files/<path>` | `{content}` → grava / 404 |
| GET | `/api/projects/<id>/fonts/<name>/atlas` | JSON de métricas + `image_url` |
| GET | `/api/projects/<id>/fonts/<name>/atlas.png` | PNG do atlas |

Erros em JSON `{"error": {"code", "message"}}` com códigos `invalid_manifest`,
`invalid_bundle`, `unsupported_font`, `not_found`, `conflict`. `owner_id` é o
constante `local` (`app/api.py`) até a Fase 4.

### 5. Wiring na factory
`create_app(settings, database=None, storage=None)` injeta
`app.extensions["storage"]` (`FilesystemStorage(settings.storage_root)`) e
`app.extensions["projects"]` (`ProjectRepository(database.session_factory)`).
Testes injetam dublês/tmp. `app/routes.py` (health/shell) permanece.

### 6. Atlas com Pillow
`infra/atlas.py`: lê os bytes da fonte do storage, `domain.fonts.load_font`,
empacota os glifos (shelf/linha, simples) em uma imagem **RGBA** (branco, alfa =
máscara A8) e devolve `(png_bytes, metrics)`. `metrics` = `{line_height, cell:
{width,height}, image: {width,height}, glyphs: {"<codepoint>": {index, x, y, w,
h, advance, leading}}}`. Codepoints vêm de `font.cmap`. Geração sob demanda (sem
cache na Fase 3; fontes são pequenas). Alternativa: enviar máscaras cruas e
compor no cliente — rejeitada; o MIGRATION pede PNG no backend.
Nova dependência `Pillow`.

### 7. Testes
Manifesto e atlas com unidade pura; ingestão construindo um `.zip` em memória,
incluindo caso malicioso com `../`; API com `Flask.test_client()` sobre SQLite
in-memory + `FilesystemStorage(tmp_path)`; atlas usando a fixture real
`tests/fixtures/fonts/fontevent.NFTR` (checando assinatura PNG e métricas).

## Risks / Trade-offs

- [Zip-slip] → validar todos os membros antes de qualquer escrita; teste
  dedicado; reusar a segurança do `StorageBackend`.
- [Escrita parcial se falhar no meio] → validar antes; cleanup best-effort.
- [Pillow sem wheel para Python 3.14 no venv local] → o runtime Docker é 3.13;
  se o venv local falhar, rodar testes de atlas no container. Verificar no apply.
- [Atlas sem cache] → aceitável no volume atual; cache entra quando houver
  gargalo.
- [Manifesto virar o segundo eixo OCP] → mantido isolado em `domain/project.py`
  para virar `ProjectFormat` na Fase 5 sem retrabalho.

## Migration Plan

- Aditivo: novas rotas e módulos; `/` e `/healthz` inalterados; app legado e
  `domain/` existente intactos.
- Deploy: subir a imagem com Pillow; migrações do banco inalteradas.
- Rollback: remover `app/api.py`, `infra/ingestion.py`, `infra/atlas.py`,
  `domain/project.py` e o registro do blueprint; remover Pillow.

## Open Questions

- Estratégia de cache do atlas (memória vs pré-geração) — decidível quando
  houver gargalo, sem afetar specs ou abordagem.
