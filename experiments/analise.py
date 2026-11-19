"""
Resumo estatístico e gráficos a partir de experiments/results.csv.

Uso (da raiz do repositório): python3 experiments/analise.py

Gera:
  experiments/summary.csv   média, desvio-padrão (amostral) e razões T/n, T/n²
  graphs/1_caso_medio.png          tempo x n, entrada aleatória (log-log)
  graphs/2_melhor_caso.png         tempo x n, entrada de elementos iguais
  graphs/3_pior_caso.png           tempo x n, entrada crescente
  graphs/4_razao_caso_medio.png    T(n)/n na entrada aleatória
  graphs/5_razao_pior_caso.png     T(n)/n² (quickselect pivô fixo) e T(n)/n
                                   (demais) na entrada crescente

A legenda dos gráficos 1-3 traz a inclinação medida em log-log
(≈1 => linear, ≈2 => quadrático). As barras de erro são ±1 desvio-padrão.
"""
import csv
import os
from collections import defaultdict
from statistics import mean, stdev

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import PASTA_EXPERIMENTOS, PASTA_GRAFICOS

ENTRADA = os.path.join(PASTA_EXPERIMENTOS, "results.csv")
RESUMO = os.path.join(PASTA_EXPERIMENTOS, "summary.csv")

CORES = {"quickselect-aleatorio": "tab:blue", "quickselect-ultimo": "tab:red", "mom": "tab:green"}
ESTILOS = {"c": ("-", "o"), "python": ("--", "s")}
NOMES = {"c": "C", "python": "Python"}

TITULOS = {
    "aleatorio": "Caso médio (entrada aleatória)",
    "iguais": "Melhor caso do quickselect (elementos iguais)",
    "crescente": "Pior caso do quickselect com pivô fixo (entrada crescente)",
}


def ler_resumo():
    """(cenario, linguagem, variante) -> lista de (n, media, desvio, reps) por n."""
    tempos = defaultdict(list)
    with open(ENTRADA, newline="") as f:
        for linha in csv.DictReader(f):
            chave = (linha["cenario"], linha["linguagem"], linha["variante"], int(linha["n"]))
            tempos[chave].append(float(linha["tempo_s"]))

    resumo = defaultdict(list)
    for (cenario, lang, variante, n), ts in sorted(tempos.items()):
        desvio = stdev(ts) if len(ts) > 1 else 0.0
        resumo[(cenario, lang, variante)].append((n, mean(ts), desvio, len(ts)))
    return resumo


def gravar_resumo(resumo):
    with open(RESUMO, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cenario", "linguagem", "variante", "n", "repeticoes",
                    "media_s", "desvio_s", "media_sobre_n", "media_sobre_n2"])
        for (cenario, lang, variante), pontos in resumo.items():
            for n, media, desvio, reps in pontos:
                w.writerow([cenario, lang, variante, n, reps,
                            f"{media:.9f}", f"{desvio:.9f}", f"{media / n:.6e}", f"{media / n**2:.6e}"])


def inclinacao(pontos):
    """Inclinação da reta ajustada em log-log (expoente medido)."""
    ns = np.log([p[0] for p in pontos])
    ts = np.log([p[1] for p in pontos])
    return np.polyfit(ns, ts, 1)[0]


def desenhar(ax, resumo, cenario, variantes=None, razao=None, legenda_inclinacao=False):
    """Desenha as curvas de um cenário. razao: None (tempo), 1 (T/n) ou 2 (T/n²)."""
    for (cen, lang, variante), pontos in resumo.items():
        if cen != cenario or (variantes and variante not in variantes):
            continue
        estilo, marcador = ESTILOS[lang]
        ns = [p[0] for p in pontos]
        medias = [p[1] / (p[0] ** razao if razao else 1) for p in pontos]
        desvios = [p[2] / (p[0] ** razao if razao else 1) for p in pontos]
        rotulo = f"{NOMES[lang]} - {variante}"
        if legenda_inclinacao:
            rotulo += f" (inclinação {inclinacao(pontos):.2f})"
        ax.errorbar(ns, medias, yerr=desvios, color=CORES[variante], linestyle=estilo,
                    marker=marcador, capsize=3, label=rotulo)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Quantidade de elementos (n)")
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend(fontsize=8)


def salvar(fig, nome):
    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    caminho = os.path.join(PASTA_GRAFICOS, nome)
    fig.tight_layout()
    fig.savefig(caminho, dpi=200)
    plt.close(fig)
    print(f"Grafico criado: {os.path.relpath(caminho)}")


def main():
    resumo = ler_resumo()
    gravar_resumo(resumo)
    print(f"Resumo criado: {os.path.relpath(RESUMO)}")

    # 1-3: tempo x n por cenário
    for numero, nome, cenario in [(1, "caso_medio", "aleatorio"), (2, "melhor_caso", "iguais"),
                                  (3, "pior_caso", "crescente")]:
        fig, ax = plt.subplots(figsize=(9, 6))
        desenhar(ax, resumo, cenario, legenda_inclinacao=True)
        ax.set_title(TITULOS[cenario])
        ax.set_ylabel("Tempo médio (s)")
        salvar(fig, f"{numero}_{nome}.png")

    # 4: T(n)/n no caso médio (deve tender a constante: O(n))
    fig, ax = plt.subplots(figsize=(9, 6))
    desenhar(ax, resumo, "aleatorio", razao=1)
    ax.set_title("Razão T(n)/n - caso médio (constante => O(n))")
    ax.set_ylabel("T(n) / n  (s por elemento)")
    salvar(fig, "4_razao_caso_medio.png")

    # 5: pior caso. Quickselect pivô fixo: T/n² constante; os demais: T/n constante.
    fig, (esq, dir) = plt.subplots(1, 2, figsize=(14, 6))
    desenhar(esq, resumo, "crescente", variantes=["quickselect-ultimo"], razao=2)
    esq.set_title("Quickselect pivô fixo: T(n)/n² (constante => O(n²))")
    esq.set_ylabel("T(n) / n²")
    desenhar(dir, resumo, "crescente", variantes=["quickselect-aleatorio", "mom"], razao=1)
    dir.set_title("Pivô aleatório e mediana das medianas: T(n)/n (constante => O(n))")
    dir.set_ylabel("T(n) / n")
    salvar(fig, "5_razao_pior_caso.png")


if __name__ == "__main__":
    main()
