## Context

Ver `proposal.md` — Why. O `ProjectRepository.delete` e o
`StorageBackend.delete_project` já existem; falta orquestrar a remoção e expor na API/UI.
A tabela `changes` tem FK (`changes.project_id → projects.id`) **sem cascade**, então as
alterações precisam ser apagadas antes do projeto.

## Goals / Non-Goals

**Goals:** remover um projeto do usuário (registro + alterações + working copy) por uma rota
autenticada, com ação equivalente na interface.

**Non-Goals:** mexer no GitHub; soft-delete/desfazer; remoção administrativa de projetos de
terceiros.

## Decisions

### 1. Ordem da remoção: changes → projeto → working copy
Apagar primeiro as linhas de `changes` do projeto (novo
`ChangeRepository.delete_for_project(project_id)`), depois o registro (`ProjectRepository.delete`)
e por fim o diretório do working copy (`StorageBackend.delete_project`, que já é `rmtree`
tolerante). Se a remoção do diretório falhar, o registro já foi apagado — o pior caso é
**arquivos órfãos**, não inconsistência de banco.

### 2. Rota `DELETE /projects/<id>` restrita ao dono
Reusa `_project(project_id)` (que já valida dono via `owner_id`). Retorna **404** quando o
projeto não existe ou não é do usuário (não vaza existência), **204** no sucesso. Não é
idempotente em termos de resposta (segunda chamada → 404), o que é aceitável.

### 3. Remoto intocado
A remoção **não** fecha PRs nem apaga branches no fork/upstream. É uma operação de
**working copy local**. Isso mantém o app fora da responsabilidade de mantenedor e evita
apagar contribuições por engano. Trade-off: podem sobrar branches/PRs no GitHub; o usuário
resolve lá, se quiser.

### 4. UI: lixeira por projeto no seletor, com confirmação
Cada **linha do seletor** ganha um botão de **lixeira** (mesmo padrão da lista do Retomar),
com diálogo de confirmação. Hoje a linha é um único `<button>`; para acomodar a lixeira sem
aninhar botões (HTML inválido), a linha passa a ser uma `div` com o **botão do nome**
(navega) e o **botão lixeira** (remove). Funciona no desktop e na gaveta do mobile. Se o
projeto removido for o **aberto**, a interface volta ao estado "sem projeto" (limpa
documentos, arquivos e prévia) e recarrega a lista.

### 5. Confirmação forte: digitar "confirmar"
Por ser destrutivo, o diálogo de remoção **não** basta com um clique: exige **digitar
`confirmar`** no campo para **habilitar** o botão de remover. O texto é comparado
**case-insensitive** com aparas de espaço; qualquer outro valor mantém o botão desabilitado.
Isso evita remoção acidental (ex.: toque errado no mobile).

## Risks / Trade-offs

- **Dados no GitHub permanecem** (branches/PRs) — intencional; documentado na UI/confirm.
- **Reimportar** recria o working copy do zero (clone esparso) — custo de rede, esperado.
- **Apagar o projeto aberto** exige resetar o estado do front para não apontar para um
  projeto inexistente.
