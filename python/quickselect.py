import random

from common import particao3


def quickselect(a, k):
    """k-ésimo menor (k 0-indexado). Reordena `a`. Pivô aleatório."""
    lo, hi = 0, len(a) - 1
    while True:
        if lo == hi:
            return a[lo]
        pivo = a[random.randint(lo, hi)]
        lt, gt = particao3(a, lo, hi, pivo)
        if k < lt:
            hi = lt - 1
        elif k > gt:
            lo = gt + 1
        else:
            return pivo
