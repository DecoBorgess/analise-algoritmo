import random

from common import particao3

PIVOS = ("aleatorio", "ultimo")


def quickselect(a, k, pivo="aleatorio"):
    """k-ésimo menor (k 0-indexado). Reordena `a`.

    pivo="aleatorio": elemento sorteado em [lo, hi]  -> O(n) esperado.
    pivo="ultimo":    sempre a[hi] (pivô fixo)       -> O(n²) em entrada
                      crescente (pior caso forçado).
    """
    if pivo not in PIVOS:
        raise ValueError(f"pivo deve ser um de {PIVOS}")
    ultimo = pivo == "ultimo"
    lo, hi = 0, len(a) - 1
    while True:
        if lo == hi:
            return a[lo]
        p = a[hi] if ultimo else a[random.randint(lo, hi)]
        lt, gt = particao3(a, lo, hi, p)
        if k < lt:
            hi = lt - 1
        elif k > gt:
            lo = gt + 1
        else:
            return p
