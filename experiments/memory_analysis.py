"""Análise experimental de memória (espaço auxiliar) dos algoritmos.

Uso (da raiz do repositório):
  python3 experiments/memory_analysis.py            # mede C e Python (lento)
  python3 experiments/memory_analysis.py --so-c     # remede só C, mantém Python

Método
  C       binário c/main_mem (compilado com -DMEM_TRACK). Pilha por "pintura":
          64 KB abaixo do topo da pilha são preenchidos com um padrão antes de
          chamar o algoritmo; os bytes alterados depois são o pico de pilha
          (resolução de 8 B). Também conta a profundidade máxima de recursão.
          Heap: confirmado via `nm -u` que os objetos dos algoritmos não
          referenciam malloc/calloc/realloc (heap auxiliar = 0). O vetor de
          entrada (n * 8 B) pertence ao chamador e não é contado.
  Python  tracemalloc: pico de alocações adicionais durante a chamada, em
          relação ao baseline (vetor de entrada fica fora da medição).

Gera experiments/memory_results.csv, experiments/memory_summary.csv (ajustes
de tendência) e graphs/memoria_{stack_c,python}_<cenario>.png.
"""
import csv
import math
import os
import re
import subprocess
import sys

from config import (
    RAIZ,
    PASTA_EXPERIMENTOS,
    PASTA_GRAFICOS,
    TAMANHOS,
    VARIANTES,
    caminho_entrada,
)

BIN_MEM = os.path.join(RAIZ, "c", "main_mem")
BIN_TEMPO = os.path.join(RAIZ, "c", "main")
FONTES_C = [os.path.join(RAIZ, "c", f) for f in ("main.c", "quickselect.c", "median_of_medians.c")]
PYTHON_MEDIDOR = os.path.join(PASTA_EXPERIMENTOS, "memory_python.py")
SAIDA_CSV = os.path.join(PASTA_EXPERIMENTOS, "memory_results.csv")
SAIDA_RESUMO = os.path.join(PASTA_EXPERIMENTOS, "memory_summary.csv")
CAMPOS = ["cenario", "linguagem", "variante", "n", "k", "tipo_medicao",
          "memoria_bytes", "memoria_kb", "profundidade"]
FLAGS = ["-O2", "-std=c11", "-D_POSIX_C_SOURCE=200809L", "-Wall"]


def compilar_c():
    print("Compilando C (tempo e memória)...")
    subprocess.run(["gcc", *FLAGS, *FONTES_C, "-o", BIN_TEMPO], check=True)
    subprocess.run(["gcc", *FLAGS, "-DMEM_TRACK", *FONTES_C, "-o", BIN_MEM], check=True)


def verificar_sem_heap():
    """Os algoritmos não podem alocar: nenhuma referência a malloc & cia."""
    for nome in ("quickselect", "median_of_medians"):
        obj = os.path.join(PASTA_EXPERIMENTOS, f"_{nome}.o")
        subprocess.run(["gcc", "-O2", "-std=c11", "-c",
                        os.path.join(RAIZ, "c", f"{nome}.c"), "-o", obj], check=True)
        saida = subprocess.run(["nm", "-u", obj], capture_output=True, text=True, check=True).stdout
        os.remove(obj)
        if re.search(r"\b(malloc|calloc|realloc|free)\b", saida):
            sys.exit(f"{nome}.c referencia alocação dinâmica:\n{saida}")
    print("Heap auxiliar dos algoritmos: 0 B (nenhuma chamada a malloc/calloc/realloc).")


def medir_c(arquivo, k, algoritmo, pivo):
    cmd = [BIN_MEM, arquivo, str(k), algoritmo, "reps=1"]
    if algoritmo == "quickselect":
        cmd.append(f"pivo={pivo}")
    saida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    pilha = re.search(r"PILHA_BYTES:\s*(\d+)", saida)
    prof = re.search(r"PROFUNDIDADE:\s*(\d+)", saida)
    if not pilha or not prof:
        raise RuntimeError("Saída sem PILHA_BYTES/PROFUNDIDADE:\n" + saida)
    return int(pilha.group(1)), int(prof.group(1))


def medir_python(arquivo, k, algoritmo, pivo):
    cmd = [sys.executable, PYTHON_MEDIDOR, arquivo, str(k), algoritmo]
    if algoritmo == "quickselect":
        cmd.append(pivo)
    saida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    m = re.search(r"PICO_BYTES:\s*(\d+)", saida)
    if not m:
        raise RuntimeError("Sem PICO_BYTES:\n" + saida)
    return int(m.group(1))


def linha(cen, lg, var, n, k, tipo, b, prof=""):
    return [cen, lg, var, n, k, tipo, b, f"{b / 1024:.4f}", prof]


def ler_python_existente():
    if not os.path.exists(SAIDA_CSV):
        sys.exit("--so-c exige um memory_results.csv anterior com as linhas de Python.")
    with open(SAIDA_CSV, newline="") as f:
        linhas = [r for r in csv.DictReader(f) if r["linguagem"] == "python"]
    return {(r["cenario"], r["variante"], int(r["n"])): r for r in linhas}


def coletar(so_c):
    py_antigo = ler_python_existente() if so_c else {}
    linhas = []
    for cenario, tamanhos in TAMANHOS.items():
        for n in tamanhos:
            arquivo, k = caminho_entrada(cenario, n), (n + 1) // 2
            print(f"===== {cenario} | n={n} =====")
            for variante, (alg, pivo) in VARIANTES.items():
                b, prof = medir_c(arquivo, k, alg, pivo or "aleatorio")
                linhas.append(linha(cenario, "c", variante, n, k, "pico_pilha_pintura", b, prof))
                print(f"  c      {variante:22s} {b:6d} B  prof={prof}")
                if so_c:
                    r = py_antigo[(cenario, variante, n)]
                    linhas.append([r.get(c, "") for c in CAMPOS])
                    continue
                b = medir_python(arquivo, k, alg, pivo or "aleatorio")
                linhas.append(linha(cenario, "python", variante, n, k,
                                    "alocacoes_adicionais_rastreadas", b))
                print(f"  python {variante:22s} {b:6d} B")
    return linhas


def regressao(xs, ys):
    """Mínimos quadrados y = a + b x; devolve (a, b, R²)."""
    m = len(xs)
    mx, my = sum(xs) / m, sum(ys) / m
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx if sxx else 0.0
    a = my - b * mx
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    return a, b, (1 - sse / sst) if sst else 1.0


def carregar():
    dados = {}
    with open(SAIDA_CSV, newline="") as f:
        for r in csv.DictReader(f):
            chave = (r["cenario"], r["linguagem"], r["variante"])
            dados.setdefault(chave, []).append((int(r["n"]), int(r["memoria_bytes"])))
    for v in dados.values():
        v.sort()
    return dados


def resumo(dados):
    """Para cada série: memória ~ a + b*log2(n) e ~ a + b*n (R² de cada)."""
    with open(SAIDA_RESUMO, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cenario", "linguagem", "variante", "min_bytes", "max_bytes",
                    "b_por_log2n", "r2_log2n", "b_por_n", "r2_n"])
        for (cen, lg, var), pts in dados.items():
            ns, ms = [p[0] for p in pts], [p[1] for p in pts]
            _, b_log, r_log = regressao([math.log2(n) for n in ns], ms)
            _, b_lin, r_lin = regressao(ns, ms)
            w.writerow([cen, lg, var, min(ms), max(ms),
                        f"{b_log:.3f}", f"{r_log:.3f}", f"{b_lin:.3e}", f"{r_lin:.3f}"])
    print(f"Resumo: {SAIDA_RESUMO}")


def graficos(dados):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cfg = {
        "c": ("memoria_stack_c_{}.png", "Pico de pilha (B)", "Pilha auxiliar - C - {}"),
        "python": ("memoria_python_{}.png", "Pico adicional rastreado (B)",
                   "Alocações auxiliares (tracemalloc) - Python - {}"),
    }
    cores = {"quickselect-aleatorio": "tab:blue", "quickselect-ultimo": "tab:red", "mom": "tab:green"}
    for cenario in TAMANHOS:
        for lg, (arq, ylabel, titulo) in cfg.items():
            plt.figure(figsize=(7, 4.5))
            for (c, l, var), pts in dados.items():
                if c != cenario or l != lg:
                    continue
                ns, ms = [p[0] for p in pts], [p[1] for p in pts]
                plt.plot(ns, ms, marker="o", color=cores[var], label=var)
                if var == "mom":  # curva teórica a + b*log2(n) ajustada
                    a, b, r2 = regressao([math.log2(n) for n in ns], ms)
                    plt.plot(ns, [a + b * math.log2(n) for n in ns], "k--", lw=1,
                             label=f"ajuste a+b·log₂n (R²={r2:.2f})")
            plt.xscale("log")
            plt.ylim(bottom=0)
            plt.title(titulo.format(cenario))
            plt.xlabel("Tamanho da entrada n (escala log)")
            plt.ylabel(ylabel)
            plt.grid(True, which="both", alpha=0.3)
            plt.legend(fontsize=8)
            plt.tight_layout()
            plt.savefig(os.path.join(PASTA_GRAFICOS, arq.format(cenario)), dpi=130)
            plt.close()
    print("Gráficos de memória gerados.")


def main():
    so_c = "--so-c" in sys.argv
    if not all(os.path.exists(caminho_entrada(c, n)) for c, ns in TAMANHOS.items() for n in ns):
        sys.exit("Datasets ausentes. Rode primeiro python3 experiments/gerar_entradas.py")
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    compilar_c()
    verificar_sem_heap()
    linhas = coletar(so_c)
    with open(SAIDA_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(CAMPOS)
        w.writerows(linhas)
    dados = carregar()
    resumo(dados)
    graficos(dados)
    print(f"CSV: {SAIDA_CSV}")


if __name__ == "__main__":
    main()