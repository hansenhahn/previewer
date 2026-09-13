## 1. Setup

- [x] 1.1 Criar `pyproject.toml` com `requires-python = ">=3.13"`, pacote `domain` e configuração do pytest; verificar com `python -c "import domain"` após criar o pacote
- [x] 1.2 Criar a estrutura `domain/`, `domain/fonts/` e `tests/` com `__init__.py`; verificar que os diretórios e arquivos existem
- [x] 1.3 Instalar dependências de desenvolvimento (`pytest`) em um ambiente virtual; verificar com `python -m pytest --version`

## 2. Codec de texto (project-text)

- [x] 2.1 Implementar `domain/errors.py` com as exceções do domínio; verificar importação em teste
- [x] 2.2 Implementar `decode_text(data, encoding)` com normalização de `\r\n`/`\r` para `\n`; verificar com teste de CRLF e de decodificação no encoding do projeto
- [x] 2.3 Implementar `encode_text(text, encoding)` com round-trip; verificar teste que decodifica o resultado e compara com a entrada
- [x] 2.4 Tratar bytes inválidos com erro explícito do domínio; verificar teste que espera a exceção
- [x] 2.5 Rodar `python -m pytest tests/ -k text` e confirmar que todos os cenários de `project-text` passam

## 3. Contratos e registro de fontes (font-decoding)

- [x] 3.1 Definir `Glyph`, `Font` e `FontFormat` em `domain/fonts/base.py` conforme design.md; verificar importação e anotação de tipos
- [x] 3.2 Implementar `register(fmt)` e `load_font(data)` em `domain/fonts/registry.py` com seleção por `sniff`; verificar teste com dublê que casa e com conteúdo desconhecido que gera erro
- [x] 3.3 Registrar adaptadores embutidos em `domain/fonts/__init__.py`; verificar que `load_font` reconhece o NFTR
- [x] 3.4 Adicionar teste que percorre os adaptadores registrados exercitando `sniff`/`load`/`glyph`/`advance` (validação de contrato em runtime); verificar que passa

## 4. Adaptador NFTR (font-decoding)

- [x] 4.1 Portar o parsing de `FINF`/`CGLP`/`CWDH`/`CMAP` de `nftr.py` para Python 3 (`bytes`, `zip` lazy, sem `gtk`); verificar com teste que lê largura, altura, bpp e mapeamento de uma fonte
- [x] 4.2 Converter os glifos do CGLP para bitmap A8 com padding de largura/altura; verificar teste que compara `pixels`, `width`, `height` e `advance` com valores conhecidos (golden)
- [x] 4.3 Tratar codepoint ausente do `CMAP` com glifo não mapeado e avanço padrão; verificar teste
- [x] 4.4 Tratar arquivo truncado/corrompido com erro de decodificação; verificar teste que espera a exceção
- [x] 4.5 Rodar `python -m pytest tests/ -k nftr` e confirmar que os cenários de `font-decoding` passam

## 5. Layout da tela (screen-layout)

- [x] 5.1 Implementar `ScreenConfig` e `PlacedGlyph` em `domain/layout.py`; verificar criação via teste
- [x] 5.2 Implementar avanço horizontal a partir de `ScreenXPos` e quebra por `ScreenNewLine`; verificar teste de posições com um `Font` dublê
- [x] 5.3 Implementar sinalização de transbordo horizontal (256 px) e vertical (192 px); verificar testes para linha longa e muitas linhas
- [x] 5.4 Implementar a linha-pivô a partir de `Matches`, com fallback para o início; verificar testes com e sem pivô
- [x] 5.5 Implementar a remoção de `Tags` antes da medição; verificar teste que compara avanço com e sem tag
- [x] 5.6 Garantir que `layout.py` não importa `domain.fonts.nftr` (agnóstico de formato); verificar com teste que usa um `Font` dublê
- [x] 5.7 Rodar `python -m pytest tests/ -k layout` e confirmar que os cenários de `screen-layout` passam

## 6. Fixtures e integração

- [x] 6.1 Adicionar um helper que gera um NFTR mínimo sintético e versionar em `tests/fixtures/fonts/`; verificar com teste que o decodifica
- [x] 6.2 Obter e versionar ao menos uma fonte NFTR real (anonimizada se necessário) em `tests/fixtures/fonts/`; se indisponível, registrar a limitação em `tests/fixtures/README` e manter o teste real como pendência
- [x] 6.3 Rodar `python -m pytest tests/` e confirmar que toda a suíte passa em Python 3.13+

## 7. Verificação final

- [x] 7.1 Confirmar que nenhum arquivo legado (`editor.py`, `drawer.py`, `nftr.py`, `writer.py`, `dialogs/`, `editor.ui`) foi alterado; verificar com `git status`
- [x] 7.2 Executar `git grep -n "^import gtk\|^from gtk" -- domain/` e confirmar que não há dependência de GTK no domínio
