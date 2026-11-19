/*
 * Uso: ./main <arquivo> <k> <quickselect|mom> [pivo=aleatorio|ultimo] [reps=N]
 *
 *   k      posição desejada, 1-indexada (k=1 é o mínimo).
 *   pivo   só para quickselect; padrão: aleatorio.
 *   reps   número de execuções do algoritmo, cada uma sobre uma cópia do
 *          vetor lido (padrão: 1). O arquivo é lido uma única vez.
 *
 * Saída: valor encontrado e tempos do algoritmo em segundos
 * (sem incluir a leitura do arquivo nem a cópia do vetor).
 *
 * Formato do arquivo (binário, little-endian):
 * [uint64 n][int64 a_0] ... [int64 a_(n-1)]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "median_of_medians.h"
#include "quickselect.h"

static i64 *ler_entrada(const char *path, size_t *n_out) {
    FILE *f = fopen(path, "rb");

    if (!f) {
        perror("fopen");
        exit(1);
    }

    uint64_t n;

    if (fread(&n, sizeof n, 1, f) != 1) {
        fprintf(stderr, "cabeçalho inválido\n");
        exit(1);
    }

    i64 *a = malloc(n * sizeof *a);

    if (!a && n) {
        fprintf(stderr, "sem memória para %llu elementos\n",
                (unsigned long long)n);
        exit(1);
    }

    if (fread(a, sizeof *a, n, f) != n) {
        fprintf(stderr, "arquivo truncado\n");
        exit(1);
    }

    fclose(f);

    *n_out = n;
    return a;
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr,
                "uso: %s <arquivo> <k> <quickselect|mom> "
                "[pivo=aleatorio|ultimo] [reps=N]\n",
                argv[0]);
        return 2;
    }

    int usa_mom;

    if (strcmp(argv[3], "quickselect") == 0) {
        usa_mom = 0;
    }
    else if (strcmp(argv[3], "mom") == 0) {
        usa_mom = 1;
    }
    else {
        fprintf(stderr, "algoritmo desconhecido: %s\n", argv[3]);
        return 2;
    }

    pivo_modo_t modo = PIVO_ALEATORIO;
    int pivo_informado = 0;
    size_t reps = 1;

    for (int i = 4; i < argc; i++) {
        if (strncmp(argv[i], "pivo=", 5) == 0) {
            const char *valor = argv[i] + 5;

            if (strcmp(valor, "aleatorio") == 0)   modo = PIVO_ALEATORIO;
            else if (strcmp(valor, "ultimo") == 0) modo = PIVO_ULTIMO;
            else {
                fprintf(stderr, "pivo deve ser aleatorio ou ultimo\n");
                return 2;
            }
            pivo_informado = 1;
        }
        else if (strncmp(argv[i], "reps=", 5) == 0) {
            reps = strtoull(argv[i] + 5, NULL, 10);

            if (reps < 1) {
                fprintf(stderr, "reps deve ser >= 1\n");
                return 2;
            }
        }
        else {
            fprintf(stderr, "opcao desconhecida: %s\n", argv[i]);
            return 2;
        }
    }

    if (pivo_informado && usa_mom) {
        fprintf(stderr, "pivo= so se aplica ao quickselect\n");
        return 2;
    }

    size_t n;
    i64 *a = ler_entrada(argv[1], &n);

    size_t k = strtoull(argv[2], NULL, 10);

    if (k < 1 || k > n) {
        fprintf(stderr, "k deve estar em [1, %zu]\n", n);
        free(a);
        return 2;
    }

    i64 *trabalho = malloc(n * sizeof *trabalho);
    double *tempos = malloc(reps * sizeof *tempos);

    if (!trabalho || !tempos) {
        fprintf(stderr, "sem memória\n");
        return 1;
    }

    i64 r = 0;
    double soma = 0;

    for (size_t rep = 0; rep < reps; rep++) {
        memcpy(trabalho, a, n * sizeof *a);

        struct timespec t0, t1;

        clock_gettime(CLOCK_MONOTONIC, &t0);
        i64 atual = usa_mom ? median_of_medians(trabalho, n, k - 1)
                            : quickselect(trabalho, n, k - 1, modo);
        clock_gettime(CLOCK_MONOTONIC, &t1);

        if (rep == 0) {
            r = atual;
        }
        else if (atual != r) {
            fprintf(stderr, "resultado diferente entre repeticoes\n");
            return 3;
        }

        tempos[rep] = (t1.tv_sec - t0.tv_sec)
                    + (t1.tv_nsec - t0.tv_nsec) / 1e9;
        soma += tempos[rep];
    }

    printf("\n========== RESULTADO ==========\n");
    printf("Algoritmo: %s\n", usa_mom ? "Median of Medians" : "Quickselect");

    if (!usa_mom) {
        printf("Pivo: %s\n", modo == PIVO_ULTIMO ? "ultimo" : "aleatorio");
    }

    printf("Quantidade de elementos: %zu\n", n);
    printf("Posicao procurada (k): %zu\n", k);
    printf("Valor encontrado: %lld\n", (long long)r);
    printf("Repeticoes: %zu\n", reps);
    printf("Tempo de execucao: %.9f segundos\n", soma / reps);
    printf("Tempos (s):");

    for (size_t rep = 0; rep < reps; rep++) {
        printf(" %.9f", tempos[rep]);
    }

    printf("\n================================\n");

    free(a);
    free(trabalho);
    free(tempos);

    return 0;
}
