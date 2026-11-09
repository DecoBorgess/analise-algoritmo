"""Roda os dois algoritmos, em C e Python, sobre os arquivos de datasets/ e
grava os tempos em experiments/results.csv.

Uso (da raiz do repositório): python3 experiments/benchmark.py [repeticoes]

Para cada arquivo, usa k = mediana (k = (n+1)//2). O tempo vem do próprio
programa e mede só o algoritmo, sem a leitura do arquivo.
"""
import csv
import glob
import os
import struct
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_C = os.path.join(RAIZ, "c", "main")
PROGRAMAS = {
    "c": [BIN_C],
    "python": [sys.executable, os.path.join(RAIZ, "python", "main.py")],
}
ALGORITMOS = ["quickselect", "mom"]
SAIDA = os.path.join(RAIZ, "experiments", "results.csv")


def compilar_c():
    fontes = [os.path.join(RAIZ, "c", f) for f in ("main.c", "quickselect.c", "median_of_medians.c")]
    subprocess.run(["cc", "-O2", "-Wall", "-o", BIN_C, *fontes], check=True)


def tamanho(path):
    with open(path, "rb") as f:
        return struct.unpack("<Q", f.read(8))[0]


def main():
    repeticoes = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    arquivos = sorted(glob.glob(os.path.join(RAIZ, "datasets", "*.binario")), key=tamanho)
    if not arquivos:
        sys.exit("nenhum arquivo *.binario em datasets/")
    compilar_c()

    with open(SAIDA, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["linguagem", "algoritmo", "arquivo", "n", "k", "repeticao", "tempo_s"])
        for arq in arquivos:
            n = tamanho(arq)
            k = (n + 1) // 2
            for lang, prog in PROGRAMAS.items():
                for alg in ALGORITMOS:
                    for rep in range(1, repeticoes + 1):
                        saida = subprocess.run(prog + [arq, str(k), alg], capture_output=True, text=True, check=True)
                        _valor, tempo = saida.stdout.split()
                        w.writerow([lang, alg, os.path.basename(arq), n, k, rep, tempo])
                    print(f"{os.path.basename(arq)} {lang} {alg}: ok")
    print(f"resultados em {os.path.relpath(SAIDA, RAIZ)}")


if __name__ == "__main__":
    main()
