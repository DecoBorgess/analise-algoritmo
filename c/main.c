/*
 * Uso: ./main <arquivo> <k> <quickselect|mom>
 *   k = posição desejada, 1-indexada (k=1 é o mínimo).
 * Saída (stdout): valor, tempo do algoritmo em segundos (sem a leitura).
 *
 * Formato do arquivo (binário, little-endian):
 *   [uint64 n][int64 a_0] ... [int64 a_{n-1}]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "median_of_medians.h"
#include "quickselect.h"

static i64 *ler_entrada(const char *path, size_t *n_out) {
    FILE *f = fopen(path, "rb");
    if (!f) { perror("fopen"); exit(1); }
    uint64_t n;
    if (fread(&n, sizeof n, 1, f) != 1) { fprintf(stderr, "cabeçalho inválido\n"); exit(1); }
    i64 *a = malloc(n * sizeof *a);
    if (!a && n) { fprintf(stderr, "sem memória para %llu elementos\n", (unsigned long long)n); exit(1); }
    if (fread(a, sizeof *a, n, f) != n) { fprintf(stderr, "arquivo truncado\n"); exit(1); }
    fclose(f);
    *n_out = n;
    return a;
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "uso: %s <arquivo> <k> <quickselect|mom>\n", argv[0]);
        return 2;
    }
    size_t n;
    i64 *a = ler_entrada(argv[1], &n);
    size_t k = strtoull(argv[2], NULL, 10);
    if (k < 1 || k > n) { fprintf(stderr, "k deve estar em [1, %zu]\n", n); return 2; }

    i64 (*algoritmo)(i64 *, size_t, size_t);
    if (strcmp(argv[3], "quickselect") == 0) algoritmo = quickselect;
    else if (strcmp(argv[3], "mom") == 0)    algoritmo = median_of_medians;
    else { fprintf(stderr, "algoritmo desconhecido: %s\n", argv[3]); return 2; }

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    i64 r = algoritmo(a, n, k - 1);
    clock_gettime(CLOCK_MONOTONIC, &t1);

    double dt = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;
    printf("%lld %.9f\n", (long long)r, dt);
    free(a);
    return 0;
}
