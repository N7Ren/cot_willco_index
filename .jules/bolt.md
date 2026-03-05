## 2024-03-24 - Pandas DataFrame Filtering Bottleneck
**Learning:** Repeatedly filtering a large Pandas DataFrame inside a loop is highly inefficient.
**Action:** Pre-group the data using `df.groupby()` before the loop, and retrieve groups using `get_group()`. This significantly improves performance when extracting subsets of data repeatedly. Also, avoid constructing DataFrames in a loop by collecting dictionaries and creating a single DataFrame at the end.
