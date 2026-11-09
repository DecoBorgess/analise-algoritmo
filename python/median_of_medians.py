from common import insertion_sort, particao3


def _mom_pivo(a, lo, hi):
    """Mediana das medianas de grupos de 5 em a[lo..hi]."""
    m = 0
    for g in range(lo, hi + 1, 5):
        fim = min(g + 4, hi)
        insertion_sort(a, g, fim)
        meio = g + (fim - g) // 2
        a[lo + m], a[meio] = a[meio], a[lo + m]  # mediana do grupo -> frente
        m += 1
    if m == 1:
        return a[lo]
    return _mom_select(a, lo, lo + m - 1, lo + (m - 1) // 2)


def _mom_select(a, lo, hi, k):
    """k é índice absoluto em [lo, hi]."""
    while True:
        if hi - lo < 5:
            insertion_sort(a, lo, hi)
            return a[k]
        pivo = _mom_pivo(a, lo, hi)
        lt, gt = particao3(a, lo, hi, pivo)
        if k < lt:
            hi = lt - 1
        elif k > gt:
            lo = gt + 1
        else:
            return pivo


def median_of_medians(a, k):
    """k-ésimo menor (k 0-indexado), pior caso O(n). Reordena `a`."""
    return _mom_select(a, 0, len(a) - 1, k)
