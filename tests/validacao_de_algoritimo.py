
"""Testa as implementações em C e Python contra sorted().

Uso (a partir da raiz do repositório):
python3 tests/validacao_de_algoritimo.py

Verifica se os algoritmos estão corretos e se produzem
o mesmo resultado nas duas linguagens para a mesma entrada.
"""

import os
import random
import struct
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp = tempfile.mkdtemp()
binario_c = os.path.join(tmp, "main")
entrada = os.path.join(tmp, "in.bin")

fontes = [
    os.path.join(RAIZ, "c", f)
    for f in ("main.c", "quickselect.c", "median_of_medians.c")
]

subprocess.run(
    ["cc", "-O2", "-Wall", "-o", binario_c, *fontes],
    check=True
)

programas = [
    [binario_c],
    [sys.executable, os.path.join(RAIZ, "python", "main.py")]
]

falhas = total = 0

for n in [1, 2, 3, 5, 6, 7, 10, 11, 100, 1001, 20000]:
    casos = {
        "aleatorio": [random.randint(-10**9, 10**9) for _ in range(n)],
        "duplicados": [random.randint(0, 3) for _ in range(n)],
        "iguais": [7] * n,
        "ordenado": list(range(n)),
        "reverso": list(range(n, 0, -1)),
    }

    for nome, v in casos.items():
        with open(entrada, "wb") as f:
            f.write(struct.pack("<Q", n))
            f.write(struct.pack(f"<{n}q", *v))

        esperado = sorted(v)

        for k in {1, n, (n + 1) // 2, random.randint(1, n)}:
            for alg, extras in (
                ("quickselect", ["pivo=aleatorio", "reps=2"]),
                ("quickselect", ["pivo=ultimo", "reps=2"]),
                ("mom", ["reps=2"]),
            ):
                for prog in programas:

                    if prog[0] == sys.executable and n > 1001:
                        continue

                    total += 1

                    saida = subprocess.run(
                        prog + [entrada, str(k), alg] + extras,
                        capture_output=True,
                        text=True
                    )

                    obtido = None

                    for linha in saida.stdout.splitlines():
                        if linha.startswith("Valor encontrado:"):
                            obtido = int(linha.split(":")[1].strip())
                            break

                    if saida.returncode != 0 or obtido != esperado[k - 1]:
                        falhas += 1
                        print(
                            f"FALHA {nome} n={n} k={k} "
                            f"{alg} {extras} {prog[0]}: "
                            f"{obtido} != {esperado[k - 1]}"
                        )

                        if saida.stderr:
                            print("Erro:", saida.stderr)

print(f"{total - falhas}/{total} testes passaram")

sys.exit(1 if falhas else 0)
