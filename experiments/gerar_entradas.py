"""Gera os arquivos de entrada em datasets/ com semente fixa.

Uso (da raiz do repositório): python3 experiments/gerar_entradas.py

Formato (binário, little-endian): [uint64 n][int64 a_0] ... [int64 a_(n-1)]
Cenários e tamanhos: ver experiments/config.py. Rodar duas vezes gera
arquivos idênticos.
"""
import os
import random
import struct
import sys
from array import array

from config import PASTA_DATASETS, SEMENTE, TAMANHOS, caminho_entrada

VALOR_IGUAL = 42


def gerar(cenario, n):
    if cenario == "aleatorio":
        rng = random.Random(SEMENTE + n)  # semente fixa, uma por arquivo
        return array("q", (rng.randint(0, 2**31 - 1) for _ in range(n)))
    if cenario == "iguais":
        return array("q", [VALOR_IGUAL]) * n
    if cenario == "crescente":
        return array("q", range(n))
    raise ValueError(cenario)


def main():
    os.makedirs(PASTA_DATASETS, exist_ok=True)

    for cenario, tamanhos in TAMANHOS.items():
        for n in tamanhos:
            valores = gerar(cenario, n)

            if sys.byteorder == "big":
                valores.byteswap()  # garante little-endian no arquivo

            caminho = caminho_entrada(cenario, n)

            with open(caminho, "wb") as f:
                f.write(struct.pack("<Q", n))
                valores.tofile(f)

            print(f"{os.path.relpath(caminho)}: {n:,} elementos")

    print("Entradas geradas.")


if __name__ == "__main__":
    main()
