## Purpose

Definir o contrato de formato de fonte e decodificar fontes em um modelo de
glifos consumível pela renderização, começando pelo formato NFTR do NDS.

## ADDED Requirements

### Requirement: Identificação de formato pelo conteúdo

O sistema SHALL identificar o formato de uma fonte a partir do conteúdo binário
(magic bytes), sem que o chamador informe o formato. O sistema SHALL rejeitar
conteúdo não reconhecido com erro explícito, sem retornar dados parciais.

#### Scenario: Fonte NFTR reconhecida

- **WHEN** um conteúdo iniciado pela assinatura `NFTR` é submetido à carga
- **THEN** o formato NFTR é selecionado e a fonte é decodificada

#### Scenario: Conteúdo desconhecido rejeitado

- **WHEN** um conteúdo sem assinatura de formato suportado é submetido à carga
- **THEN** um erro de formato não suportado é retornado

### Requirement: Decodificação de fonte NFTR

O decodificador NFTR SHALL ler os chunks `FINF`, `CGLP`, `CWDH` e `CMAP`,
expondo largura e altura do glifo, bits por pixel, o mapa de caracteres
(codepoint → índice de glifo), as métricas por glifo (avanço e offsets) e o mapa
de bits de cada glifo no formato de 8 bits por pixel.

#### Scenario: Métricas e mapeamento extraídos

- **WHEN** uma fonte NFTR válida é decodificada
- **THEN** o modelo expõe largura e altura do glifo, o `line_height`, e para cada
  codepoint mapeado o índice de glifo, o avanço e o mapa de bits correspondentes

#### Scenario: Caractere ausente do mapa

- **WHEN** o texto contém um codepoint não presente no `CMAP` da fonte
- **THEN** o modelo fornece um glifo não mapeado com avanço padrão, sem falhar

### Requirement: Modelo de fonte agnóstico de formato

O sistema SHALL expor um modelo de fonte único, com consulta de glifo por
codepoint, avanço e altura de linha, do qual o layout depende sem conhecer o
formato concreto. Adicionar um novo formato SHALL ocorrer por novo adaptador
registrado, sem alterar o código de carga nem o de layout.

#### Scenario: Adicionar formato sem alterar o núcleo

- **WHEN** um segundo formato de fonte é registrado no sistema
- **THEN** ele é carregado pelo mesmo ponto de entrada e consumido pelo layout
  sem modificação no código de carga ou de layout existente

### Requirement: Falha segura em entrada inválida

O decodificador SHALL falhar de forma explícita e previsível diante de um
arquivo truncado ou corrompido, em vez de retornar dados inconsistentes.

#### Scenario: Arquivo truncado

- **WHEN** um conteúdo NFTR incompleto é decodificado
- **THEN** um erro de decodificação é retornado
