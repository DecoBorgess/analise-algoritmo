#ifndef QUICKSELECT_H
#define QUICKSELECT_H

#include "common.h"

/* Escolha do pivô.
 *   PIVO_ALEATORIO: elemento sorteado em [lo, hi]  -> O(n) esperado.
 *   PIVO_ULTIMO:    sempre a[hi] (pivô fixo)       -> O(n²) em entrada
 *                   crescente (pior caso forçado). */
typedef enum { PIVO_ALEATORIO, PIVO_ULTIMO } pivo_modo_t;

/* k-ésimo menor elemento (k 0-indexado). Reordena `a`. */
i64 quickselect(i64 *a, size_t n, size_t k, pivo_modo_t modo);

#endif
