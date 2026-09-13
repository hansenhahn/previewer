## 1. Manifesto (project-manifest)

- [x] 1.1 Criar `domain/project.py` com `ProjectManifest` e `parse_manifest(data)` lendo formato, versão, nome, encoding, textos, fontes, backgrounds, telas, tags e matches; verificar teste com um manifesto válido
- [x] 1.2 Validar o manifesto (formato/versão reconhecidos, campos obrigatórios, referências de tela consistentes) e levantar `ManifestError` explícito; verificar testes de manifesto ausente, versão não suportada e campo inválido
- [x] 1.3 Rodar `.venv/bin/python -m pytest tests/ -k manifest` e confirmar os cenários de `project-manifest`

## 2. Listagem de arquivos no storage (project-storage)

- [x] 2.1 Adicionar `list_files(owner_id, project_id)` ao `StorageBackend` e ao `FilesystemStorage`, retornando caminhos relativos; verificar teste que lista o que foi escrito
- [x] 2.2 Garantir que `list_files` respeita o isolamento da raiz; verificar teste com projeto inexistente (lista vazia) e sem acesso fora do projeto

## 3. Ingestão de projeto (project-ingestion)

- [x] 3.1 Criar `infra/ingestion.py` para ler o `.zip`, extrair e validar o manifesto, e validar todos os membros antes de escrever; verificar teste de importação bem-sucedida
- [x] 3.2 Rejeitar membros com travessia/absolutos sem escrever fora do projeto; verificar teste com membro `../` que não cria arquivo fora
- [x] 3.3 Registrar o projeto no `ProjectRepository` e tratar conflito de nome; verificar teste de nome duplicado rejeitado sem sujar storage
- [x] 3.4 Rejeitar bundle sem manifesto válido; verificar teste que nenhum projeto é criado

## 4. API de projetos (project-ingestion)

- [x] 4.1 Criar `app/api.py` com o blueprint em `/api`, tratamento de erros em JSON e o proprietário stub `local`; registrar na factory e injetar `storage`/`projects`; verificar `GET /api/projects` retornando lista vazia
- [x] 4.2 Implementar `POST /api/projects` (multipart `.zip`) chamando a ingestão; verificar teste 201 e projeto presente em `GET /api/projects`
- [x] 4.3 Implementar `GET /api/projects/<id>` com manifesto e metadados; verificar teste 200 e 404 para id inexistente

## 5. API de arquivos (project-files)

- [x] 5.1 Implementar `GET /api/projects/<id>/files` listando caminhos relativos; verificar teste com arquivos importados
- [x] 5.2 Implementar `GET /api/projects/<id>/files/<path>` decodificando com o encoding do projeto; verificar teste de leitura e 404 para caminho inexistente
- [x] 5.3 Implementar `PUT /api/projects/<id>/files/<path>` codificando com o encoding do projeto; verificar teste de salvar e reler com o mesmo texto

## 6. Atlas de fonte (font-atlas)

- [x] 6.1 Criar `infra/atlas.py` gerando PNG (Pillow) e métricas a partir dos bytes da fonte; verificar teste com a fixture real `tests/fixtures/fonts/fontevent.NFTR` (assinatura PNG e métricas por codepoint)
- [x] 6.2 Adicionar `Pillow` a `requirements.txt`; verificar `pip install` e o teste do atlas passando
- [x] 6.3 Implementar `GET /api/projects/<id>/fonts/<name>/atlas` (JSON com `image_url` e métricas) e `.../atlas.png`; verificar teste 200 e `Content-Type` de imagem
- [x] 6.4 Tratar fonte não suportada com erro explícito; verificar teste com conteúdo inválido

## 7. Verificação final

- [x] 7.1 Rodar a suíte completa (`.venv/bin/python -m pytest`) e confirmar que todos os testes passam
- [x] 7.2 Confirmar que o app legado e o `domain/`/`infra/` das fases anteriores não sofreram alteração indevida; verificar com `git status` restrito a esses caminhos
- [x] 7.3 Confirmar que o novo código não importa GTK/cairo; verificar com `git grep -n "gtk\|cairo" -- app/ infra/ domain/`
- [x] 7.4 Validar a change com `openspec validate project-api-font-atlas --strict`
