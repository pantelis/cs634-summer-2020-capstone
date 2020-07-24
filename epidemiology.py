from mobility import fetch_total_population_df
import pandas as pd
import numpy as np

population_df = fetch_total_population_df()
quantiles = population_df.quantile(0.95,axis=1)
foo_df = population_df.copy()

#population_df.quantile(0.95,axis=1) - Medium lockdown
#population_df.quantile(0.8,axis=1) - Strict lockdown
for i in range(24):
    foo_df.loc[i] = foo_df.loc[i].apply(lambda x: 'safe' if x < quantiles[i] else 'unsafe')

#row_df['frequency'] = row_df.apply(lambda row: sum(row[0:1010] == 'unsafe'), axis=1)

print(foo_df)