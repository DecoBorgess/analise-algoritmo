#include "quickselect.h"

static uint64_t rng_state = 88172645463325252ULL;

static inline uint64_t xorshift64(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return rng_state;
}

i64 quickselect(i64 *a, size_t n, size_t k) {
    size_t lo = 0, hi = n - 1;
    for (;;) {
        if (lo == hi) return a[lo];
        i64 pivot = a[lo + xorshift64() % (hi - lo + 1)];
        size_t lt, gt;
        partition3(a, lo, hi, pivot, &lt, &gt);
        if (k < lt)       hi = lt - 1;
        else if (k > gt)  lo = gt + 1;
        else              return pivot;
    }
}
