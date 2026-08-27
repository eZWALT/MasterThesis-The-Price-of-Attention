# After-reply Dataset B heatmaps

Parallel sensitivity. **Not** the confirmatory lock.

```bash
python analysis/eeg/preprocessing/run_after_reply_dataset_b.py
python analysis/eeg/analysis/plot_after_reply_heatmaps.py
```

Lock: `assistant_reply` + 0.494 s (frozen explicit banner lag), for
implicit, explicit, and matched no-ad.

Golden visual-onset Gold is untouched. These files live only under
`sensitivity/after_reply/` and this folder.

| File | What |
|---|---|
| `board_dataset_b_golden_vs_after_reply` | Top = golden Dataset B; bottom = this lock |
| `board_dataset_b_2_4_8s` | After-reply Dataset B only |
| `dataset_b_2s` / `dataset_b_4s` / `dataset_b_8s` | Singles |
| `board_dataset_a_golden_dataset_b_after_reply` | Unchanged Dataset A + this Dataset B |
