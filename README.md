## Modelos
Expansões da distância comóvel por aproximantes de Padé. Expansões implementadas:
- $P_{2,1}$
- $P_{2,2}$
- $P_{3,1}$
- $P_{3,2}$

## Dados
Há quatro conjuntos de dados possíveis:
- 33 dados de cronômetros cósmicos compilados em [Moresco (2024)](https://arxiv.org/abs/2412.01994).
- Dados de supernovas do Pantheon+ com ou sem calibração pelo SH0ES.
- 18 dados de BAO compilados em [Staicova & Benisty (2022)](https://doi.org/10.1051/0004-6361/202244366).
- 14 dados de BAO do [DESI DR2](https://github.com/CobayaSampler/bao_data/tree/master/desi_bao_dr2)

## Dados sintéticos
O arquivo `mock_generator.py` localizado em `scripts\mock_generator\` gera dados sem ruídos para os quatro tipos de dados disponíveis. A covariância original é mantida. É possível gerar os dados a partir do modelo $\Lambda$CDM ou dos modelos considerando os aproximantes de Padé $P_{21}$, $P_{22}$ e $P_{31}$. O arquivo gera automaticamente os quatro tipos de dados para os quatro modelos e os salva na pasta `mock_data`.

## Funcionamento
Para escolher qual modelo ajustar e quais dados usar, basta modificar a lista `tarefas` no início do arquivo `run_batch.py`. É uma lista de dicionários cuja estrutura é
- `'modelo'`: insere o modelo a ser ajustado (`'P21'`, `'P22'` ou `'P31'`).
- `'dados'`: lista contendo os tipos de dados a serem usados (`'cc'`, `'sne'`, `'bao_desi'` e `'bao_seb'`). A lista pode conter de um a quatro elementos.
- `'sh0es'`: indicativo para usar ou não a calibração do SH0ES (`True` ou `False`).
- `'nlive'`: número do parâmetro `nlive` do `PyPolyChord` (variável do tipo `int`).
- `'seed'`: valor da seed a ser usada pelo `PyPolyChord`.
- `'mock'`: parâmetro opcional. Se não estiver presente, usará as versões reais dos dados contidos na lista `'dados'`. O valor deve ser um dos quatro modelos usados para gerar os dados sintéticos (`'LCDM'`, `'P21'`, `'P22'` ou `'P31'`).

Uma vez construídos os dicionários dos modelos a serem ajustados, basta rodar o arquivo `run_batch.py`. Os resultados serão salvos na pasta `resultados`.
