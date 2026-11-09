
"""
Uso: python3 python/main.py <arquivo> <k> <quickselect|mom>

k = posição desejada, 1-indexada (k=1 é o mínimo).

Saída:
Valor encontrado e tempo de execução do algoritmo em segundos
(sem incluir a leitura do arquivo).

Formato do arquivo (binário, little-endian):
[uint64 n][int64 a_0] ... [int64 a_(n-1)]
"""

import struct
import sys
import time
from array import array

from median_of_medians import median_of_medians
from quickselect import quickselect

ALGORITMOS = {
    "quickselect": quickselect,
    "mom": median_of_medians
}


def ler_entrada(path):
    with open(path, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))

        arr = array("q")
        arr.fromfile(f, n)  # EOFError se o arquivo estiver truncado

    if sys.byteorder == "big":
        arr.byteswap()

    return arr.tolist()


def main():
    if len(sys.argv) != 4 or sys.argv[3] not in ALGORITMOS:
        sys.exit(
            f"uso: {sys.argv[0]} <arquivo> <k> <quickselect|mom>"
        )

    a = ler_entrada(sys.argv[1])
    k = int(sys.argv[2])

    if not 1 <= k <= len(a):
        sys.exit(f"k deve estar em [1, {len(a)}]")

    algoritmo = sys.argv[3]

    t0 = time.perf_counter()
    r = ALGORITMOS[algoritmo](a, k - 1)
    dt = time.perf_counter() - t0

    nome_algoritmo = (
        "Median of Medians"
        if algoritmo == "mom"
        else "Quickselect"
    )

    print("\n========== RESULTADO ==========")
    print(f"Algoritmo: {nome_algoritmo}")
    print(f"Quantidade de elementos: {len(a)}")
    print(f"Posicao procurada (k): {k}")
    print(f"Valor encontrado: {r}")
    print(f"Tempo de execucao: {dt:.9f} segundos")
    print("================================")


if __name__ == "__main__":
    main()
