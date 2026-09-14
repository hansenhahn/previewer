## Purpose

Oferecer uma visão de tradução assistida que exibe e edita os segmentos
alinhados entre original e traduzido, em caixas, com status e navegação.

## ADDED Requirements

### Requirement: Caixas alinhadas

O sistema SHALL exibir cada par de segmentos alinhados como uma caixa contendo o
segmento original (somente-leitura) e o segmento traduzido (editável), na ordem
dos segmentos. Os segmentos sem par SHALL ser exibidos sinalizados.

#### Scenario: Pares exibidos

- **WHEN** a visão por segmentos é aberta em um projeto com segmentação e ambos
  os textos segmentados
- **THEN** cada par é exibido como uma caixa com original e traduzido

#### Scenario: Segmentos sem par

- **WHEN** a quantidade de segmentos diverge entre original e traduzido
- **THEN** os segmentos excedentes são exibidos sinalizados como sem par

#### Scenario: Sem configuração de segmentação

- **WHEN** o projeto não declara segmentação
- **THEN** a visão informa que a segmentação não está disponível, sem quebrar

### Requirement: Tags de separação abstraídas

O sistema SHALL exibir e editar apenas o **corpo** do segmento nas caixas,
abstraindo as tags de separação (linhas delimitadoras), que são preservadas na
reconstrução.

#### Scenario: Caixa mostra o diálogo

- **WHEN** uma caixa é exibida
- **THEN** o original e o traduzido mostram o corpo do segmento, sem as linhas
  delimitadoras

#### Scenario: Salvar preserva os delimitadores

- **WHEN** o usuário edita o corpo de um segmento e salva
- **THEN** o arquivo mantém as linhas delimitadoras originais em volta do corpo
  editado

### Requirement: Visão inicial por segmentos

O sistema SHALL abrir na visão por segmentos quando o projeto declara
segmentação.

#### Scenario: Projeto com segmentação

- **WHEN** um projeto com `segments` é aberto
- **THEN** a visão por segmentos é exibida por padrão

### Requirement: Edição por segmento

O sistema SHALL permitir editar o texto de cada caixa traduzida, atualizando o
segmento correspondente.

#### Scenario: Editar uma caixa

- **WHEN** o usuário altera o texto de uma caixa traduzida
- **THEN** o segmento correspondente passa a refletir o novo texto

### Requirement: Salvar por reconstrução

O sistema SHALL reconstruir o arquivo traduzido a partir dos segmentos editados e
dos separadores preservados, e persistí-lo, mantendo intacto o que não foi
editado.

#### Scenario: Salvar mantém a estrutura

- **WHEN** o usuário salva após editar segmentos
- **THEN** o arquivo persistido contém as edições e preserva os separadores

### Requirement: Status e navegação

O sistema SHALL indicar o status de cada segmento (por exemplo, vazio ou
preenchido) e permitir navegar para o segmento anterior e o próximo.

#### Scenario: Navegar entre segmentos

- **WHEN** o usuário aciona próximo/anterior
- **THEN** o foco vai para o próximo segmento (ou anterior), respeitando os
  limites

### Requirement: Prévia reflete as edições

A prévia SHALL usar o texto traduzido reconstruído, refletindo as edições não
salvas dos segmentos.

#### Scenario: Edição reflete na prévia

- **WHEN** um segmento é editado
- **THEN** a prévia é atualizada a partir do texto reconstruído
