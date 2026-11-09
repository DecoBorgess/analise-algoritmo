import random
import struct
from array import array
import sys
import os

TAMANHOS = [
    1_000,
    5_000,
    10_000,
    100_000,
    500_000,
    1_000_000
]

SEED = 42
PASTA = "experiments"


def gerar_entradas():
    rng = random.Random(SEED)

    os.makedirs(PASTA, exist_ok=True)

    for n in TAMANHOS:

        nome_arquivo = f"{PASTA}/entrada_{n}.bin"

        print(f"Gerando {n:,} elementos...")

        # Gera números inteiros aleatórios de 64 bits
        valores = array(
            "q",
            (rng.randint(0, 2**31 - 1) for _ in range(n))
        )

        # Garante armazenamento little-endian
        if sys.byteorder == "big":
            valores.byteswap()

        with open(nome_arquivo, "wb") as f:

            # Quantidade de elementos (uint64)
            f.write(struct.pack("<Q", n))

            # Elementos (int64)
            valores.tofile(f)

        print(f"Arquivo criado: {nome_arquivo}\n")

    print("Todos os arquivos foram gerados com sucesso!")


if __name__ == "__main__":
    gerar_entradas()
