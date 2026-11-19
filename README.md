# analise-algoritmo

<a href="https://docs.google.com/document/d/1gAHpcYxgl8Jwd9g_LKOc4zrBrZBYkzUF-AqN1a5lEeo/edit?usp=sharing">
      <img src="https://img.shields.io/badge/Relatorio_IA-blue?style=for-the-badge&logo=google-docs&logoColor=white" />
</a>

Seleção do k-ésimo menor elemento: **Quickselect** (O(n) médio, O(n²) pior) e
**Mediana das Medianas** (BFPRT, O(n) garantido), em **C** e **Python**, com
análise experimental de tempo.

## Alterações recentes (adequação às specs do projeto)

- **Pivô no último elemento** em `quickselect` (C e Python), mantendo o modo aleatório; escolhido por `pivo=aleatorio|ultimo` na linha de comando de `main.c` e `main.py`.
- **`reps=N`** nos dois `main`: o arquivo é lido uma vez e o algoritmo roda N vezes sobre cópias do vetor; o tempo continua medindo só o algoritmo.
- **Gerador de entradas** (`experiments/gerar_entradas.py`) com semente fixa e três cenários: aleatório (caso médio), iguais (melhor caso) e crescente (pior caso do pivô fixo), com 6 tamanhos em progressão geométrica. Substitui `gerar_teste.py` e os `entrada_*.bin` antigos.
- **Benchmark** (`experiments/benchmark.py`) refeito: 20 repetições por tamanho, as quatro implementações (quickselect em dois modos de pivô e mom, em C e Python), validação de cada resposta contra `sorted()` e gravação em `results.csv`.
- **Análise** (`experiments/analise.py`): média, desvio-padrão e razões T/n e T/n² em `summary.csv`, e 5 gráficos em `graphs/` (os gráficos antigos foram removidos por virem de outra metodologia).
- **Testes** passam a cobrir os dois modos de pivô e `reps`.
- Configuração central em `experiments/config.py`; `datasets/*.bin` ficam fora do git (regeneráveis pela semente).
- Ainda não feito: ambiente de execução, comparação teoria × medições e relatório (ficam para o relatório).

## Estrutura

```
c/                       common.h, quickselect.{h,c}, median_of_medians.{h,c}, main.c
python/                  common.py, quickselect.py, median_of_medians.py, main.py
datasets/                entradas binárias geradas (ignoradas pelo git)
experiments/
  config.py              cenários, tamanhos, repetições, semente
  gerar_entradas.py      gera datasets/ com semente fixa
  benchmark.py           roda as implementações e grava results.csv
  analise.py             média, desvio-padrão, razões e gráficos
  results.csv            todos os tempos medidos
  summary.csv            média / desvio por (cenário, linguagem, variante, n)
graphs/                  5 gráficos gerados por analise.py
tests/validacao_de_algoritimo.py   corretude contra sorted()
```

## Como reproduzir os resultados

Da raiz do repositório (precisa de `gcc`, Python 3, `numpy` e `matplotlib`):

```bash
python3 tests/validacao_de_algoritimo.py   # 1. corretude das implementações
python3 experiments/gerar_entradas.py      # 2. gera datasets/ (semente fixa)
python3 experiments/benchmark.py           # 3. 20 repetições por tamanho
python3 experiments/analise.py             # 4. summary.csv + graphs/*.png
```

`benchmark.py [N]` aceita outro número de repetições (ex.: `3` para um teste
rápido). O passo 3 leva alguns minutos, a maior parte no pior caso em Python.
Ele para com erro se alguma resposta divergir de `sorted()[k-1]`.

## Cenários, casos e tamanhos

Todos usam `k` = mediana e são lidos dos mesmos arquivos pelas quatro
implementações. Tamanhos em progressão geométrica (6 por cenário):

| Cenário | Caso provocado | Tamanhos |
|---|---|---|
| `aleatorio` (valores aleatórios, semente 42) | caso médio | 1.000 · 4ⁱ (1 mil a 1,024 milhão) |
| `iguais` (todos 42) | melhor caso do quickselect: 1 passada | 1.000 · 4ⁱ |
| `crescente` (0, 1, …, n-1) | pior caso do quickselect com pivô fixo: O(n²) | 1.000 · 2ⁱ (1 mil a 32 mil) |

O cenário `crescente` é menor porque o pior caso quadrático em Python leva
dezenas de segundos já com 32 mil elementos.

Variantes medidas (por linguagem): `quickselect-aleatorio` (pivô sorteado),
`quickselect-ultimo` (pivô fixo no último elemento, usado para forçar o pior
caso) e `mom`. A mediana das medianas é Θ(n) em qualquer entrada, então não
tem um pior caso diferente do médio.

O tempo mede **só o algoritmo**: leitura do arquivo e cópia do vetor entre
repetições ficam fora. Cada programa lê o arquivo uma vez e repete o algoritmo
sobre cópias, então o pivô aleatório muda a cada repetição (com semente fixa,
resultado reprodutível).

## Gráficos (`graphs/`)

1. `1_caso_medio.png`: tempo × n, entrada aleatória (log-log, barras = ±1 desvio-padrão).
2. `2_melhor_caso.png`: tempo × n, elementos iguais.
3. `3_pior_caso.png`: tempo × n, entrada crescente.
4. `4_razao_caso_medio.png`: T(n)/n no caso médio; constante indica O(n).
5. `5_razao_pior_caso.png`: T(n)/n² do quickselect com pivô fixo (constante indica O(n²)) e T(n)/n das demais variantes.

Nos gráficos 1 a 3 a legenda traz a inclinação medida em log-log (≈1 linear, ≈2 quadrático).

## Executando um programa isolado

```bash
gcc -O2 -std=c11 -D_POSIX_C_SOURCE=200809L -o c/main c/main.c c/quickselect.c c/median_of_medians.c

./c/main datasets/aleatorio_16000.bin 8000 quickselect pivo=ultimo reps=5   # C
python3 python/main.py datasets/aleatorio_16000.bin 8000 mom                # Python
```

Argumentos: `<arquivo> <k> <quickselect|mom> [pivo=aleatorio|ultimo] [reps=N]`.
`k` é 1-indexado (`k=1` é o mínimo); `pivo` só vale para o quickselect
(padrão `aleatorio`); `reps` repete a execução (padrão 1).

## Formato dos arquivos de entrada

Binário, little-endian: `[uint64 n][int64 a_0] ... [int64 a_(n-1)]`.

## Funções auxiliares

| Função | Onde | Papel |
|---|---|---|
| `partition3` / `particao3` | `common` | Reorganiza `a[lo..hi]` em torno de um pivô em três faixas (`<`, `==`, `>`) e devolve onde a faixa dos iguais começa e termina. Com valores repetidos, uma passada resolve. |
| `insertion_sort` | `common` | Ordena trechos minúsculos (grupos de 5 e caso base). |
| `quickselect` | `quickselect` | Escolhe o pivô (aleatório ou último), particiona e descarta o lado sem a posição `k`. |
| `mom_pivot` / `_mom_pivo` | `median_of_medians` | Mediana das medianas de grupos de 5; é o pivô, e garante descartar ~30% por passo. |
| `mom_select` / `_mom_select` | `median_of_medians` | Laço de seleção que usa o pivô acima; chama `mom_pivot` e vice-versa. |
| `median_of_medians` | `median_of_medians` | Ponto de entrada. |

Internamente `k` é 0-indexado; a linha de comando converte (`k - 1`).
