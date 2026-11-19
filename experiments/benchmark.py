"""
Benchmark do Quickselect e da Mediana das Medianas, em C e Python.

Para cada arquivo de datasets/ (gerado por gerar_entradas.py) roda as
implementações (2 algoritmos x 2 linguagens; o quickselect nos dois modos de
pivô) com k = mediana, confere cada resposta contra sorted() e grava todos os
tempos em experiments/results.csv. Os gráficos são feitos por analise.py.

Uso (da raiz do repositório):
    python3 experiments/gerar_entradas.py     # uma vez
    python3 experiments/benchmark.py          # 20 repetições (padrão)
    python3 experiments/benchmark.py 3        # teste rápido

O tempo vem do próprio programa e cobre só o algoritmo: a leitura do arquivo
e a cópia do vetor entre repetições ficam de fora.
"""

import csv
import os
import re
import struct
import subprocess
import sys
from array import array

from config import (
    PASTA_EXPERIMENTOS,
    RAIZ,
    REPETICOES,
    TAMANHOS,
    VARIANTES,
    caminho_entrada,
)

BIN_C = os.path.join(RAIZ, "c", "main")
FONTES_C = [
    os.path.join(RAIZ, "c", f)
    for f in ("main.c", "quickselect.c", "median_of_medians.c")
]
FLAGS_C = ["-O2", "-std=c11", "-D_POSIX_C_SOURCE=200809L", "-Wall"]

PROGRAMAS = {
    "c": [BIN_C],
    "python": [sys.executable, os.path.join(RAIZ, "python", "main.py")],
}

SAIDA = os.path.join(PASTA_EXPERIMENTOS, "results.csv")


def compilar_c():
    print("Compilando programa C...")
    subprocess.run(["gcc", *FLAGS_C, *FONTES_C, "-o", BIN_C], check=True)


def ler_entrada(path):
    with open(path, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))
        valores = array("q")
        valores.fromfile(f, n)
    return valores


def executar(programa, arquivo, k, algoritmo, pivo, repeticoes):
    args = programa + [arquivo, str(k), algoritmo, f"reps={repeticoes}"]
    if pivo:
        args.append(f"pivo={pivo}")

    saida = subprocess.run(args, capture_output=True, text=True)

    if saida.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} falhou:\n{saida.stderr}")

    valor = re.search(r"Valor encontrado:\s*(-?\d+)", saida.stdout)
    tempos = re.search(r"Tempos \(s\):(.*)", saida.stdout)

    if not valor or not tempos:
        raise RuntimeError(f"saida inesperada de {' '.join(args)}:\n{saida.stdout}")

    return int(valor.group(1)), [float(t) for t in tempos.group(1).split()]


def main():
    repeticoes = int(sys.argv[1]) if len(sys.argv) > 1 else REPETICOES

    if repeticoes < 1:
        sys.exit("O numero de repeticoes deve ser maior que zero.")

    if not all(
        os.path.exists(caminho_entrada(c, n))
        for c, tamanhos in TAMANHOS.items()
        for n in tamanhos
    ):
        sys.exit("Entradas ausentes; rode antes: python3 experiments/gerar_entradas.py")

    compilar_c()
    print(f"Repeticoes por experimento: {repeticoes}")

    with open(SAIDA, "w", newline="") as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(
            ["cenario", "linguagem", "variante", "arquivo", "n", "k", "repeticao", "tempo_s"]
        )

        for cenario, tamanhos in TAMANHOS.items():
            for n in tamanhos:
                arquivo = caminho_entrada(cenario, n)
                k = (n + 1) // 2
                esperado = sorted(ler_entrada(arquivo))[k - 1]

                print(f"\n=== {cenario}  n={n}  k={k} ===")

                for linguagem, programa in PROGRAMAS.items():
                    for variante, (algoritmo, pivo) in VARIANTES.items():
                        valor, tempos = executar(programa, arquivo, k, algoritmo, pivo, repeticoes)

                        if valor != esperado or len(tempos) != repeticoes:
                            sys.exit(
                                f"RESPOSTA INVALIDA: {linguagem} {variante} {cenario} n={n}: "
                                f"obtido {valor}, esperado {esperado}"
                            )

                        for rep, t in enumerate(tempos, start=1):
                            escritor.writerow(
                                [cenario, linguagem, variante, os.path.basename(arquivo), n, k, rep, f"{t:.9f}"]
                            )
                        arquivo_csv.flush()

                        print(f"  {linguagem:6} {variante:22} media = {sum(tempos) / len(tempos):.6f}s  [ok]")

    print(f"\nResultados em {os.path.relpath(SAIDA, RAIZ)}")
    print("Para o resumo e os graficos: python3 experiments/analise.py")


if __name__ == "__main__":
    main()
