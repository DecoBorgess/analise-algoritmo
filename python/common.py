"""Funções auxiliares compartilhadas pelos dois algoritmos."""


def particao3(a, lo, hi, pivo):
    """Partição em 3 vias (menores | iguais | maiores) de a[lo..hi] (inclusivo).

    `pivo` deve ser um valor presente no intervalo. Devolve (lt, gt), os
    limites da faixa de iguais.
    """
    lt, i, gt = lo, lo, hi
    while i <= gt:
        x = a[i]
        if x < pivo:
            a[lt], a[i] = x, a[lt]
            lt += 1
            i += 1
        elif x > pivo:
            a[i], a[gt] = a[gt], x
            gt -= 1
        else:
            i += 1
    return lt, gt


def insertion_sort(a, lo, hi):
    """Ordena a[lo..hi] (inclusivo); usado só em trechos minúsculos."""
    for i in range(lo + 1, hi + 1):
        key = a[i]
        j = i
        while j > lo and a[j - 1] > key:
            a[j] = a[j - 1]
            j -= 1
        a[j] = key
