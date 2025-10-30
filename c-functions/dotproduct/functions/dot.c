#include <stdint.h>


int64_t dot(int32_t n, const int32_t *a, const int32_t *b) {
    int64_t sum = 0;
    for (int32_t i = 0; i < n; i++) {
        sum += (int64_t)a[i] * (int64_t)b[i];
    }
    return sum;
}


int64_t sparse_dot(int32_t n_a, const int32_t *idx_a, const int32_t *val_a,
                   int32_t n_b, const int32_t *idx_b, const int32_t *val_b)
{
    int64_t sum = 0;
    int32_t i = 0, j = 0;
    while (i < n_a && j < n_b) {
        if (idx_a[i] == idx_b[j]) {
            sum += (int64_t)val_a[i] * (int64_t)val_b[j];
            i++;
            j++;
        } else if (idx_a[i] < idx_b[j]) {
            i++;
        } else {
            j++;
        }
    }
    return sum;
}
