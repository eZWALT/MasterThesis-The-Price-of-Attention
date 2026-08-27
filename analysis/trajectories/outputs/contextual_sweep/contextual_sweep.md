# Contextual labelling sweep

Hard labels only. Same crossing estimand as family A.
``bare`` and ``deployed`` are the Gold readings. The other four are
new ThradBERT passes. Holm-within is the four contrasts inside a
recipe. Holm-across is the six early-pooled p-values, the thing a
reader would harvest.

| recipe    |   distinct_genres |   mean_n_shift |   share_sticky |   crossing_delta |    p_t |   p_holm_within |   mcnemar_only_t |   mcnemar_only_c |   p_mcnemar |   delta_tilde |   tilde_chance |   p_tilde |   already_in_ad_genre |   p_holm_across_recipes |
|:----------|------------------:|---------------:|---------------:|-----------------:|-------:|----------------:|-----------------:|-----------------:|------------:|--------------:|---------------:|----------:|----------------------:|------------------------:|
| bare      |                13 |         2.4519 |         0.0259 |           0.0463 | 0.471  |          0.9419 |               11 |                6 |      0.3323 |             9 |        10.4527 |    0.79   |                    25 |                  1      |
| deployed  |                 7 |         0.3963 |         0.7    |          -0.0185 | 0.7551 |          1      |                5 |                6 |      1      |             2 |         3.7205 |    0.965  |                    53 |                  1      |
| no_task   |                12 |         0.937  |         0.3778 |           0.0093 | 0.9027 |          1      |               11 |                8 |      0.6476 |             7 |         8.6635 |    0.8762 |                    34 |                  1      |
| prev_only |                13 |         1.5889 |         0.1    |          -0.1389 | 0.0959 |          0.3835 |               10 |               17 |      0.2478 |             9 |        10.4652 |    0.8049 |                    34 |                  0.5753 |
| task_only |                 5 |         0.5037 |         0.6778 |          -0.0185 | 0.7551 |          1      |                6 |                9 |      0.6072 |             3 |         4.165  |    0.8839 |                    46 |                  1      |
| opening   |                12 |         1.2778 |         0.3667 |          -0.0556 | 0.4512 |          1      |               12 |               13 |      1      |            10 |        11.7156 |    0.8374 |                    34 |                  1      |

## Crossing δ, every contrast

| recipe    | contrast                        |   n |    mean |   ci_low |   ci_high |      dz |    p_t |   p_wilcoxon |   p_holm |
|:----------|:--------------------------------|----:|--------:|---------:|----------:|--------:|-------:|-------------:|---------:|
| bare      | early ads pooled - no ad        |  54 |  0.0463 |  -0.0816 |    0.1742 |  0.0988 | 0.471  |       0.3429 |   0.9419 |
| bare      | implicit early - no ad          |  54 |  0.0926 |  -0.0599 |    0.2451 |  0.1658 | 0.2286 |       0.2253 |   0.9143 |
| bare      | explicit early - no ad          |  54 |  0      |  -0.15   |    0.15   |  0      | 1      |       1      |   1      |
| bare      | implicit early - explicit early |  54 |  0.0926 |  -0.0688 |    0.254  |  0.1566 | 0.2551 |       0.2513 |   0.9143 |
| deployed  | early ads pooled - no ad        |  54 | -0.0185 |  -0.137  |    0.0999 | -0.0427 | 0.7551 |       0.5592 |   1      |
| deployed  | implicit early - no ad          |  54 | -0.0185 |  -0.1428 |    0.1057 | -0.0407 | 0.7661 |       0.763  |   1      |
| deployed  | explicit early - no ad          |  54 | -0.0185 |  -0.1636 |    0.1266 | -0.0348 | 0.799  |       0.7963 |   1      |
| deployed  | implicit early - explicit early |  54 |  0      |  -0.1299 |    0.1299 |  0      | 1      |       1      |   1      |
| no_task   | early ads pooled - no ad        |  54 |  0.0093 |  -0.1419 |    0.1604 |  0.0167 | 0.9027 |       0.8916 |   1      |
| no_task   | implicit early - no ad          |  54 |  0.0556 |  -0.1072 |    0.2183 |  0.0932 | 0.4964 |       0.4913 |   1      |
| no_task   | explicit early - no ad          |  54 | -0.037  |  -0.2204 |    0.1464 | -0.0551 | 0.6871 |       0.6831 |   1      |
| no_task   | implicit early - explicit early |  54 |  0.0926 |  -0.0773 |    0.2625 |  0.1487 | 0.2793 |       0.2752 |   1      |
| prev_only | early ads pooled - no ad        |  54 | -0.1389 |  -0.3032 |    0.0254 | -0.2307 | 0.0959 |       0.1573 |   0.3835 |
| prev_only | implicit early - no ad          |  54 | -0.1296 |  -0.3211 |    0.0619 | -0.1847 | 0.1803 |       0.1779 |   0.3835 |
| prev_only | explicit early - no ad          |  54 | -0.1481 |  -0.3349 |    0.0386 | -0.2165 | 0.1176 |       0.1167 |   0.3835 |
| prev_only | implicit early - explicit early |  54 |  0.0185 |  -0.1689 |    0.2059 |  0.027  | 0.8436 |       0.8415 |   0.8436 |
| task_only | early ads pooled - no ad        |  54 | -0.0185 |  -0.137  |    0.0999 | -0.0427 | 0.7551 |       0.5852 |   1      |
| task_only | implicit early - no ad          |  54 | -0.0556 |  -0.2    |    0.0888 | -0.105  | 0.4437 |       0.4386 |   1      |
| task_only | explicit early - no ad          |  54 |  0.0185 |  -0.1166 |    0.1536 |  0.0374 | 0.7844 |       0.7815 |   1      |
| task_only | implicit early - explicit early |  54 | -0.0741 |  -0.2226 |    0.0745 | -0.1361 | 0.3219 |       0.3173 |   1      |
| opening   | early ads pooled - no ad        |  54 | -0.0556 |  -0.2024 |    0.0913 | -0.1033 | 0.4512 |       0.4394 |   1      |
| opening   | implicit early - no ad          |  54 | -0.0185 |  -0.2059 |    0.1689 | -0.027  | 0.8436 |       0.8415 |   1      |
| opening   | explicit early - no ad          |  54 | -0.0926 |  -0.2625 |    0.0773 | -0.1487 | 0.2793 |       0.2752 |   1      |
| opening   | implicit early - explicit early |  54 |  0.0741 |  -0.1303 |    0.2784 |  0.0989 | 0.4704 |       0.4652 |   1      |

## McNemar

| recipe    | contrast                        |   n |   shifted_treatment |   shifted_control |   only_treatment |   only_control |   p_exact |   p_holm |
|:----------|:--------------------------------|----:|--------------------:|------------------:|-----------------:|---------------:|----------:|---------:|
| bare      | implicit early - no ad          |  54 |                  47 |                42 |               11 |              6 |    0.3323 |   0.9969 |
| bare      | explicit early - no ad          |  54 |                  42 |                42 |                8 |              8 |    1      |   1      |
| bare      | implicit early - explicit early |  54 |                  47 |                42 |               12 |              7 |    0.3593 |   0.9969 |
| deployed  | implicit early - no ad          |  54 |                   7 |                 8 |                5 |              6 |    1      |   1      |
| deployed  | explicit early - no ad          |  54 |                   7 |                 8 |                7 |              8 |    1      |   1      |
| deployed  | implicit early - explicit early |  54 |                   7 |                 7 |                6 |              6 |    1      |   1      |
| no_task   | implicit early - no ad          |  54 |                  18 |                15 |               11 |              8 |    0.6476 |   1      |
| no_task   | explicit early - no ad          |  54 |                  13 |                15 |               11 |             13 |    0.8388 |   1      |
| no_task   | implicit early - explicit early |  54 |                  18 |                13 |               13 |              8 |    0.3833 |   1      |
| prev_only | implicit early - no ad          |  54 |                  33 |                40 |               10 |             17 |    0.2478 |   0.5059 |
| prev_only | explicit early - no ad          |  54 |                  32 |                40 |                9 |             17 |    0.1686 |   0.5059 |
| prev_only | implicit early - explicit early |  54 |                  33 |                32 |               13 |             12 |    1      |   1      |
| task_only | implicit early - no ad          |  54 |                   6 |                 9 |                6 |              9 |    0.6072 |   1      |
| task_only | explicit early - no ad          |  54 |                  10 |                 9 |                7 |              6 |    1      |   1      |
| task_only | implicit early - explicit early |  54 |                   6 |                10 |                6 |             10 |    0.4545 |   1      |
| opening   | implicit early - no ad          |  54 |                  25 |                26 |               12 |             13 |    1      |   1      |
| opening   | explicit early - no ad          |  54 |                  21 |                26 |                8 |             13 |    0.3833 |   1      |
| opening   | implicit early - explicit early |  54 |                  25 |                21 |               17 |             13 |    0.5847 |   1      |
