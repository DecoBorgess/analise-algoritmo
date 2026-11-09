#ifndef QUICKSELECT_H
#define QUICKSELECT_H

#include "common.h"

/* k-ésimo menor elemento (k 0-indexado). Reordena `a`. Pivô aleatório. */
i64 quickselect(i64 *a, size_t n, size_t k);

#endif
