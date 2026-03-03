# Bolt's Journal

## 2024-03-03 - O(N*M) Dataframe filtering is slow
**Learning:** Filtering a large DataFrame repeatedly inside a nested loop `df[df['market'] == m]` for `M` markets and `W` lookbacks means `O(N * M * W)` string comparisons. Pandas `groupby` reduces this to `O(N)` plus direct dictionary lookups.
**Action:** Use `df.groupby('key')` before looping over keys instead of filtering inside the loop, especially when combining with `ThreadPoolExecutor`.
