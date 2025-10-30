#include <stdint.h>

int64_t dot(int32_t n, const int32_t *a, const int32_t *b) {
    int64_t sum = 0;
    for (int32_t i = 0; i < n; i++) {
        sum += (int64_t)a[i] * (int64_t)b[i];
    }
    return sum;
}
