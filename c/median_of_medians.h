#ifndef MEDIAN_OF_MEDIANS_H
#define MEDIAN_OF_MEDIANS_H

#include "common.h"

/* k-ésimo menor elemento (k 0-indexado). Reordena `a`. Pior caso O(n). */
i64 median_of_medians(i64 *a, size_t n, size_t k);

#endif
