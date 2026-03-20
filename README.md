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

## Funcionamento
Para escolher qual modelo ajustar a quais dados, basta modificar a lista `tarefas` no início do arquivo `run_batch.py`. Para escolher o modelo, basta digitar a expansão correspondente. Quanto aos dados que serão usados, deve-se adicioná-los na lista `dados` através de suas siglas:
- `cc`: cronômetros cósmicos;
- `sne`: supernovas;
- `bao_seb`: dados de BAO de Staicova & Benisty (2022).
Para escolher entre usar ou não a calibração do SH0ES, basta alterar o valor de `sh0es` para `True`or `False`.