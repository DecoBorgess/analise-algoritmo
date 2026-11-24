import csv
import os
import re
import subprocess
import sys

from config import (
    RAIZ,
    PASTA_DATASETS,
    PASTA_EXPERIMENTOS,
    PASTA_GRAFICOS,
    TAMANHOS,
    VARIANTES,
    caminho_entrada,
)

BIN_C = os.path.join(RAIZ, "c", "main")

FONTES_C = [
    os.path.join(RAIZ, "c", arquivo)
    for arquivo in ("main.c", "quickselect.c", "median_of_medians.c")
]

PYTHON_MEDIDOR = os.path.join(PASTA_EXPERIMENTOS, "memory_python.py")

SAIDA_CSV = os.path.join(PASTA_EXPERIMENTOS, "memory_results.csv")


def compilar_c():
    print("Compilando C...")

    subprocess.run(
        [
            "gcc",
            "-O2",
            "-std=c11",
            "-D_POSIX_C_SOURCE=200809L",
            "-Wall",
            *FONTES_C,
            "-o",
            BIN_C,
        ],
        check=True,
    )


def medir_python(arquivo, k, algoritmo, pivo):
    comando = [
        sys.executable,
        PYTHON_MEDIDOR,
        arquivo,
        str(k),
        algoritmo,
    ]

    if algoritmo == "quickselect":
        comando.append(pivo)

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True,
        check=True,
    )

    match = re.search(r"PICO_BYTES:\s*(\d+)", resultado.stdout)

    if not match:
        raise RuntimeError(
            "Não foi possível extrair a memória do Python:\n"
            + resultado.stdout
        )

    return int(match.group(1))


def medir_c(arquivo, k, algoritmo, pivo):
    saida_massif = os.path.join(
        PASTA_EXPERIMENTOS,
        "massif.out",
    )

    comando = [
        "valgrind",
        "--tool=massif",
        "--stacks=yes",
        f"--massif-out-file={saida_massif}",
        BIN_C,
        arquivo,
        str(k),
        algoritmo,
        "reps=1",
    ]

    if algoritmo == "quickselect":
        comando.append(f"pivo={pivo}")

    subprocess.run(
        comando,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    with open(saida_massif, "r") as f:
        conteudo = f.read()

    snapshots = re.findall(
        r"mem_stacks_B=(\d+)",
        conteudo,
    )

    if not snapshots:
        raise RuntimeError(
            "Não foi possível ler os dados de stack do Massif."
        )

    picos_stack = [int(stack) for stack in snapshots]

    return max(picos_stack)


def gerar_graficos():
    import matplotlib.pyplot as plt

    dados = {}

    with open(SAIDA_CSV, "r") as f:
        leitor = csv.DictReader(f)

        for linha in leitor:
            cenario = linha["cenario"]
            linguagem = linha["linguagem"]
            variante = linha["variante"]
            n = int(linha["n"])
            memoria = float(linha["memoria_kb"])

            chave = (cenario, linguagem, variante)

            dados.setdefault(chave, []).append((n, memoria))

    for cenario in TAMANHOS:

        # Gráfico separado para C.
        plt.figure()

        for (c, linguagem, variante), valores in dados.items():
            if c != cenario or linguagem != "c":
                continue

            valores.sort()

            x = [v[0] for v in valores]
            y = [v[1] for v in valores]

            plt.plot(
                x,
                y,
                marker="o",
                label=variante,
            )

        plt.title(f"Pico de stack - C - {cenario}")
        plt.xlabel("Tamanho da entrada (n)")
        plt.ylabel("Pico de stack (KB)")
        plt.legend()
        plt.grid(True)

        plt.savefig(
            os.path.join(
                PASTA_GRAFICOS,
                f"memoria_stack_c_{cenario}.png",
            )
        )

        plt.close()

        # Gráfico separado para Python.
        plt.figure()

        for (c, linguagem, variante), valores in dados.items():
            if c != cenario or linguagem != "python":
                continue

            valores.sort()

            x = [v[0] for v in valores]
            y = [v[1] for v in valores]

            plt.plot(
                x,
                y,
                marker="o",
                label=variante,
            )

        plt.title(
            f"Alocacoes adicionais rastreadas - Python - {cenario}"
        )
        plt.xlabel("Tamanho da entrada (n)")
        plt.ylabel("Pico adicional rastreado (KB)")
        plt.legend()
        plt.grid(True)

        plt.savefig(
            os.path.join(
                PASTA_GRAFICOS,
                f"memoria_python_{cenario}.png",
            )
        )

        plt.close()

    print("Gráficos de memória gerados.")


def main():
    if not os.path.exists(PYTHON_MEDIDOR):
        sys.exit("Arquivo memory_python.py não encontrado.")

    if not all(
        os.path.exists(caminho_entrada(cenario, n))
        for cenario, tamanhos in TAMANHOS.items()
        for n in tamanhos
    ):
        sys.exit(
            "Datasets ausentes. Rode primeiro "
            "python3 experiments/gerar_entradas.py"
        )

    if not os.path.exists("/usr/bin/valgrind"):
        sys.exit(
            "Valgrind não encontrado. "
            "Instale com sudo apt install valgrind."
        )

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    compilar_c()

    with open(SAIDA_CSV, "w", newline="") as arquivo_csv:
        escritor = csv.writer(arquivo_csv)

        escritor.writerow([
            "cenario",
            "linguagem",
            "variante",
            "n",
            "k",
            "tipo_medicao",
            "memoria_bytes",
            "memoria_kb",
        ])

        for cenario, tamanhos in TAMANHOS.items():
            for n in tamanhos:
                arquivo = caminho_entrada(cenario, n)
                k = (n + 1) // 2

                print(f"\n===== {cenario} | n={n} =====")

                for variante, (algoritmo, pivo) in VARIANTES.items():

                    for linguagem in ("c", "python"):

                        print(
                            f"Medindo {linguagem} - {variante}..."
                        )

                        if linguagem == "c":
                            memoria = medir_c(
                                arquivo,
                                k,
                                algoritmo,
                                pivo or "aleatorio",
                            )

                            tipo_medicao = "pico_stack_processo"

                        else:
                            memoria = medir_python(
                                arquivo,
                                k,
                                algoritmo,
                                pivo or "aleatorio",
                            )

                            tipo_medicao = (
                                "alocacoes_adicionais_rastreadas"
                            )

                        memoria_kb = memoria / 1024

                        escritor.writerow([
                            cenario,
                            linguagem,
                            variante,
                            n,
                            k,
                            tipo_medicao,
                            memoria,
                            f"{memoria_kb:.4f}",
                        ])

                        arquivo_csv.flush()

                        print(
                            f"Memoria: {memoria} bytes "
                            f"({memoria_kb:.2f} KB)"
                        )

    gerar_graficos()

    print("\nAnálise de memória concluída.")
    print(f"CSV salvo em: {SAIDA_CSV}")


if __name__ == "__main__":
    main()