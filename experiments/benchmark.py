
"""
Benchmark dos algoritmos Quickselect e Median of Medians.

Executa as implementações em C e Python, registra os tempos
em experiments/results.csv e gera gráficos em graphs/.

Uso:
    python3 experiments/benchmark.py
    python3 experiments/benchmark.py 10

O número informado representa a quantidade de repetições.
"""

import csv
import glob
import os
import re
import statistics
import subprocess
import sys
import struct

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIN_C = os.path.join(RAIZ, "c", "main")
PASTA_EXPERIMENTOS = os.path.join(RAIZ, "experiments")
PASTA_GRAFICOS = os.path.join(RAIZ, "graphs")

SAIDA = os.path.join(PASTA_EXPERIMENTOS, "results.csv")

PROGRAMAS = {
    "c": [BIN_C],
    "python": [
        sys.executable,
        os.path.join(RAIZ, "python", "main.py")
    ],
}

ALGORITMOS = ["quickselect", "mom"]


def compilar_c():
    fontes = [
        os.path.join(RAIZ, "c", arquivo)
        for arquivo in (
            "main.c",
            "quickselect.c",
            "median_of_medians.c"
        )
    ]

    print("\nCompilando programa C...")

    subprocess.run(
        [
            "gcc",
            "-O2",
            "-std=c11",
            "-D_POSIX_C_SOURCE=200809L",
            "-Wall",
            *fontes,
            "-o",
            BIN_C
        ],
        check=True
    )

    print("Compilacao concluida!")


def tamanho(path):
    with open(path, "rb") as arquivo:
        return struct.unpack("<Q", arquivo.read(8))[0]


def executar_programa(programa, arquivo, k, algoritmo):
    processo = subprocess.run(
        programa + [arquivo, str(k), algoritmo],
        capture_output=True,
        text=True
    )

    if processo.returncode != 0:
        raise RuntimeError(
            f"Erro ao executar {algoritmo}:\n{processo.stderr}"
        )

    resultado = re.search(
        r"Tempo de execucao:\s*([0-9.eE+-]+)",
        processo.stdout
    )

    if not resultado:
        raise RuntimeError(
            f"Nao foi possivel encontrar o tempo na saida:\n"
            f"{processo.stdout}"
        )

    return float(resultado.group(1))


def gerar_graficos(dados):
    import matplotlib.pyplot as plt

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    configuracoes = [
        ("geral", ["c", "python"], "Comparacao geral"),
        ("c", ["c"], "Comparacao dos algoritmos em C"),
        ("python", ["python"], "Comparacao dos algoritmos em Python")
    ]

    for nome, linguagens, titulo in configuracoes:
        plt.figure(figsize=(10, 6))

        for linguagem in linguagens:
            for algoritmo in ALGORITMOS:
                pontos = []

                for n in sorted(set(
                    linha["n"] for linha in dados
                )):
                    tempos = [
                        linha["tempo_s"]
                        for linha in dados
                        if linha["linguagem"] == linguagem
                        and linha["algoritmo"] == algoritmo
                        and linha["n"] == n
                    ]

                    if tempos:
                        pontos.append(
                            (n, statistics.mean(tempos))
                        )

                if pontos:
                    plt.plot(
                        [p[0] for p in pontos],
                        [p[1] for p in pontos],
                        marker="o",
                        label=f"{linguagem.upper()} - {algoritmo}"
                    )

        plt.title(titulo)
        plt.xlabel("Quantidade de elementos (n)")
        plt.ylabel("Tempo medio (segundos)")
        plt.xscale("log")
        plt.yscale("log")
        plt.grid(True, which="both", linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()

        caminho = os.path.join(
            PASTA_GRAFICOS,
            f"comparacao_{nome}.png"
        )

        plt.savefig(caminho, dpi=300)
        plt.close()

        print(f"Grafico criado: {caminho}")


def main():
    repeticoes = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    if repeticoes < 1:
        sys.exit("O numero de repeticoes deve ser maior que zero.")

    arquivos = sorted(
        glob.glob(
            os.path.join(PASTA_EXPERIMENTOS, "entrada_*.bin")
        ),
        key=tamanho
    )

    if not arquivos:
        sys.exit("Nenhum arquivo entrada_*.bin encontrado.")

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    compilar_c()

    dados = []

    print("\nINICIANDO BENCHMARK")
    print(f"Repeticoes por experimento: {repeticoes}")
    print(f"Arquivos encontrados: {len(arquivos)}")

    with open(SAIDA, "w", newline="") as arquivo_csv:
        escritor = csv.writer(arquivo_csv)

        escritor.writerow([
            "linguagem",
            "algoritmo",
            "arquivo",
            "n",
            "k",
            "repeticao",
            "tempo_s"
        ])

        for arquivo in arquivos:
            n = tamanho(arquivo)
            k = (n + 1) // 2

            print(f"\n========== N = {n} ==========")

            for linguagem, programa in PROGRAMAS.items():
                for algoritmo in ALGORITMOS:

                    tempos = []

                    for repeticao in range(1, repeticoes + 1):
                        tempo = executar_programa(
                            programa,
                            arquivo,
                            k,
                            algoritmo
                        )

                        tempos.append(tempo)

                        escritor.writerow([
                            linguagem,
                            algoritmo,
                            os.path.basename(arquivo),
                            n,
                            k,
                            repeticao,
                            tempo
                        ])

                        arquivo_csv.flush()

                    dados.append({
                        "linguagem": linguagem,
                        "algoritmo": algoritmo,
                        "n": n,
                        "tempo_s": statistics.mean(tempos)
                    })

                    print(
                        f"{linguagem.upper()} - {algoritmo}: "
                        f"media = {statistics.mean(tempos):.9f}s"
                    )

    print("\nBenchmark concluido!")
    print(f"Resultados salvos em: {SAIDA}")

    print("\nGerando graficos...")
    gerar_graficos(dados)

    print("\nTODOS OS PROCESSOS FORAM CONCLUIDOS!")


if __name__ == "__main__":
    main()
