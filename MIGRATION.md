# Plano de Migração — previewer

> De aplicativo desktop (Python 2 + GTK) para web app dockerizável (Python 3 + Flask + Canvas).
> Status: **proposta**. Nada do código legado foi alterado por este documento.

## 1. Objetivo

Reescrever o visualizador/editor de textos NDS como um web app que:

1. Rode **localmente** primeiro (para validar viabilidade), num container.
2. Depois seja **hospedado** para múltiplos usuários.
3. Possa, no futuro, virar um produto **genérico** (não só textos NDS).

Princípios:

- **Dockerizável desde o dia 1** — build reproduzível, config por env, container stateless.
- **Domínio puro** — parsing de fonte, quebra de linha e encoding vivem fora de qualquer UI/framework.
- **Protótipo simples, mas sem becos sem saída** — sem microservices/k8s agora, mas com os *seams* certos (storage, formato, banco).

## 2. Estado atual

| Item | Situação |
|---|---|
| Linguagem | Python 2 (`unicode`, `file`, `filter`, divisão inteira) |
| GUI | Misto GTK2/GTK3 — quebrado |
| Empacotamento | `py2exe` (`setup2.py`) e cx_Freeze (`setup.py`) com dezenas de DLLs |
| Renderização | `cairo` direto em `Gtk.DrawingArea` (`drawer.py`) |
| Config | `ConfigObj` lida de arquivos `.ini` por projeto |
| Artefatos | `editor/` (build py2exe, ~37 MB) e `editor.rar` (16 MB) fora do git |

### Arquivos e papéis

- `editor.py` (293 linhas) — app principal, carrega `editor.ui` via `Gtk.Builder`, orquestra tudo.
- `drawer.py` (201) — desenha background e glifos da fonte NFTR no canvas da tela 256×192.
- `writer.py` (232) — `Gtk.TextBuffer` com pilhas próprias de undo/redo.
- `nftr.py` (138) — parser do formato de fonte NDS **NFTR** (`FINF`/`CGLP`/`CWDH`/`CMAP`). Ainda faz `import gtk`.
- `dialogs/` — `project.py`, `search.py` (`import gtk`, GTK2), `defaults.py` (GTK3), `__init__.py`.
- `configobj.py` (2468) — lib de terceiros; reescrita de line endings pendente no working tree.
- `Pixmaps/`, `editor.ui`, `configobj.pyc`, `*.pyc` — assets e UI.

### Config de projeto (chaves em uso)

Nível projeto (`main_config`): `ConfigFolder`, `TextFolder`, `OriginalFolder`, `BackgroundFolder`, `FontFolder`, `Encoding`, `Tags`, `Matches`.

Nível tela (`cfg_in_use` / `cfg`): `ScreenName`, `ScreenBackground`, `ScreenFont`, `ScreenXPos`, `ScreenYPos`, `ScreenNewLine`.

## 3. Arquitetura alvo

```
┌──────────────────────────────────────────────┐
│ Browser (Canvas 2D + editor de texto)        │
│  - desenha glifos/background                 │
│  - CodeMirror 6 para edição                  │
└───────────────┬──────────────────────────────┘
                │ HTTP/JSON
┌───────────────▼──────────────────────────────┐
│ Flask (gunicorn)                             │
│  ├─ web/         rotas, auth, upload         │
│  ├─ domain/      nftr, layout, encoding      │  ← puro, testável
│  └─ infra/       StorageBackend, DB          │
└───────┬───────────────────────┬──────────────┘
        │                       │
   Volume /data            Postgres
   (ou S3 depois)
```

Camadas com dependência unidirecional: `web → domain`, `web → infra`, `infra → domain`. **`domain` não importa Flask nem storage.**

### 3.1 Extensibilidade (Open/Closed Principle)

Há **dois eixos de variação** independentes, cada um atrás de um contrato abstrato:

1. **Formato de fonte** — NFTR (bitmap) hoje; TTF/OTF (contorno, rasterizado) depois.
2. **Formato de texto/projeto** — NDS hoje; outro jogo/genérico depois.

Contratos (nomes provisórios, definidos pelo primeiro caso concreto):

```python
# domain/fonts/base.py
class FontFormat(Protocol):
    name: str
    def sniff(self, data: bytes) -> bool: ...   # magic bytes (NFTR="NFTR", TTF="\x00\x01\x00\x00"/"true"/"OTTO")
    def load(self, data: bytes) -> Font: ...

class Font(Protocol):
    line_height: int
    def glyph(self, codepoint: int) -> Glyph | None: ...
    def advance(self, codepoint: int) -> int: ...
```

O denominador comum entre bitmap e vetorial é `rasterize(codepoint, size) -> GlyphBitmap`:
NFTR retorna seu bitmap nativo; TTF rasteriza sob demanda. O renderer consome `Font`
genérico e **nunca** conhece o formato. O atlas entregue ao frontend é sempre bitmap,
então o cliente permanece format-agnóstico.

Registro simples via `register(fmt)` + detecção por `sniff` (sem entry points por ora).
O mesmo vale para `ProjectFormat` (`read_text`, `write_text`, `encoding`, `pivot_patterns`).

**Regra de ouro:** no núcleo não pode existir `if format == 'nftr'`. Adicionar formato =
novo módulo + registro, **sem editar código existente**.

**YAGNI:** não criar plugin discovery de terceiros nem abstrair formatos desconhecidos antes
do segundo caso concreto (TTF) validar o contrato.

## 4. Decisões

| Tema | Decisão | Motivo |
|---|---|---|
| Python | **3.13/3.14** estável | Ecossistema maduro; no-GIL é irrelevante aqui (workload I/O-bound) |
| Framework | **Flask + Jinja** | Simples e suficiente; FastAPI só se a API crescer |
| Frontend | **TypeScript + Canvas 2D + CodeMirror 6** | Sem React/Next no início |
| Render | **No cliente** | Tira CPU do servidor, escala melhor, elimina GTK/cairo do runtime |
| Banco | **Postgres** via SQLAlchemy (SQLite aceitável para validar) | Paridade dev/prod; troca sem código |
| Storage | Interface `StorageBackend`; implementação filesystem → S3 | Único seam que não pode ser adiado |
| Fonte | `FontFormat` (NFTR, TTF…) → decodifica no backend 1× → atlas PNG + JSON de métricas/CMAP | Menos round-trips; front format-agnóstico (ver 3.1) |
| Deploy | Monolito Flask + gunicorn, multi-stage image | Dockerizável sem complexidade distribuída |

## 5. Modelo de dados

- `User` → `Project` → (`TextFile`, `Asset`, `ScreenConfig`)
- `Project` tem `owner_id` **desde já** (mesmo com auth anônima/local).
- Settings do projeto migram das chaves `main_config` acima para colunas/JSON validado.
- `ScreenConfig` corresponde ao `cfg_in_use` (nome, background, fonte, X/Y, newline).

Regra: semântica no banco, **não** no layout de pastas. Os arquivos em si ficam no storage.

## 6. Mapeamento componente → novo

| Legado | Novo | Observação |
|---|---|---|
| `nftr.py` | `domain/nftr.py` | Portar p/ Py3; remover `import gtk`; cobrir com testes |
| Lógica de `drawer.py` | `domain/layout.py` + canvas no front | Backend entrega dados, front desenha |
| `writer.py` (undo/redo) | CodeMirror 6 | Não reescrever pilhas de undo na mão |
| `editor.py` (orquestração) | `web/` rotas Flask | Reescrita |
| `dialogs/defaults.py` | endpoint de upload/FileChooser nativo | Upload no host, não path local |
| `configobj.py` | settings no banco | Não portar a lib |
| `editor.ui` | templates Jinja + JS | Reescrita |
| `setup.py` / `setup2.py` | `Dockerfile` + `compose` | Substituídos |

## 7. Fases

### Fase 0 — Higiene do repositório
- [ ] `.gitignore` para `editor/`, `editor.rar`, `*.pyc`, `__pycache__/`.
- [ ] `.gitattributes` para normalizar line endings (o diff atual é só CRLF).
- [ ] Remover `.pyc` do versionamento.

### Fase 1 — Domínio puro (maior risco)
- [ ] Portar `nftr.py` para Python 3 (`bytes`, `zip` lazy, sem `gtk`).
- [ ] Extrair regras de layout/quebra de `drawer.py` para `domain/layout.py`.
- [ ] Portar encoding de `editor.py` para o domínio.
- [ ] Testes unitários com fontes NFTR reais + fixtures.

### Fase 2 — Esqueleto web + Docker
- [ ] `app/` Flask, rota `/healthz`, tela inicial.
- [ ] `Dockerfile` multi-stage + `docker-compose.yml`.
- [ ] `StorageBackend` filesystem apontando para `STORAGE_ROOT`.
- [ ] `.env.example` com as variáveis.

### Fase 3 — Núcleo funcional
- [ ] Upload/abertura de projeto (zip → `STORAGE_ROOT`).
- [ ] Listar arquivos, ler/salvar texto.
- [ ] Endpoint de fonte: atlas PNG + JSON de métricas.
- [ ] Preview no canvas 256×192 com zoom (`image-rendering: pixelated`).
- [ ] Editor CodeMirror com salvar.

### Fase 4 — Pronto para host
- [ ] Auth + isolamento por `owner_id`.
- [ ] Sessões fora de memória (cookie assinado → Redis quando preciso).
- [ ] Validação de upload e limites.
- [ ] Postgres gerenciado + storage S3/equivalente.

### Fase 5 — Generalização (condicional)
- [ ] Extrair `FormatAdapter` (NDS é a primeira implementação).
- [ ] Só abstrair quando existir o **segundo** formato.

## 8. Dockerização

Requisitos: container stateless, dado em volume/S3, config por env, não-root.

Variáveis de ambiente: `STORAGE_ROOT`, `DATABASE_URL`, `SECRET_KEY`, `FLASK_ENV`.

- Imagem: `python:3.13-slim`; build do front em stage Node; runtime sem GTK/cairo.
- Artefatos de usuário **nunca** entram na imagem.
- Healthcheck `/healthz`; rodar como usuário não-root.
- Dev: `compose` com bind mount + debug; Prod: mesma imagem, só env diferente.

## 9. Segurança

- `Tags`/`Matches` são usados como **regex do usuário** → risco de **ReDoS** em host. Aplicar timeout/limite ou regex restrita.
- Upload de projeto: validar path traversal, zip-slip e tamanho.
- `ConfigObj(..., unrepr=True)` parseia config como código — nunca confiar em upload de terceiros.
- Isolar toda leitura de arquivo por usuário/projeto.

## 10. Testes

- `domain/` com cobertura alta (nftr, layout, encoding) — é o núcleo e o maior risco.
- Smokes de rotas Flask e do `StorageBackend`.
- Fixtures: fontes NFTR, backgrounds e um projeto exemplo versionado no repo de testes.

## 11. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Porte do `nftr.py` incorreto | Preview errado | Testes com fontes reais antes de mexer na UI |
| Depender de path local | Trava o host | `StorageBackend` na Fase 2 |
| ReDoS por regex de usuário | Segurança | Limites/timeout na Fase 4 |
| Sobre-engenharia precoce | Atraso | Adiar abstrações até o 2º caso real |

## 12. Não-objetivos (por enquanto)

- Microservices, k8s, separar front/back em repos distintos.
- Abstração de "formato genérico" antes do segundo formato.
- Filas de background (Redis/Celery) antes de haver gargalo real.

## 13. Próximos passos

1. Fase 0 (higiene) e Fase 1 (porte do `domain`, começando por `nftr.py`).
2. Em paralelo, validar o esqueleto Docker da Fase 2.

Ponto de decisão de arquitetura: **SQLite+volume** (mais simples para validar) vs **Postgres no compose** (paridade dev/prod desde já).
