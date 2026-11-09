# analise-algoritmo

<a href="https://docs.google.com/document/d/1gAHpcYxgl8Jwd9g_LKOc4zrBrZBYkzUF-AqN1a5lEeo/edit?usp=sharing">
      <img src="https://img.shields.io/badge/Relatorio_IA_Checkpoint 3-blue?style=for-the-badge&logo=google-docs&logoColor=white" />
</a>

Implementações de **Quickselect** (pivô aleatório) e **Mediana das Medianas**
(BFPRT, pior caso O(n)) em **C** e **Python**, para análise de desempenho com
entradas grandes lidas de arquivo.

## Estrutura

```
c/
  common.h               # swap, partition3, insertion_sort (compartilhados)
  quickselect.{h,c}
  median_of_medians.{h,c}
  main.c                 # lê o arquivo, roda o algoritmo, imprime valor e tempo
python/
  common.py              # particao3, insertion_sort (compartilhados)
  quickselect.py
  median_of_medians.py
  main.py                # idem ao main.c
datasets/                # entradas binárias (input_<n>.binario)
experiments/
  benchmark.py           # roda tudo sobre datasets/ e grava results.csv
  results.csv
graphs/                  # gráficos da análise (vazio por enquanto)
tests/
  teste.py               # corretude: compara com sorted()
```

## Formato dos arquivos de entrada

Binário, little-endian:

```
[uint64 n][int64 a_0][int64 a_1] ... [int64 a_{n-1}]
```

Cabeçalho de 8 bytes com a quantidade de elementos, seguido dos `n` inteiros de
8 bytes. Os arquivos atuais em `datasets/` foram gerados assim:

```python
import random, struct
n = 1000
v = [random.randint(-10**9, 10**9) for _ in range(n)]
with open("datasets/input_1000.binario", "wb") as f:
    f.write(struct.pack("<Q", n))
    f.write(struct.pack(f"<{n}q", *v))
```

## Como rodar

```bash
cc -O2 -o c/main c/main.c c/quickselect.c c/median_of_medians.c   # compilar o C

./c/main datasets/input_100000.binario <k> <algoritmo>            # C
python3 python/main.py datasets/input_100000.binario <k> <algoritmo>   # Python
```

- `<algoritmo>`: `quickselect` ou `mom` (mediana das medianas).
- `<k>`: posição desejada, **1-indexada** (`k=1` é o mínimo; `k=(n+1)/2` é a mediana).
- Saída: `valor tempo_em_segundos`. O tempo mede **só o algoritmo**, sem a leitura do arquivo.

> Os algoritmos reordenam o vetor em memória, mas o arquivo nunca é alterado.

## Como testar

```bash
python3 tests/teste.py
```

Compila o C, gera entradas (aleatórias, muitos duplicados, todas iguais,
ordenadas, ordem reversa; tamanhos de 1 a 20000) e confere os dois algoritmos,
nas duas linguagens, contra `sorted()[k-1]`. Sai com código 1 se algo falhar.
