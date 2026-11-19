"""Configuração compartilhada por gerar_entradas.py, benchmark.py e analise.py.

Cenários de entrada (sempre com k = mediana):
  aleatorio  caso médio dos dois algoritmos.
  iguais     melhor caso do quickselect: com partição em 3 vias, uma única
             passada já encontra o k-ésimo (O(n)).
  crescente  pior caso do quickselect com pivô fixo no último elemento: o
             pivô é sempre o máximo do intervalo e cada passada descarta só
             1 elemento (O(n²)). A mediana das medianas é Θ(n) em qualquer
             entrada.

Os tamanhos seguem progressão geométrica (6 por cenário). O cenário crescente
é menor porque o pior caso quadrático em Python leva dezenas de segundos.
"""
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DATASETS = os.path.join(RAIZ, "datasets")
PASTA_EXPERIMENTOS = os.path.join(RAIZ, "experiments")
PASTA_GRAFICOS = os.path.join(RAIZ, "graphs")

SEMENTE = 42
REPETICOES = 20

TAMANHOS = {
    "aleatorio": [1000 * 4**i for i in range(6)],  # 1 mil .. 1,024 milhão (razão 4)
    "iguais": [1000 * 4**i for i in range(6)],
    "crescente": [1000 * 2**i for i in range(6)],  # 1 mil .. 32 mil (razão 2)
}

# variante -> (algoritmo, pivô); o pivô só vale para o quickselect
VARIANTES = {
    "quickselect-aleatorio": ("quickselect", "aleatorio"),
    "quickselect-ultimo": ("quickselect", "ultimo"),
    "mom": ("mom", None),
}


def caminho_entrada(cenario, n):
    return os.path.join(PASTA_DATASETS, f"{cenario}_{n}.bin")
