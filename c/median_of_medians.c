#include "median_of_medians.h"

static i64 mom_select(i64 *a, size_t lo, size_t hi, size_t k);

/* Pivô: mediana das medianas de grupos de 5 em a[lo..hi]. */
static i64 mom_pivot(i64 *a, size_t lo, size_t hi) {
    size_t m = 0; /* quantidade de grupos */
    for (size_t g = lo; g <= hi; g += 5) {
        size_t end = (g + 4 < hi) ? g + 4 : hi;
        insertion_sort(a, g, end);
        swap(&a[lo + m], &a[g + (end - g) / 2]); /* mediana do grupo -> frente */
        m++;
    }
    if (m == 1) return a[lo];
    return mom_select(a, lo, lo + m - 1, lo + (m - 1) / 2);
}

/* k é índice absoluto em [lo, hi]. */
static i64 mom_select(i64 *a, size_t lo, size_t hi, size_t k) {
    for (;;) {
        if (hi - lo < 5) {
            insertion_sort(a, lo, hi);
            return a[k];
        }
        i64 pivot = mom_pivot(a, lo, hi);
        size_t lt, gt;
        partition3(a, lo, hi, pivot, &lt, &gt);
        if (k < lt)       hi = lt - 1;
        else if (k > gt)  lo = gt + 1;
        else              return pivot;
    }
}

i64 median_of_medians(i64 *a, size_t n, size_t k) {
    return mom_select(a, 0, n - 1, k);
}
