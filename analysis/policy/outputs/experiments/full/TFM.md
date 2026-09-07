# Transformer fusion (5-fold person)

| model | Spearman | same-t | pair | AUROC |
|---|---:|---:|---:|---:|
| tfm_qwen06_lora_turn_m0.2 | 0.0603 | 0.5 | 0.5648 | 0.4781 |
| tfm_minilm_turn_m0.2 | 0.0305 | 0.4352 | 0.5617 | 0.5148 |
| tfm_distil_mnli_turn_m0.2 | 0.0304 | 0.5463 | 0.5741 | 0.4948 |
| tfm_qwen06_lora_turn_m0.35 | 0.025 | 0.5 | 0.571 | 0.4689 |
| tfm_qwen06_lora_turn_m0.5 | 0.0108 | 0.5 | 0.5586 | 0.4663 |
| tfm_distil_mnli_turn_m0.35 | -0.0108 | 0.5463 | 0.5432 | 0.4806 |
| tfm_minilm_turn_m0.35 | -0.0211 | 0.4352 | 0.5432 | 0.4996 |
| tfm_distil_mnli_turn_m0.5 | -0.0232 | 0.5463 | 0.5556 | 0.4793 |
| tfm_qwen06_lora_raw | -0.0313 | 0.5 | 0.5278 | 0.4576 |
| tfm_distil_mnli_turn_m1.0 | -0.0392 | 0.5463 | 0.5556 | 0.4775 |
| tfm_minilm_turn_m0.5 | -0.0428 | 0.4352 | 0.5401 | 0.4938 |
| tfm_distil_mnli_raw | -0.0593 | 0.5463 | 0.534 | 0.4726 |
| tfm_distil_mnli_raw | -0.0593 | 0.5463 | 0.534 | 0.4726 |
| tfm_distil_mnli_raw | -0.0593 | 0.5463 | 0.534 | 0.4726 |
| tfm_distil_mnli_raw | -0.0593 | 0.5463 | 0.534 | 0.4726 |
| tfm_minilm_turn_m1.0 | -0.0646 | 0.4352 | 0.5216 | 0.4886 |
| tfm_minilm_raw | -0.0923 | 0.4352 | 0.5 | 0.4808 |
| tfm_minilm_raw | -0.0923 | 0.4352 | 0.5 | 0.4808 |
| tfm_minilm_raw | -0.0923 | 0.4352 | 0.5 | 0.4808 |
| tfm_minilm_raw | -0.0923 | 0.4352 | 0.5 | 0.4808 |
