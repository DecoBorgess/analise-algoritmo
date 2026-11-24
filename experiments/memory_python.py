import struct
import sys
import random
import tracemalloc
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "python"))

from quickselect import quickselect
from median_of_medians import median_of_medians


def ler_entrada(path):
    with open(path, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))
        valores = list(struct.unpack(f"<{n}q", f.read(n * 8)))

    return valores


def medir_memoria(arquivo, k, algoritmo, pivo="aleatorio"):
    # Leitura e cópia do vetor ficam fora da medição.
    a = ler_entrada(arquivo)
    trabalho = a[:]

    random.seed(42)

    tracemalloc.start()

    # Baseline antes da chamada do algoritmo.
    baseline, _ = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()

    if algoritmo == "quickselect":
        resultado = quickselect(trabalho, k - 1, pivo)

    elif algoritmo == "mom":
        resultado = median_of_medians(trabalho, k - 1)

    else:
        tracemalloc.stop()
        raise ValueError("Algoritmo inválido.")

    _, pico = tracemalloc.get_traced_memory()

    # Pico adicional em relação ao baseline.
    memoria_adicional = max(0, pico - baseline)

    tracemalloc.stop()

    print(f"Valor encontrado: {resultado}")
    print(f"PICO_BYTES: {memoria_adicional}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(
            "Uso: python3 memory_python.py <arquivo> <k> "
            "<quickselect|mom> [pivo]"
        )

    arquivo = sys.argv[1]
    k = int(sys.argv[2])
    algoritmo = sys.argv[3]
    pivo = sys.argv[4] if len(sys.argv) > 4 else "aleatorio"

    medir_memoria(arquivo, k, algoritmo, pivo)