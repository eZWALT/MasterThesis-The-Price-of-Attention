# After-reply Path B heatmaps

Parallel sensitivity. **Not** the confirmatory lock.

```bash
python analysis/eeg/preprocessing/run_after_reply_path_b.py
python analysis/eeg/analysis/plot_after_reply_heatmaps.py
```

Lock: `assistant_reply` + 0.494 s (frozen explicit banner lag), for
implicit, explicit, and matched no-ad.

Golden visual-onset Gold is untouched. These files live only under
`sensitivity/after_reply/` and this folder.

| File | What |
|---|---|
| `board_path_b_golden_vs_after_reply` | Top = golden Path B; bottom = this lock |
| `board_path_b_2_4_8s` | After-reply Path B only |
| `path_b_2s` / `path_b_4s` / `path_b_8s` | Singles |
| `board_path_a_golden_path_b_after_reply` | Unchanged Path A + this Path B |
