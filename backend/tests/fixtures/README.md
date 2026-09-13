# Fixtures de fonte

Fontes usadas pela suíte:

- `fontevent.NFTR` — fonte real de bitmap do NDS (1 bpp, célula 9×12, 158
  glifos, CMAP tipo tabela). Usada por `tests/test_nftr_real_font.py` para
  validar o parser contra bytes reais, com métricas e hash de bitmap como
  *golden values*.
- NFTR mínimo sintético gerado por `tests/fixtures/fonts/synth.py`, usado para
  os caminhos de contrato e erro, independente de arquivos externos.

Observação: as assinaturas de bloco do NFTR são tags u32 em little-endian, então
no arquivo aparecem invertidas (`RTFN`, `FNIF`, `PLGC`, `HDWC`, `PAMC`). O
parser trata isso; uma implementação que compare `b"NFTR"` cru falha em fontes
reais.
