## Why

As Fases 1 e 2 entregaram o domínio puro e o esqueleto web (Flask, storage,
Postgres, Docker), mas o serviço ainda não faz nada de útil: só existe `/` e
`/healthz`. Esta é a **Fase 3a do MIGRATION.md** (metade backend da Fase 3):
expor o núcleo funcional por HTTP — importar um projeto, navegar/editar seus
textos e obter a fonte pronta para o preview. O frontend (canvas 256×192 +
CodeMirror) fica para a 3b.

## What Changes

- Definir o **formato de projeto** da nova plataforma: um `manifest.json`
  (formato, versão, nome, encoding, pastas de texto/original, fontes,
  backgrounds, telas, tags e matches) com validação.
- **Importar projeto** por upload de um bundle `.zip`, validando o manifesto e
  extraindo os arquivos de forma segura (sem travessia de caminho), registrando o
  projeto no catálogo e vinculando-o ao storage.
- **Listar projetos** disponíveis.
- **Navegar e editar textos**: listar os arquivos de texto, ler o conteúdo
  (respeitando o encoding do projeto via `domain/`) e salvar alterações.
- **Atlas de fonte**: decodificar a fonte do projeto com `domain/` e servir um
  **PNG** com os glifos mais um **JSON de métricas** (dimensões, `line_height`,
  avanço/leading por glifo e mapeamento codepoint → posição no atlas), formato
  agnóstico e pronto para o canvas.
- Adicionar à camada de storage a operação de **listar arquivos** de um projeto
  (hoje só há criar/listar projeto e ler/escrever/remover arquivo).
- Novas dependências: `Pillow` (compor o PNG do atlas).

## Capabilities

### New Capabilities
- `project-manifest`: contrato do `manifest.json` e sua validação.
- `project-ingestion`: importar um bundle zip (extração segura), registrar no
  catálogo e listar projetos.
- `project-files`: listar, ler e salvar os arquivos de texto do projeto.
- `font-atlas`: servir o atlas PNG dos glifos e as métricas da fonte.

### Modified Capabilities
- `project-storage`: adicionar a operação de listar arquivos de um projeto ao
  contrato de armazenamento.

## Impact

- **Novo:** `domain/project.py` (manifesto), `app/api.py` (blueprint
  `/api/projects`), `infra/ingestion.py` (import + extração segura),
  `infra/atlas.py` (geração do atlas) e testes.
- **Alterado:** `app/__init__.py` (registrar o blueprint e injetar storage),
  `infra/storage.py` (listar arquivos), `requirements.txt`/`Dockerfile`
  (Pillow).
- **Não alterado:** o app legado e a Fase 1/2 (exceto o ponto de extensão acima).
- **Não-objetivos:** ver seção própria.
- Referência: `MIGRATION.md` §7 (Fase 3), §9 (Segurança: travessia de caminho).

## Não-objetivos

- Frontend: canvas 256×192, CodeMirror, Vite/TypeScript — change 3b.
- Autenticação e isolamento real por usuário — Fase 4 (aqui `owner_id` continua
  o stub `local`).
- Limites de tamanho de upload, rate limiting e antivírus — Fase 4.
- Editar o manifesto pela API, criação de projetos sem bundle, versionamento de
  revisões de texto, S3 e preview renderizado em imagem no servidor.
