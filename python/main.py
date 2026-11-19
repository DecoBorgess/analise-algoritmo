"""
Uso: python3 python/main.py <arquivo> <k> <quickselect|mom> [pivo=aleatorio|ultimo] [reps=N]

k    = posição desejada, 1-indexada (k=1 é o mínimo).
pivo = só para quickselect; padrão: aleatorio.
reps = número de execuções do algoritmo, cada uma sobre uma cópia do vetor
       lido (padrão: 1). O arquivo é lido uma única vez.

Saída:
Valor encontrado e tempos do algoritmo em segundos
(sem incluir a leitura do arquivo nem a cópia do vetor).

Formato do arquivo (binário, little-endian):
[uint64 n][int64 a_0] ... [int64 a_(n-1)]
"""

import random
import struct
import sys
import time
from array import array

from median_of_medians import median_of_medians
from quickselect import PIVOS, quickselect

SEMENTE = 42  # sorteios do quickselect reprodutíveis entre execuções


def ler_entrada(path):
    with open(path, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))

        arr = array("q")
        arr.fromfile(f, n)  # EOFError se o arquivo estiver truncado

    if sys.byteorder == "big":
        arr.byteswap()

    return arr.tolist()


def main():
    if len(sys.argv) < 4 or sys.argv[3] not in ("quickselect", "mom"):
        sys.exit(
            f"uso: {sys.argv[0]} <arquivo> <k> <quickselect|mom> "
            "[pivo=aleatorio|ultimo] [reps=N]"
        )

    algoritmo = sys.argv[3]
    pivo = None
    reps = 1

    for opcao in sys.argv[4:]:
        if opcao.startswith("pivo="):
            pivo = opcao[5:]
            if pivo not in PIVOS:
                sys.exit("pivo deve ser aleatorio ou ultimo")
        elif opcao.startswith("reps="):
            reps = int(opcao[5:])
            if reps < 1:
                sys.exit("reps deve ser >= 1")
        else:
            sys.exit(f"opcao desconhecida: {opcao}")

    if pivo is not None and algoritmo == "mom":
        sys.exit("pivo= so se aplica ao quickselect")

    a = ler_entrada(sys.argv[1])
    k = int(sys.argv[2])

    if not 1 <= k <= len(a):
        sys.exit(f"k deve estar em [1, {len(a)}]")

    if algoritmo == "mom":
        def executar(v):
            return median_of_medians(v, k - 1)
    else:
        modo = pivo or "aleatorio"

        def executar(v):
            return quickselect(v, k - 1, modo)

    random.seed(SEMENTE)

    tempos = []
    r = None

    for rep in range(reps):
        trabalho = a[:]

        t0 = time.perf_counter()
        atual = executar(trabalho)
        tempos.append(time.perf_counter() - t0)

        if rep == 0:
            r = atual
        elif atual != r:
            sys.exit("resultado diferente entre repeticoes")

    print("\n========== RESULTADO ==========")
    print(f"Algoritmo: {'Median of Medians' if algoritmo == 'mom' else 'Quickselect'}")

    if algoritmo == "quickselect":
        print(f"Pivo: {pivo or 'aleatorio'}")

    print(f"Quantidade de elementos: {len(a)}")
    print(f"Posicao procurada (k): {k}")
    print(f"Valor encontrado: {r}")
    print(f"Repeticoes: {reps}")
    print(f"Tempo de execucao: {sum(tempos) / reps:.9f} segundos")
    print("Tempos (s): " + " ".join(f"{t:.9f}" for t in tempos))
    print("================================")


if __name__ == "__main__":
    main()
