"""Testa as implementações em C e Python contra sorted().

Uso (a partir da raiz do repositório): python3 tests/teste.py

seve apenas para ver se os algoritimos estão corretos e se estão dando o mesmo resultado nas liguagens diferentes para a mesma entrada

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

fontes = [os.path.join(RAIZ, "c", f) for f in ("main.c", "quickselect.c", "median_of_medians.c")]
subprocess.run(["cc", "-O2", "-Wall", "-o", binario_c, *fontes], check=True)
programas = [[binario_c], [sys.executable, os.path.join(RAIZ, "python", "main.py")]]

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
            for alg in ("quickselect", "mom"):
                for prog in programas:
                    if prog[0] == sys.executable and n > 1001:
                        continue  # Python puro é lento; evita demorar
                    total += 1
                    saida = subprocess.run(prog + [entrada, str(k), alg], capture_output=True, text=True)
                    obtido = int(saida.stdout.split()[0]) if saida.stdout else None
                    if obtido != esperado[k - 1]:
                        falhas += 1
                        print(f"FALHA {nome} n={n} k={k} {alg} {prog[0]}: {obtido} != {esperado[k-1]}")

print(f"{total - falhas}/{total} testes passaram")
sys.exit(1 if falhas else 0)
