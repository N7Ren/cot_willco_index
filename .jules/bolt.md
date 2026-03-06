## 2024-03-06 - DataFrame Grouping and Dict Appending
**Learning:** To prevent performance bottlenecks when processing large datasets with Pandas, pre-group data using `.groupby()`, compute intermediate results into standard Python dictionaries inside loops, and convert to a pandas DataFrame only at the end. Avoid repeatedly filtering DataFrames or appending to fragmented DataFrames.
**Action:** Always use .groupby() before loops instead of filtering DataFrames sequentially inside loops, and accumulate results in dictionaries before finally converting to a DataFrame.
