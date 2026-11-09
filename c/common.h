#ifndef COMMON_H
#define COMMON_H

#include <stddef.h>
#include <stdint.h>

typedef int64_t i64;

static inline void swap(i64 *a, i64 *b) {
    i64 t = *a;
    *a = *b;
    *b = t;
}

/* Partição em 3 vias (menores | iguais | maiores) de a[lo..hi] (inclusivo)
 * em torno de `pivot`, que deve ser um valor presente no intervalo.
 * Devolve em *out_lt / *out_gt os limites da faixa de iguais. */
static inline void partition3(i64 *a, size_t lo, size_t hi, i64 pivot,
                              size_t *out_lt, size_t *out_gt) {
    size_t lt = lo, i = lo, gt = hi;
    while (i <= gt) {
        if (a[i] < pivot) {
            swap(&a[lt++], &a[i++]);
        } else if (a[i] > pivot) {
            swap(&a[i], &a[gt]);
            if (gt == 0) break;
            gt--;
        } else {
            i++;
        }
    }
    *out_lt = lt;
    *out_gt = gt;
}

/* Ordena a[lo..hi] (inclusivo); usado só em trechos minúsculos. */
static inline void insertion_sort(i64 *a, size_t lo, size_t hi) {
    for (size_t i = lo + 1; i <= hi; i++) {
        i64 key = a[i];
        size_t j = i;
        while (j > lo && a[j - 1] > key) {
            a[j] = a[j - 1];
            j--;
        }
        a[j] = key;
    }
}

#endif
